"""Selenium steps for checking the Products service in a browser."""

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
