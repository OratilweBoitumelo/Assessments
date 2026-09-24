from behave import then, when
from logger import get_logger

log = get_logger("steps")


# ---------- navigation ----------
@when("I open the PIM module")
def step_open_pim(context):
    context.dashboard.open_pim()

@then("the PIM page is displayed")
def step_pim_displayed(context):
    assert context.pim.is_loaded(), "PIM page was not displayed"


@when("I click Add Employee")
def step_click_add_employee(context):
    context.pim.go_to_add_employee()

@then("the Add Employee page is displayed")
def step_add_page_displayed(context):
    assert context.add_page.is_loaded(), "Add Employee page was not displayed"

# ---------- add employee ----------
@when("I enter the new employee's first, middle and last name")
def step_enter_name(context):
    emp = context.emp
    context.add_page.fill_name(emp.first_name, emp.middle_name, emp.last_name)
    context.employee_id = context.add_page.get_employee_id()
    log.info("Employee under test: %s %s %s (ID %s)", emp.first_name, emp.middle_name, emp.last_name, context.employee_id)

@when("I save the new employee")
def step_save_employee(context):
    context.add_page.save()


@then("a success notification is shown")
def step_success_toast(context):
    assert "Success" in context.base.wait_for_success_toast()


# ---------- personal details ----------
@when("I fill in the personal details")
def step_fill_personal(context):
    emp = context.emp
    log.info("Personal details: %s, %s, DOB %s, %s", emp.nationality, emp.marital_status, emp.date_of_birth, emp.gender)
    context.personal.wait_until_loaded()
    context.personal.fill_details(emp.nationality, emp.marital_status, emp.date_of_birth, emp.gender)


@when("I save the personal details")
def step_save_personal(context):
    context.personal.save()


@when("I attach a file in the Attachments section")
def step_attach_file(context):
    log.info("Uploading attachment: %s", context.sample_file)
    context.personal.add_attachment(str(context.sample_file))


@then("the attachment appears in the attachments table")
def step_attachment_listed(context):
    assert context.personal.attachment_listed(context.sample_file.name), "Attachment missing from table"


# ---------- job ----------
@when("I open the Job tab")
def step_open_job(context):
    context.job.open()


@when("I fill in the job details")
def step_fill_job(context):
    context.job.fill(context.emp)


@when("I save the job details")
def step_save_job(context):
    context.job.save()


# ---------- employee list ----------
@when("I go to the Employee List")
def step_go_list(context):
    context.pim.go_to_employee_list()


@then("the Employee Information page is displayed")
def step_list_displayed(context):
    assert context.employee_list.is_loaded(), "Employee Information page was not displayed"


@when("I search for the new employee by ID")
def step_search_new(context):
    context.employee_list.search_by_id(context.employee_id)


@then("the employee record is displayed with the correct details")
def step_verify_row(context):
    emp = context.emp
    row = context.employee_list.get_row_text(context.employee_id)
    # The results table has no Location column, so location is not asserted here.
    for expected in (
        f"{emp.first_name} {emp.middle_name}",
        emp.last_name,
        emp.job_title,
        emp.employment_status,
        emp.sub_unit,
    ):
        assert expected.lower() in row.lower(), f"'{expected}' not found in search result row: {row!r}"


@when("I capture a full-page screenshot of the search page")
def step_screenshot(context):
    context.screenshot_path = context.employee_list.take_screenshot("employee_search_result")


@then("the screenshot is saved")
def step_screenshot_saved(context):
    assert context.screenshot_path and context.screenshot_path.exists(), "Screenshot was not saved"


# ---------- negative ----------
@then('a "{message}" validation error is displayed')
def step_validation_error(context, message):
    assert message in context.add_page.get_field_errors()


@then("I am still on the Add Employee page")
def step_still_add_page(context):
    assert "addEmployee" in context.driver.current_url


@when('I search for employee ID "{employee_id}"')
def step_search_id(context, employee_id):
    context.employee_list.search_by_id(employee_id)


@then("no records are found")
def step_no_records(context):
    assert context.employee_list.has_no_records()
