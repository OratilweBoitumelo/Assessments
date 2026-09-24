from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class DashboardPage(BasePage):
    HEADER = (By.XPATH, "//h6[normalize-space()='Dashboard']")
    PIM_MENU = (
        By.XPATH,
        "//a[contains(@class,'oxd-main-menu-item')][.//span[normalize-space()='PIM']]",
    )

    def is_loaded(self) -> bool:
        return self.is_visible(self.HEADER) and "/dashboard" in self.driver.current_url

    def open_pim(self):
        self.click(self.PIM_MENU)
