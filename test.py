import pytest
from playwright.sync_api import Playwright, sync_playwright, expect

class LoginPage:
    def __init__(self, page):
        self.page = page

    def login(self, locator, login, password):
        self.page.locator(locator).fill(login)
        self.page.locator("[data-test=\"password\"]").fill(password)
        self.page.locator("[data-test=\"login-button\"]").click()

# @pytest.fixture(name="login_page")
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.saucedemo.com/")
    page.screenshot(path='screenshot1.png')
    page.locator("[data-test=\"username\"]").click()
    page.locator("[data-test=\"username\"]").fill("standard_user")
    page.locator("[data-test=\"password\"]").click()
    page.locator("[data-test=\"password\"]").fill("secret_sauce")
    page.screenshot(path='screenshot2.png')
    page.locator("[data-test=\"login-button\"]").click()
    page.screenshot(path='screenshot3.png')
    expect(page.locator("[data-test=\"item-4-title-link\"]")).to_be_visible()
    expect(page.locator("[data-test=\"item-0-title-link\"] [data-test=\"inventory-item-name\"]")).to_contain_text("Sauce Labs Bike Light")
    page.get_by_role("button", name="Open Menu").click()
    expect(page.locator("[data-test=\"logout-sidebar-link\"]")).to_be_visible()
    expect(page.locator("[data-test=\"logout-sidebar-link\"]")).to_contain_text("Logout")
    page.screenshot(path='screenshot4.png')
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)