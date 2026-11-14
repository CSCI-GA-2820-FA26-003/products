"""Selenium steps for checking the Products service in a browser."""

from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

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
