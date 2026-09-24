@e2e
Feature: End-to-end employee management
  As an HR admin
  I want to add an employee and complete their details
  So that the record is correct in the Employee List

  Scenario: Add a new employee, update personal and job details, then find them in the Employee List
    Given I open the OrangeHRM login page
    Then the login page is displayed
    When I log in with the configured credentials
    Then the Dashboard is displayed as the landing page
    When I open the PIM module
    Then the PIM page is displayed
    When I click Add Employee
    Then the Add Employee page is displayed
    When I enter the new employee's first, middle and last name
    And I save the new employee
    Then a success notification is shown
    When I fill in the personal details
    And I save the personal details
    Then a success notification is shown
    When I attach a file in the Attachments section
    Then a success notification is shown
    And the attachment appears in the attachments table
    When I open the Job tab
    And I fill in the job details
    And I save the job details
    Then a success notification is shown
    When I go to the Employee List
    Then the Employee Information page is displayed
    When I search for the new employee by ID
    Then the employee record is displayed with the correct details
    When I capture a full-page screenshot of the search page
    Then the screenshot is saved
