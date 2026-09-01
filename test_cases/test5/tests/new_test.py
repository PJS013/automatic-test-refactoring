import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.saucedemo.com/")
    page.get_by_text("Swag LabsLoginAccepted").click()
    page.locator("[data-test=\"username\"]").click()
    page.locator("[data-test=\"username\"]").fill("error_user")
    page.locator("[data-test=\"username\"]").press("Tab")
    page.locator("[data-test=\"password\"]").fill("secret_sauce")
    page.locator("[data-test=\"login-button\"]").click()
    expect(page.locator("[data-test=\"error\"]")).to_contain_text("Epic sadface: Sorry, this user has been locked out.")
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
