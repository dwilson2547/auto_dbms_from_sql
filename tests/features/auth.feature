Feature: Authentication
  As a user of the generated DBMS
  I want to log in and log out using default credentials
  So I can securely access the application

  Background:
    Given the sample schema with 4 tables
    And a running PostgreSQL test database
    And the generated Flask API is running
    And the Angular UI is running

  Scenario: Login with default credentials
    When I navigate to the home page
    And I click the "Login" button
    And I enter username "admin" and password "admin"
    And I click "Sign In"
    Then I should see "Logged in"
    And the "Login" button should not be visible

  Scenario: Login with invalid credentials is rejected
    When I navigate to the home page
    And I click the "Login" button
    And I enter username "admin" and password "wrongpassword"
    And I click "Sign In"
    Then I should see "Invalid credentials"
    And the "Login" button should still be visible

  Scenario: Logout after successful login
    Given I am logged in with username "admin" and password "admin"
    When I click the "Logout" button
    Then I should see the "Login" button
    And I should not see "Logged in"
