from playwright.sync_api import Playwright, sync_playwright
from test_cases.test1.tests_refactored.test1 import MiscClass
from test_cases.test1.tests_refactored.test1 import LoginPage
from test_cases.test1.tests_refactored.test1 import ExpectMethods

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.saucedemo.com/')
    loginpage = LoginPage(page)
    loginpage.login(locator='[data-test="username"]', login='standard_user', password='secret_sauce')
    expectmethods = ExpectMethods(page)
    expectmethods.expect()
    expectmethods.expect_text(locator='[data-test="item-0-title-link"] [data-test="inventory-item-name"]', text='Sauce Labs Bike Light')
    miscclass = MiscClass(page, loginpage)
    miscclass.generated_2(locator_arg_0='[data-test="product-sort-container"]', action_arg_0='az', locator_arg_1='$29.99')
    page.get_by_text('Name (A to Z)Name (A to Z)').click()
    miscclass.generated_0(locator_keyword_0='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_0='div', modifiers_0='Swag Labs', modifiers_1=5, locator_arg_1='$29.99', locator_arg_2='Name (A to Z)Name (A to Z)')
    page.locator('div').filter(has_text='Swag Labs').nth(5).click()
    page.get_by_text('$29.99').click()
    page.get_by_text('Name (A to Z)Name (A to Z)').click()
    miscclass.generated_0(locator_keyword_0='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_0='div', modifiers_0='Swag Labs', modifiers_1=5, locator_arg_1='$29.99', locator_arg_2='Name (A to Z)Name (A to Z)')
    miscclass.generated_1(locator_arg_0='div', modifiers_0='Swag Labs', modifiers_1=5, locator_arg_1='button', locator_keyword_0='button', locator_arg_2='[data-test="logout-sidebar-link"]', action_keyword_0='[data-test="username"]', action_keyword_1='locked_out_user', action_keyword_2='secret_sauce')
    expectmethods.expect_text(locator='[data-test="error"]', text='Epic sadface: Sorry, this user has been locked out.')
    context.close()
    browser.close()
with sync_playwright() as playwright:
    run(playwright)