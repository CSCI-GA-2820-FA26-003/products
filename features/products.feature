Feature: Products service browser smoke test
    As a developer
    I want to check that the Products service is reachable in a browser
    So that the Behave and Selenium setup can be verified

Background:
    Given the following products
        | name       | description | category | price | stock |
        | Blue Shirt | Cotton tee  | Clothing | 19.99 | 10    |
        | Coffee Mug | Ceramic mug | Kitchen  | 12.50 | 25    |
        | Apple      | Fresh apple | Fruit    | 1.25  | 30    |
        | Apple      | Apple phone | Electronics | 999.00 | 4 |
        | Banana     | Fresh banana | Fruit   | 0.75  | 20    |

Scenario: The Product Admin home page is reachable
    When I visit the "Home Page"
    Then I should see "Product Admin" on the page

Scenario: Retrieve a product from the Admin UI
  When I visit the "Home Page"
  And I set the "Product ID" to "Blue Shirt"
  And I press the "Retrieve" button
  Then I should see "Blue Shirt" in the "Name" field

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "Red Hat"
    And I set the "Description" to "Wool hat"
    And I set the "Category" to "Clothing"
    And I set the "Price" to "15.00"
    And I set the "Stock" to "5"
    And I set the "Image URL" to "https://example.com/hat.png"
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: Restock a product
    Given I have created "Apple" with stock "10" on the admin page
    When I set the "Quantity" to "5"
    And I press the "Restock" button
    Then the "Stock" field should show "15"

Scenario: Buy a product
    Given I have created "Apple" with stock "10" on the admin page
    When I set the "Quantity" to "3"
    And I press the "Buy" button
    Then the "Stock" field should show "7"
Scenario: List all products
    When I visit the "Home Page"
    And I press the "List Products" button
    Then I should see "Blue Shirt" in the results table
    And I should see "Coffee Mug" in the results table

Scenario: Query products by name
    When I visit the "Home Page"
    And I set the "Name" to "Apple"
    And I press the "Search" button
    Then I should see only products with the name "Apple"

Scenario: Query products by multiple attributes
    When I visit the "Home Page"
    And I set the "Name" to "Apple"
    And I set the "Category" to "Fruit"
    And I press the "Search" button
    Then I should see only products matching both criteria

Scenario: Query products by price
    When I visit the "Home Page"
    And I set the "Price" to "1.25"
    And I press the "Search" button
    Then I should see only products with the price "1.25"


Scenario: Update a Product
    Given I have created "Blue Hat" with stock "5" on the admin page
    When I set the "Name" to "Green Shirt"
    And I press the "Update" button
    Then I should see the message "Success"
    And the "Name" field should show "Green Shirt"
    When I press the "List Products" button
    Then I should see "Green Shirt" in the results table

Scenario: Delete a Product and confirm
    Given I have retrieved the product "Blue Shirt" on the admin page
    When I click the "Delete" button and I confirm the deletion
    Then I should see the message "Success"
    And retrieving product "Blue Shirt" should show a not-found message

Scenario: Delete a Product and cancel
    Given I have retrieved the product "Blue Shirt" on the admin page
    When I click the "Delete" button and I cancel the deletion
    Then retrieving product "Blue Shirt" should still show "Blue Shirt"
