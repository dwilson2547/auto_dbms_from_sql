Feature: AutoDBMS Full Pipeline
  As a developer
  I want to generate a DBMS project from a SQL schema
  So I can have a working CRUD API and UI

  Scenario: Generate project files from a 4-table schema
    Given the sample schema with 4 tables
    When I generate a project from the sample schema
    Then a models.py file is created
    And a blueprint file is created for each of the 4 tables
    And a service file is created for each of the 4 tables
    And a form file is created for each of the 4 tables
    And an app.py file is created

  Scenario: Generated API returns entity list
    Given the sample schema with 4 tables
    And a running PostgreSQL test database
    When I generate a project from the sample schema
    And the generated Flask API is running
    Then GET /api/get_all returns 4 entities
    And the entity list includes "Customers"
    And the entity list includes "Products"
    And the entity list includes "Orders"
    And the entity list includes "OrderItems"

  Scenario: Generated API supports adding and retrieving records
    Given the sample schema with 4 tables
    And a running PostgreSQL test database
    When I generate a project from the sample schema
    And the generated Flask API is running
    And I POST a customer with name "Alice" and email "alice@example.com"
    Then GET /api/customers/get_all returns a record with name "Alice"

  Scenario: Generated API supports deleting records
    Given the sample schema with 4 tables
    And a running PostgreSQL test database
    When I generate a project from the sample schema
    And the generated Flask API is running
    And I POST a customer with name "ToDelete" and email "todelete@example.com"
    Then the customer can be deleted by its returned id
    And GET /api/customers/get_all does not contain name "ToDelete"
