"""Selenium steps for checking the Products service in a browser."""
from selenium.webdriver.support.ui import WebDriverWait
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By


@when('I visit the "Home Page"')
def step_visit_home_page(context):
    """Open the Products service root URL."""
    context.driver.get(context.base_url)


@then('I should see "{text_string}" on the page')
def step_text_is_present(context, text_string):
    """Check that the expected text appears in the page body."""
    body = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string in body.text

@when('I set the "Product ID" to "{product_id}"')
def step_set_product_id(context, product_id):
    if product_id == "1":
        product_id = str(context.blue_shirt_id)

    element = context.driver.find_element(By.ID, "product_id")
    element.clear()
    element.send_keys(product_id)


@when('I press the "Retrieve" button')
def step_press_retrieve(context):
    button = context.driver.find_element(By.ID, "retrieve-btn")
    button.click()


@then('I should see "{product_name}" in the "Name" field')
def step_check_product_name(context, product_name):
    WebDriverWait(context.driver, 10).until(
        lambda driver: driver.find_element(
            By.ID, "product_name"
        ).get_attribute("value") == product_name
    )
