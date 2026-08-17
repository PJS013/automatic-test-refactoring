import pytest
from playwright.sync_api import Playwright, sync_playwright, expect
from page_objects.MiscClass import MiscClass

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.saucedemo.com/')
    miscclass = MiscClass(page)
    miscclass.generated_2(action_keyword_0='[data-test="username"]', action_keyword_1='standard_user', action_keyword_2='[data-test="password"]', action_keyword_3='secret_sauce', action_keyword_4='[data-test="login-button"]', locator_arg_0='[data-test="item-4-title-link"]', locator_arg_1='[data-test="item-0-title-link"] [data-test="inventory-item-name"]', action_arg_0='Sauce Labs Bike Light', locator_arg_2='[data-test="product-sort-container"]', action_arg_1='az', action_keyword_5='$29.99', action_keyword_6='Name (A to Z)Name (A to Z)', action_keyword_7='lohi', action_keyword_8='div', action_keyword_9='Swag Labs', action_keyword_10=5)
    miscclass.generated_0(locator_arg_0='$29.99', locator_arg_1='Name (A to Z)Name (A to Z)', locator_arg_2='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_3='div', modifiers_0='Swag Labs', modifiers_1=5)
    miscclass.generated_0(locator_arg_0='$29.99', locator_arg_1='Name (A to Z)Name (A to Z)', locator_arg_2='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_3='div', modifiers_0='Swag Labs', modifiers_1=5)
    miscclass.generated_0(locator_arg_0='$29.99', locator_arg_1='Name (A to Z)Name (A to Z)', locator_arg_2='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_3='div', modifiers_0='Swag Labs', modifiers_1=5)
    page.get_by_role('button', name='Open Menu').click()
    page.locator('[data-test="logout-sidebar-link"]').click()
    miscclass.generated_1(locator_arg_0='[data-test="username"]', action_arg_0='locked_out_user', locator_arg_1='[data-test="password"]', action_arg_1='secret_sauce', locator_arg_2='[data-test="login-button"]')
    expect(page.locator('[data-test="error"]')).to_contain_text('Epic sadface: Sorry, this user has been locked out.')
    context.close()
    browser.close()
with sync_playwright() as playwright:
    run(playwright)