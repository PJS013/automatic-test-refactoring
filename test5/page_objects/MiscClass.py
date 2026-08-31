from playwright.sync_api import Page, expect

class MiscClass:

    def __init__(self, page):
        self.page = page

    def generated_0(self, locator_arg_0, action_arg_0, locator_arg_1, action_arg_1, locator_arg_2, locator_arg_3, action_arg_2):
        self.page.locator(locator_arg_0).fill(action_arg_0)
        self.page.locator(locator_arg_1).fill(action_arg_1)
        self.page.locator(locator_arg_2).click()
        expect(self.page.locator(locator_arg_3)).to_contain_text(action_arg_2)

    def generated_1(self, action_keyword_0, action_keyword_1, action_keyword_2, action_keyword_3, action_keyword_4, action_keyword_5, action_keyword_6):
        self.generated_0(locator_arg_0=action_keyword_0, action_arg_0=action_keyword_1, locator_arg_1=action_keyword_2, action_arg_1=action_keyword_3, locator_arg_2=action_keyword_4, locator_arg_3=action_keyword_5, action_arg_2=action_keyword_6)
        self.page.close()