import pytest
from playwright.sync_api import Playwright, sync_playwright, expect
from test4.page_objects.ExpectMethods import ExpectMethods
from test4.page_objects.MiscClass import MiscClass
from test4.page_objects.LoginPage import LoginPage

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
    expect(page.locator('[data-test="product-sort-container"]')).to_have_value('az')
    page.get_by_text('$29.99').click()
    page.get_by_text('Name (A to Z)Name (A to Z)').click()
    miscclass = MiscClass(page)
    miscclass.generated_0(locator_keyword_0='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_0='div', modifiers_0='Swag Labs', modifiers_1=5, locator_arg_1='$29.99', locator_arg_2='Name (A to Z)Name (A to Z)')
    page.locator('div').filter(has_text='Swag Labs').nth(5).click()
    page.get_by_text('$29.99').click()
    page.get_by_text('Name (A to Z)Name (A to Z)').click()
    miscclass.generated_0(locator_keyword_0='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_0='div', modifiers_0='Swag Labs', modifiers_1=5, locator_arg_1='$29.99', locator_arg_2='Name (A to Z)Name (A to Z)')
    page.locator('div').filter(has_text='Swag Labs').nth(5).click()
    page.get_by_role('button', name='Open Menu').click()
    page.locator('[data-test="logout-sidebar-link"]').click()
    loginpage.login(locator='[data-test="username"]', login='locked_out_user', password='secret_sauce')
    expectmethods.expect_text(locator='[data-test="error"]', text='Epic sadface: Sorry, this user has been locked out.')
    context.close()
    browser.close()
with sync_playwright() as playwright:
    run(playwright)