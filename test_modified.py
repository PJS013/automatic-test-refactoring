import re
from playwright.sync_api import Playwright, sync_playwright, expect

class LoginPage:

    def __init__(self, page):
        self.page = page

    def login(self, login, password):
        self.page.locator('[data-test="username"]').fill(login)
        self.page.locator('[data-test="password"]').fill(password)
        self.page.locator('[data-test="login-button"]').click()

    def expect_text(self, locator, text):
        expect(self.page.locator(locator)).to_contain_text(text)

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.saucedemo.com/')
    loginpage = LoginPage(page)
    loginpage.login(login='standard_user', password='secret_sauce')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="item-4-title-link"]')).to_be_visible()
    loginpage.expect_text(locator='[data-test="item-0-title-link"] [data-test="inventory-item-name"]', text='Sauce Labs Bike Light')
    expect(page.locator('[data-test="product-sort-container"]')).to_have_value('az')
    page.get_by_text('$29.99').click()
    page.get_by_text('Name (A to Z)Name (A to Z)').click()
    page.locator('[data-test="product-sort-container"]').select_option('lohi')
    page.locator('div').filter(has_text='Swag Labs').nth(5).click()
    page.goto('https://www.saucedemo.com/inventory.html')
    page.get_by_role('button', name='Open Menu').click()
    page.locator('[data-test="logout-sidebar-link"]').click()
    loginpage.login(login='locked_out_user', password='secret_sauce')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    loginpage.expect_text(locator='[data-test="error"]', text='Epic sadface: Sorry, this user has been locked out.')
    context.close()
    browser.close()
with sync_playwright() as playwright:
    run(playwright)