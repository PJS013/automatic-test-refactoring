from playwright.sync_api import expect


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
