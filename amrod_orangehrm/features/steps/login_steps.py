from behave import given, then, when
import config


@given("I open the OrangeHRM login page")
def step_open_login(context):
    context.login.open()

@given("I am logged in as the admin user")
def step_logged_in(context):
    context.login.open()
    context.login.login(config.USERNAME, config.PASSWORD)
    assert context.dashboard.is_loaded(), "Login did not reach the Dashboard"

@then("the login page is displayed")
def step_login_displayed(context):
    assert context.login.is_displayed(), "Login page was not displayed"

@when("I log in with the configured credentials")
def step_login_configured(context):
    context.login.login(config.USERNAME, config.PASSWORD)

@when('I log in with username "{username}" and password "{password}"')
def step_login_custom(context, username, password):
    context.login.login(username, password)

@when("I submit the login form without entering credentials")
def step_login_empty(context):
    context.login.login("", "")

@then("the Dashboard is displayed as the landing page")
def step_dashboard_displayed(context):
    assert context.dashboard.is_loaded(), "Dashboard is not the default landing page"

@then('the error message "{message}" is displayed')
def step_login_error(context, message):
    assert context.login.get_error() == message

@then("I am not taken to the Dashboard")
def step_not_dashboard(context):
    assert "/dashboard" not in context.driver.current_url

@then('"{message}" errors are displayed for username and password')
def step_login_required(context, message):
    assert context.login.get_field_errors() == [message, message]
