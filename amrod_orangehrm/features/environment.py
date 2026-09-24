"""behave hooks: logging, browser setup/teardown, page objects, failure diagnostics."""
import re
import shutil
import tempfile
from pathlib import Path

from allure_commons._allure import attach
from allure_commons.types import AttachmentType
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import config
from employee_data import new_employee
from logger import get_logger, log_position, read_log_since, setup_logging
from pages.base_page import BasePage
from pages.dashboard_page import DashboardPage
from pages.job_page import JobPage
from pages.login_page import LoginPage
from pages.personal_details_page import PersonalDetailsPage
from pages.pim_page import AddEmployeePage, EmployeeListPage, PimPage

log = get_logger("hooks")


def before_all(context):
    """Start every run with an empty reports folder so Allure only shows this run."""
    config.REPORTS_DIR.mkdir(exist_ok=True)
    for item in config.REPORTS_DIR.iterdir():
        if item.name == ".gitkeep":
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()

    setup_logging(config.LOG_LEVEL)  # after the clean-up, so the log file survives
    log.info("Test run started | base_url=%s | headless=%s | timeout=%ss",
             config.BASE_URL, config.HEADLESS, config.TIMEOUT)


def before_scenario(context, scenario):
    context.log_start = log_position()
    context.step_no = 0
    log.info("SCENARIO START: %s", scenario.name)

    options = Options()
    if config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    context.driver = webdriver.Chrome(options=options)  # Selenium Manager fetches the driver

    driver = context.driver
    context.base = BasePage(driver)
    context.login = LoginPage(driver)
    context.dashboard = DashboardPage(driver)
    context.pim = PimPage(driver)
    context.add_page = AddEmployeePage(driver)
    context.personal = PersonalDetailsPage(driver)
    context.job = JobPage(driver)
    context.employee_list = EmployeeListPage(driver)

    context.emp = new_employee()      # unique employee for this scenario
    context.employee_id = None
    context.screenshot_path = None

    # throw-away attachment, contains no real information
    context.tmp_dir = Path(tempfile.mkdtemp())
    context.sample_file = context.tmp_dir / "qa_assessment_dump.txt"
    context.sample_file.write_text("Dummy attachment for QA assessment. No real data.")


def before_step(context, step):
    log.info("STEP: %s %s", step.keyword, step.name)


def after_step(context, step):
    status = getattr(step.status, "name", str(step.status))
    if status not in ("passed", "failed"):
        return  # skipped/undefined steps: nothing happened in the browser

    context.step_no += 1
    if status == "passed":
        log.info("STEP PASSED (%.2fs): %s %s", step.duration, step.keyword, step.name)
    else:
        log.error("STEP FAILED (%.2fs): %s %s", step.duration, step.keyword, step.name)
        log.error("Error: %s", getattr(step, "error_message", None) or "no message")
        _log_page_state(context)

    # screenshot after every step, attached to that step in the Allure report
    try:
        scenario_slug = re.sub(r"\W+", "_", context.scenario.name)[:40]
        step_slug = re.sub(r"\W+", "_", f"{step.keyword} {step.name}")[:50]
        context.base.take_screenshot(
            f"{scenario_slug}_{context.step_no:02d}_{status}_{step_slug}",
            title=f"Step {context.step_no} {status.upper()}: {step.keyword} {step.name}",
        )
    except Exception as error:  # a screenshot problem must never fail the test
        log.warning("Could not take screenshot after step: %s", error)

    if status == "failed":
        attach(read_log_since(context.log_start), name="Execution log",
               attachment_type=AttachmentType.TEXT)


def after_scenario(context, scenario):
    log.info("SCENARIO END: %s | %s", scenario.name, getattr(scenario.status, "name", scenario.status))
    context.driver.quit()
    shutil.rmtree(context.tmp_dir, ignore_errors=True)


def after_all(context):
    log.info("Test run finished")


def _log_page_state(context):
    """Record what the user would see on screen when a step fails."""
    try:
        driver = context.driver
        log.error("Page state | url=%s | title=%s", driver.current_url, driver.title)
        for css, label in (
            (".oxd-input-field-error-message", "field validation errors"),
            (".oxd-toast", "notification"),
            (".oxd-alert-content-text", "alert"),
        ):
            texts = [e.text.strip() for e in driver.find_elements(By.CSS_SELECTOR, css) if e.text.strip()]
            if texts:
                log.error("Visible %s: %s", label, texts)
    except Exception as error:  # diagnostics must never hide the real failure
        log.warning("Could not read page state: %s", error)
