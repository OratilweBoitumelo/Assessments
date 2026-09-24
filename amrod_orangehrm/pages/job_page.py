from selenium.webdriver.common.by import By
from employee_data import Employee
from pages.base_page import BasePage


class JobPage(BasePage):
    TAB = (By.XPATH, "//a[contains(@class,'orangehrm-tabs-item')][normalize-space()='Job']")
    JOINED_DATE_LABEL = (By.XPATH, "//label[normalize-space()='Joined Date']")
    SAVE = (By.XPATH, "//form[.//label[normalize-space()='Joined Date']]//button[@type='submit']")

    def open(self):
        self.click(self.TAB)
        self.visible(self.JOINED_DATE_LABEL)
        self.wait_for_loader()

    def fill(self, emp: Employee) -> str:
        """Fill the job form. Returns the location that was selected."""
        self.fill_date("Joined Date", emp.joined_date)
        self.select_dropdown("Job Title", emp.job_title)
        self.select_dropdown("Job Category", emp.job_category)
        self.select_dropdown("Sub Unit", emp.sub_unit)
        location = self.select_dropdown("Location", emp.location)
        self.select_dropdown("Employment Status", emp.employment_status)
        return location

    def save(self):
        self.click(self.SAVE)
