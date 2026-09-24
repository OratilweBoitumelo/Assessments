from datetime import date
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class PersonalDetailsPage(BasePage):
    FIRST_NAME = (By.NAME, "firstName")
    SAVE = (By.XPATH, "//form[.//input[@name='firstName']]//button[@type='submit']")
    ADD_ATTACHMENT = (
        By.XPATH,
        "//h6[normalize-space()='Attachments']/..//button[normalize-space()='Add']",
    )
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
    ATTACHMENT_SAVE = (By.XPATH, "//form[.//input[@type='file']]//button[@type='submit']")

    def wait_until_loaded(self):
        """Page fills in its data asynchronously; wait until the name is populated."""
        element = self.visible(self.FIRST_NAME)
        self._wait(lambda d: element.get_attribute("value"), "personal details to load")
        self.wait_for_loader()

    def fill_details(self, nationality: str, marital_status: str, dob: date, gender: str):
        self.select_dropdown("Nationality", nationality)
        self.select_dropdown("Marital Status", marital_status)
        self.fill_date("Date of Birth", dob)
        # radio inputs are visually hidden, so click their label
        self.click((By.XPATH, f"//label[normalize-space(.)='{gender}']"))

    def save(self):
        self.click(self.SAVE)

    def add_attachment(self, file_path: str):
        self.click(self.ADD_ATTACHMENT)
        self._wait(
            lambda d: d.find_element(*self.FILE_INPUT), "file input", timeout=10
        ).send_keys(file_path)
        self.click(self.ATTACHMENT_SAVE)

    def attachment_listed(self, file_name: str) -> bool:
        row = (By.XPATH, f"//div[@role='row'][contains(normalize-space(.),'{file_name}')]")
        return self.is_visible(row, timeout=10)
