import pytest
from playwright.sync_api import Playwright, sync_playwright, expect
from test3.page_objects.LoginPage import LoginPage
from test3.page_objects.MiscClass import MiscClass

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.saucedemo.com/')
    loginpage = LoginPage(page)
    miscclass = MiscClass(page, loginpage)
    miscclass.generated_2(action_keyword_0='[data-test="username"]', action_keyword_1='standard_user', action_keyword_2='secret_sauce', locator_arg_0='[data-test="item-4-title-link"]')
    expect(page.locator('[data-test="item-0-title-link"] [data-test="inventory-item-name"]')).to_contain_text('Sauce Labs Bike Light')
    expect(page.locator('[data-test="product-sort-container"]')).to_have_value('az')
    miscclass.generated_0(locator_arg_0='$29.99', locator_arg_1='Name (A to Z)Name (A to Z)', locator_arg_2='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_3='div', modifiers_0='Swag Labs', modifiers_1=5)
    miscclass.generated_0(locator_arg_0='$29.99', locator_arg_1='Name (A to Z)Name (A to Z)', locator_arg_2='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_3='div', modifiers_0='Swag Labs', modifiers_1=5)
    miscclass.generated_0(locator_arg_0='$29.99', locator_arg_1='Name (A to Z)Name (A to Z)', locator_arg_2='[data-test="product-sort-container"]', action_arg_0='lohi', locator_arg_3='div', modifiers_0='Swag Labs', modifiers_1=5)
    miscclass.generated_1(action_keyword_0='$29.99', action_keyword_1='Name (A to Z)Name (A to Z)', action_keyword_2='[data-test="product-sort-container"]', action_keyword_3='lohi', action_keyword_4='div', action_keyword_5='Swag Labs', action_keyword_6=5, locator_arg_0='button', locator_keyword_0='button', locator_arg_1='[data-test="logout-sidebar-link"]', action_keyword_7='[data-test="username"]', action_keyword_8='locked_out_user', action_keyword_9='secret_sauce', locator_arg_2='[data-test="error"]', action_arg_0='Epic sadface: Sorry, this user has been locked out.')
    context.close()
    browser.close()
with sync_playwright() as playwright:
    run(playwright)