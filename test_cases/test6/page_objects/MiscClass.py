from playwright.sync_api import Page, expect

class MiscClass:

    def __init__(self, page):
        self.page = page

    def generated_0(self, locator_arg_0, locator_arg_1, action_arg_0):
        expect(self.page.locator(locator_arg_0)).to_be_visible()
        expect(self.page.locator(locator_arg_1)).to_contain_text(action_arg_0)