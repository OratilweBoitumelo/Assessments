@negative
Feature: Error handling
  The application should show clear errors and handle invalid data gracefully

  Scenario: Login with invalid credentials
    Given I open the OrangeHRM login page
    When I log in with username "Admin" and password "wrong-password"
    Then the error message "Invalid credentials" is displayed
    And I am not taken to the Dashboard

  Scenario: Login with empty fields
    Given I open the OrangeHRM login page
    When I submit the login form without entering credentials
    Then "Required" errors are displayed for username and password

  Scenario: Add employee without the required names
    Given I am logged in as the admin user
    When I open the PIM module
    And I click Add Employee
    And I save the new employee
    Then a "Required" validation error is displayed
    And I am still on the Add Employee page

  Scenario: Search for an employee that does not exist
    Given I am logged in as the admin user
    When I open the PIM module
    And I search for employee ID "99999999"
    Then no records are found
