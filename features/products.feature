Feature: Products service browser smoke test
    As a developer
    I want to check that the Products service is reachable in a browser
    So that the Behave and Selenium setup can be verified

Background:
    Given the following products
        | name       | description | category | price | stock |
        | Blue Shirt | Cotton tee  | Clothing | 19.99 | 10    |
        | Coffee Mug | Ceramic mug | Kitchen  | 12.50 | 25    |

Scenario: The service root is reachable
    When I visit the "Home Page"
    Then I should see "Products Service" on the page
