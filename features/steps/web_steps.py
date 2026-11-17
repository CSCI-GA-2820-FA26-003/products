"""Selenium steps for checking the Products service in a browser."""
from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions


ID_PREFIX = "product_"


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
        product_id = str(context.product_ids[product_id])
    
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

@when('I set the "{element_name}" to "{text_string}"')
def step_set_field(context, element_name, text_string):
    """Type a value into a form field."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)
    if element.get_attribute("value") != text_string:
        # Fall back to JavaScript when send_keys does not type into the field
        context.driver.execute_script(
            "arguments[0].value = arguments[1];", element, text_string
        )
    assert element.get_attribute("value") == text_string


@when('I press the "{button}" button')
def step_press_button(context, button):
    """Click a button on the page."""
    button_id = button.lower().replace(" ", "_") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see the message "{message}"')
def step_see_message(context, message):
    """Check that the flash message shows the expected text."""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


@given('I have created "{name}" with stock "{stock}" on the admin page')
def step_create_product_for_stock_action(context, name, stock):
    """Create a product through the admin form."""
    step_visit_home_page(context)
    for field, value in (
        ("Name", name),
        ("Description", "Fresh apple"),
        ("Category", "Food"),
        ("Price", "1.00"),
        ("Stock", stock),
    ):
        step_set_field(context, field, value)
    step_press_button(context, "Create")
    step_see_message(context, "Success")


@then('the "{field}" field should show "{value}"')
def step_field_value(context, field, value):
    """Wait for the displayed field to show the expected value."""
    locator = (By.ID, ID_PREFIX + field.lower().replace(" ", "_"))
    WebDriverWait(context.driver, context.wait_seconds).until(
        lambda driver: driver.find_element(*locator).get_attribute("value") == value
    )
@then('I should see "{text_string}" in the results table')
def step_see_in_table(context, text_string):
    """Check that the text appears in the results table."""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), text_string
        )
    )
    assert found
