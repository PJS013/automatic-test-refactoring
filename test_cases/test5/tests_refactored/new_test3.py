from playwright.sync_api import Playwright, sync_playwright
from test_cases.test5.page_objects.MiscClass import MiscClass

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.saucedemo.com/')
    miscclass = MiscClass(page)
    miscclass.generated_1(action_keyword_0='[data-test="username"]', action_keyword_1='performance_glitch_user', action_keyword_2='[data-test="password"]', action_keyword_3='secret_sauce', action_keyword_4='[data-test="login-button"]', action_keyword_5='[data-test="item-4-title-link"] [data-test="inventory-item-name"]', action_keyword_6='Sauce Labs Backpack')
    context.close()
    browser.close()
with sync_playwright() as playwright:
    run(playwright)