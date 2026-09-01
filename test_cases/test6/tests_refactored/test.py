from playwright.sync_api import Playwright
from test_cases.test6.page_objects.LoginPage import LoginPage
from test_cases.test6.page_objects.MiscClass import MiscClass

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.saucedemo.com/')
    loginpage = LoginPage(page)
    loginpage.login(locator='[data-test="username"]', login='standard_user', password='secret_sauce')
    miscclass = MiscClass(page)
    miscclass.generated_0(locator_arg_0='[data-test="item-4-title-link"]', locator_arg_1='[data-test="item-0-title-link"] [data-test="inventory-item-name"]', action_arg_0='Sauce Labs Bike Light')
    page.get_by_role('button', name='Open Menu').click()
    miscclass.generated_0(locator_arg_0='[data-test="logout-sidebar-link"]', locator_arg_1='[data-test="logout-sidebar-link"]', action_arg_0='Logout')
    context.close()
    browser.close()