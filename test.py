import re

import pytest
from playwright.sync_api import Playwright, sync_playwright, expect

class LoginPage:
    def __init__(self, page):
        self.page = page

    def login(self, locator, login, password):
        self.page.locator(locator).fill(login)
        self.page.locator(locator="[data-test=\"password\"]").fill(password)
        self.page.locator("[data-test=\"login-button\"]").click()

    # def select(self, option_selector, option_value, modifier_value):
    #     self.page.locator(option_selector).select_option(option_value)
    #     self.page.locator('div').filter(has_text='Swag Labs').nth(modifier_value).click()

class ExpectMethods:
    def __init__(self, page):
        self.page = page

    # def login(self, locator, login, password):
    #     self.page.locator(locator).fill(login)
    #     self.page.locator("[data-test=\"password\"]").fill(password)
    #     self.page.locator("[data-test=\"login-button\"]").click()
    #     expect(self.page.locator("[data-test=\"item-4-title-link\"]")).to_be_visible()

    def expect_text(self, locator, text):
        expect(self.page.locator(locator)).to_contain_text(text)

    def expect(self):
        expect(self.page.locator("[data-test=\"item-4-title-link\"]")).to_be_visible()


# @pytest.fixture(name="login_page")
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.saucedemo.com/")
    page.locator("[data-test=\"username\"]").click()
    page.locator("[data-test=\"username\"]").fill("standard_user")
    page.locator("[data-test=\"password\"]").click()
    page.locator("[data-test=\"password\"]").fill("secret_sauce")
    page.locator("[data-test=\"login-button\"]").click()
    expect(page.locator("[data-test=\"item-4-title-link\"]")).to_be_visible()
    expect(page.locator("[data-test=\"item-0-title-link\"] [data-test=\"inventory-item-name\"]")).to_contain_text("Sauce Labs Bike Light")
    expect(page.locator("[data-test=\"product-sort-container\"]")).to_have_value("az")
    page.get_by_text("$29.99").click()
    page.get_by_text("Name (A to Z)Name (A to Z)").click()
    page.locator(selector="[data-test=\"product-sort-container\"]").select_option("lohi")
    page.locator("div").filter(has_text="Swag Labs").nth(5).click()
    # page.goto("https://www.saucedemo.com/inventory.html")
    # page.get_by_text("$29.99").click()
    # page.get_by_text("Name (A to Z)Name (A to Z)").click()
    # page.locator("[data-test=\"product-sort-container\"]").select_option("lohi")
    # page.locator("div").filter(has_text="Swag Labs").nth(5).click()
    page.get_by_role("button", name="Open Menu").click()
    page.locator("[data-test=\"logout-sidebar-link\"]").click()
    page.locator("[data-test=\"username\"]").click()
    page.locator("[data-test=\"username\"]").fill("locked_out_user")
    page.locator("[data-test=\"username\"]").press("Tab")
    page.locator("[data-test=\"password\"]").fill("secret_sauce")
    page.locator("[data-test=\"login-button\"]").click()
    expect(page.locator("[data-test=\"error\"]")).to_contain_text("Epic sadface: Sorry, this user has been locked out.")

    # ---------------------
    context.close()
    browser.close()

# @pytest.fixture(name="login_page")
# def run2(playwright: Playwright) -> None:
#     browser = playwright.chromium.launch(headless=False)
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto("https://www.saucedemo.com/")
#     page.locator("[data-test=\"username\"]").click()
#     page.locator("[data-test=\"username\"]").fill("segsgt")
#     page.locator("[data-test=\"password\"]").click()
#     page.locator("[data-test=\"password\"]").fill("secret_sauce")
#     page.locator("[data-test=\"login-button\"]").click()
#     expect(page.locator("[data-test=\"item-4-title-link\"]")).to_be_visible()
#     expect(page.locator("[data-test=\"item-0-title-link\"] [data-test=\"inventory-item-name\"]")).to_contain_text("Sauce Labs Bike Light")
#     expect(page.locator("[data-test=\"product-sort-container\"]")).to_have_value("az")
#     page.get_by_text("$29.99").click()
#     page.get_by_text("Name (A to Z)Name (A to Z)").click()
#     page.locator("[data-test=\"product-sort-container\"]").select_option("lohi")
#     page.locator("div").filter(has_text="Swag Labs").nth(5).click()
#     # page.goto("https://www.saucedemo.com/inventory.html")
#     # page.get_by_text("$29.99").click()
#     # page.get_by_text("Name (A to Z)Name (A to Z)").click()
#     # page.locator("[data-test=\"product-sort-container\"]").select_option("lohi")
#     # page.locator("div").filter(has_text="Swag Labs").nth(5).click()
#     page.get_by_role("button", name="Open Menu").click()
#     page.locator("[data-test=\"logout-sidebar-link\"]").click()
#     page.locator("[data-test=\"username\"]").click()
#     page.locator("[data-test=\"username\"]").fill("locked_out_user")
#     page.locator("[data-test=\"username\"]").press("Tab")
#     page.locator("[data-test=\"password\"]").fill("secret_sauce")
#     page.locator("[data-test=\"login-button\"]").click()
#     expect(page.locator("[data-test=\"error\"]")).to_contain_text("Epic sadface: Sorry, this user has been locked out.")
#
#     # ---------------------
#     context.close()
#     browser.close()

with sync_playwright() as playwright:
    run(playwright)
