import re
from playwright.sync_api import Playwright, sync_playwright, expect
from test5.page_objects.MiscClass import MiscClass

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.saucedemo.com/')
    miscclass = MiscClass(page)
    miscclass.generated_0(locator_arg_0='[data-test="username"]', action_arg_0='problem_user', locator_arg_1='[data-test="password"]', action_arg_1='secret_sauce', locator_arg_2='[data-test="login-button"]', locator_arg_3='[data-test="item-4-title-link"] [data-test="inventory-item-name"]', action_arg_2='Sauce Labs Backpack')
    page.locator('div').filter(has_text='Swag Labs').nth(5).click()
    page.close()
    context.close()
    browser.close()
with sync_playwright() as playwright:
    run(playwright)