Feature: CRUD Operations via Angular UI
  As a user of the generated DBMS
  I want to perform CRUD operations on entities through the UI
  So I can manage data visually

  Background:
    Given the sample schema with 4 tables
    And a running PostgreSQL test database
    And the generated Flask API is running
    And the Angular UI is running

  Scenario: Entity list page displays all 4 tables
    When I navigate to the home page
    Then I should see the entity list page
    And "Customers" should appear in the entity list
    And "Products" should appear in the entity list
    And "Orders" should appear in the entity list
    And "OrderItems" should appear in the entity list

  Scenario: Navigate to entity detail page
    When I navigate to the home page
    And I click on the "Customers" entity link
    Then I should be on the entity detail page for "Customers"
    And I should see 5 CRUD operation panels

  Scenario: Add a new record via the UI
    When I navigate to the entity detail page for "Customers"
    And I expand the "add" CRUD panel
    And I enter the JSON body '{"name": "Alice", "email": "alice@example.com"}'
    And I click the execute button for "add"
    Then the result for "add" should contain "Alice"

  Scenario: Get all records via the UI
    Given a customer record exists with name "Alice" and email "alice@example.com"
    When I navigate to the entity detail page for "Customers"
    And I expand the "get-all" CRUD panel
    And I click the execute button for "get-all"
    Then the result for "get-all" should contain "Alice"

  Scenario: Delete a record via the UI
    Given a customer record exists with name "Alice" and email "alice@example.com"
    When I navigate to the entity detail page for "Customers"
    And I expand the "add" CRUD panel
    And I enter the JSON body '{"name": "Bob", "email": "bob@example.com"}'
    And I click the execute button for "add"
    And I expand the "delete" CRUD panel
    And I enter the ID "1" for "delete"
    And I click the execute button for "delete"
    Then the result for "delete" should contain "ok"
