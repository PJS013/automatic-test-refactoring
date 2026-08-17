import re
from playwright.sync_api import Playwright, sync_playwright, expect
from page_objects.MiscClass import MiscClass

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.saucedemo.com/')
    miscclass = MiscClass(page)
    miscclass.generated_0(locator_arg_0='[data-test="username"]', action_arg_0='locked_out_user', locator_arg_1='[data-test="password"]', action_arg_1='secret_sauce', locator_arg_2='[data-test="login-button"]', locator_arg_3='[data-test="error"]', action_arg_2='Epic sadface: Sorry, this user has been locked out.')
    page.close()
    context.close()
    browser.close()
with sync_playwright() as playwright:
    run(playwright)