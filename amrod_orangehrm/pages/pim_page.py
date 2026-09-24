"""Add Employee form and Employee List search."""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage, field_xpath
import config

def _top_tab(name: str):
    return (
        By.XPATH,
        f"//a[contains(@class,'oxd-topbar-body-nav-tab-item')][normalize-space()='{name}']",
    )

class PimPage(BasePage):
    EMPLOYEE_LIST_TAB = (By.XPATH, "//a[normalize-space()='Employee List']")
    EMPLOYEE_LIST_URL = f"{config.BASE_URL}/web/index.php/pim/viewEmployeeList"

    def is_loaded(self) -> bool:
        return "/pim/" in self.driver.current_url and self.is_visible(_top_tab("Employee List"))

    def go_to_add_employee(self):
        self.click(_top_tab("Add Employee"))

    def go_to_employee_list(self):
        try:
            self.click(self.EMPLOYEE_LIST_TAB, timeout=8)
        except AssertionError:
            self.log.warning(
                "'Employee List' tab not clickable on %s - opening the list by URL",
                self.driver.current_url,
            )
            self.driver.get(self.EMPLOYEE_LIST_URL)

class AddEmployeePage(BasePage):
    FIRST_NAME = (By.NAME, "firstName")
    MIDDLE_NAME = (By.NAME, "middleName")
    LAST_NAME = (By.NAME, "lastName")
    EMPLOYEE_ID = field_xpath("Employee Id", "input")
    SAVE = (By.CSS_SELECTOR, "button[type='submit']")

    def is_loaded(self) -> bool:
        return "addEmployee" in self.driver.current_url and self.is_visible(self.FIRST_NAME)

    def fill_name(self, first: str, middle: str, last: str):
        if first:
            self.type(self.FIRST_NAME, first)
        if middle:
            self.type(self.MIDDLE_NAME, middle)
        if last:
            self.type(self.LAST_NAME, last)

    def get_employee_id(self) -> str:
        """The ID is generated asynchronously, so wait until the field is populated."""
        element = self.visible(self.EMPLOYEE_ID)
        self._wait(lambda d: element.get_attribute("value"), "employee ID to be generated")
        self.log.info("Generated employee ID: %s", element.get_attribute("value"))
        return element.get_attribute("value")

    def save(self):
        self.click(self.SAVE)


class EmployeeListPage(BasePage):
    SEARCH_ID = field_xpath("Employee Id", "input")
    SEARCH_BUTTON = (By.XPATH, "//button[normalize-space()='Search']")
    NO_RECORDS = (By.XPATH, "//*[normalize-space()='No Records Found']")

    @staticmethod
    def _row(employee_id: str):
        return (
            By.XPATH,
            "//div[contains(@class,'oxd-table-body')]//div[@role='row']"
            f"[.//div[@role='cell'][normalize-space()='{employee_id}']]",
        )

    def is_loaded(self) -> bool:
        return self.is_visible(self.SEARCH_ID)

    def search_by_id(self, employee_id: str):
        self.type(self.SEARCH_ID, employee_id)
        self.click(self.SEARCH_BUTTON)

    def get_row_text(self, employee_id: str) -> str:
        text = self.visible(self._row(employee_id)).text
        self.log.info("Employee list row for ID %s: %r", employee_id, text)
        return text

    def has_no_records(self) -> bool:
        return self.is_visible(self.NO_RECORDS)
