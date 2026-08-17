from playwright.sync_api import expect

class ExpectMethods:

    def __init__(self, page):
        self.page = page

    def expect_text(self, locator, text):
        expect(self.page.locator(locator)).to_contain_text(text)

    def expect(self):
        expect(self.page.locator('[data-test="item-4-title-link"]')).to_be_visible()