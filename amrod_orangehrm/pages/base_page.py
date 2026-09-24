"""contains reusable methods for all pages"""
import base64
import sys
from datetime import date, datetime
from allure_commons._allure import attach
from allure_commons.types import AttachmentType
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import config
from logger import get_logger

SELECT_ALL = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL


def field_xpath(label: str, tag: str) -> tuple:
    """Locate an OrangeHRM form control through its visible label text."""
    return (
        By.XPATH,
        f"//label[normalize-space()='{label}']/parent::div/following-sibling::div//{tag}",
    )


class BasePage:
    LOADER = (By.CSS_SELECTOR, ".oxd-form-loader, .oxd-loading-spinner")
    ANY_TOAST = (By.CSS_SELECTOR, ".oxd-toast")
    SUCCESS_TOAST = (By.CSS_SELECTOR, ".oxd-toast--success")
    FIELD_ERRORS = (By.CSS_SELECTOR, ".oxd-input-field-error-message")

    def __init__(self, driver):
        self.driver = driver
        self.log = get_logger(type(self).__name__)

    # ---------- waiting / error handling ----------
    def _wait(self, condition, what: str, timeout: int | None = None):
        """Wait for a condition; raise a readable AssertionError on timeout."""
        try:
            return WebDriverWait(
                self.driver,
                timeout or config.TIMEOUT,
                ignored_exceptions=(StaleElementReferenceException,),
            ).until(condition)
        except TimeoutException:
            message = f"Timed out waiting for {what} (url: {self.driver.current_url})"
            self.log.error(message)
            raise AssertionError(message) from None

    def visible(self, locator):
        return self._wait(EC.visibility_of_element_located(locator), f"{locator} to be visible")

    def is_visible(self, locator, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_for_loader(self):
        self._wait(EC.invisibility_of_element_located(self.LOADER), "loading spinner to disappear")

    # ---------- actions ----------
    def click(self, locator, timeout: int | None = None):
        self.log.info("Click %s", locator)
        self.wait_for_loader()
        element = self._wait(EC.element_to_be_clickable(locator), f"{locator} to be clickable", timeout)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.log.warning("Click intercepted for %s - retrying with JavaScript click", locator)
            self.wait_for_loader()
            self.driver.execute_script("arguments[0].click();", element)

    def type(self, locator, text: str, sensitive: bool = False):
        self.log.info("Type '%s' into %s", "****" if sensitive else text, locator)
        self.wait_for_loader()
        element = self.visible(locator)
        element.click()
        # .clear() does not always notify OrangeHRM's Vue forms, so select-all + delete
        element.send_keys(SELECT_ALL, "a", Keys.BACKSPACE)
        element.send_keys(text)
        return element

    def text_of(self, locator) -> str:
        return self.visible(locator).text.strip()

    def select_dropdown(self, label: str, option: str | None = None) -> str:
        """Open an OrangeHRM dropdown and pick `option` (or the first real option if None)."""
        self.log.info("Select '%s' in dropdown '%s'", option or "<first available>", label)
        self.click(field_xpath(label, "div[contains(@class,'oxd-select-text')]"))
        options_locator = (By.XPATH, "//div[@role='listbox']//div[@role='option']")
        self._wait(EC.visibility_of_element_located(options_locator), f"options of '{label}'")
        options = self.driver.find_elements(*options_locator)
        texts = [o.text.strip() for o in options]
        self.log.debug("Options for '%s': %s", label, texts)

        if option is None:
            index = next(i for i, t in enumerate(texts) if t and not t.startswith("--"))
        else:
            matches = [i for i, t in enumerate(texts) if t.lower() == option.lower()]
            if not matches:
                message = f"Option '{option}' not found for '{label}'. Available: {texts}"
                self.log.error(message)
                raise AssertionError(message)
            index = matches[0]
        options[index].click()
        self.log.info("Selected '%s' for '%s'", texts[index], label)
        return texts[index]

    def fill_date(self, label: str, value: date):
        """Type a date using whatever format the field advertises (e.g. yyyy-dd-mm)."""
        locator = field_xpath(label, "input")
        element = self.visible(locator)
        placeholder = (element.get_attribute("placeholder") or "yyyy-mm-dd").lower()
        py_format = placeholder.replace("yyyy", "%Y").replace("mm", "%m").replace("dd", "%d")
        self.log.info("Fill date '%s' = %s (field format: %s)", label, value, placeholder)
        self.type(locator, value.strftime(py_format))
        element.send_keys(Keys.TAB)  # close the calendar popup

    # ---------- notifications / validation ----------
    def wait_for_success_toast(self) -> str:
        text = self._wait(
            lambda d: d.find_element(*self.SUCCESS_TOAST).text.strip(), "success notification"
        )
        self.log.info("Notification shown: %r", text)
        # wait for it to close so the next save can't be confused with this one
        self._wait(EC.invisibility_of_element_located(self.ANY_TOAST), "notification to close")
        return text

    def get_field_errors(self) -> list[str]:
        self.visible(self.FIELD_ERRORS)
        errors = [e.text.strip() for e in self.driver.find_elements(*self.FIELD_ERRORS)]
        self.log.info("Validation errors shown: %s", errors)
        return errors

    # ---------- screenshots ----------
    def take_screenshot(self, name: str, title: str | None = None):
        config.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        path = config.SCREENSHOT_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_{name}.png"
        try:  # full-page capture through Chrome DevTools
            metrics = self.driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
            size = metrics.get("cssContentSize") or metrics["contentSize"]
            data = self.driver.execute_cdp_cmd(
                "Page.captureScreenshot",
                {
                    "format": "png",
                    "captureBeyondViewport": True,
                    "clip": {"x": 0, "y": 0, "width": size["width"], "height": size["height"], "scale": 1},
                },
            )
            path.write_bytes(base64.b64decode(data["data"]))
        except Exception:  # fall back to a normal viewport screenshot
            self.driver.save_screenshot(str(path))
        self.log.info("Screenshot saved: %s", path)
        attach.file(str(path), name=title or name, attachment_type=AttachmentType.PNG)
        return path
