from selenium.webdriver.common.by import By
import config
from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.NAME, "username")
    PASSWORD = (By.NAME, "password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR = (By.CSS_SELECTOR, ".oxd-alert-content-text")

    def open(self):
        self.driver.get(config.BASE_URL)

    def is_displayed(self) -> bool:
        return self.is_visible(self.USERNAME) and self.is_visible(self.PASSWORD)

    def login(self, username: str, password: str):
        if username:
            self.type(self.USERNAME, username)
        if password:
            self.type(self.PASSWORD, password, sensitive=True)
        self.click(self.SUBMIT)

    def get_error(self) -> str:
        return self.text_of(self.ERROR)
