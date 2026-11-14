Feature: Products service browser smoke test
    As a developer
    I want to check that the Products service is reachable in a browser
    So that the Behave and Selenium setup can be verified

Background:
    Given the following products
        | name       | description | category | price | stock |
        | Blue Shirt | Cotton tee  | Clothing | 19.99 | 10    |
        | Coffee Mug | Ceramic mug | Kitchen  | 12.50 | 25    |

Scenario: The Product Admin home page is reachable
    When I visit the "Home Page"
    Then I should see "Product Admin" on the page


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
