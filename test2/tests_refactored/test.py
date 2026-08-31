import pytest
from playwright.sync_api import Playwright, sync_playwright, expect
from test2.page_objects.MiscClass import MiscClass

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    miscclass = MiscClass(page)
    miscclass.generated_1(action_arg_0='https://www.saucedemo.com/', locator_arg_0='[data-test="username"]', action_arg_1='standard_user', locator_arg_1='[data-test="password"]', action_arg_2='secret_sauce', locator_arg_2='[data-test="login-button"]', locator_arg_3='[data-test="item-4-title-link"]', locator_arg_4='[data-test="item-0-title-link"] [data-test="inventory-item-name"]', action_arg_3='Sauce Labs Bike Light', locator_arg_5='[data-test="product-sort-container"]', action_arg_4='az')
    miscclass.generated_2(action_keyword_0='$29.99', action_keyword_1='Name (A to Z)Name (A to Z)', action_keyword_2='[data-test="product-sort-container"]', action_keyword_3='lohi', action_keyword_4='div', action_keyword_5='Swag Labs', action_keyword_6=5, locator_arg_0='button', locator_keyword_0='button', locator_arg_1='[data-test="logout-sidebar-link"]', locator_arg_2='[data-test="username"]', action_arg_0='locked_out_user', locator_arg_3='[data-test="password"]', action_arg_1='secret_sauce', locator_arg_4='[data-test="login-button"]', locator_arg_5='[data-test="error"]', action_arg_2='Epic sadface: Sorry, this user has been locked out.')
    context.close()
    browser.close()
with sync_playwright() as playwright:
    run(playwright)