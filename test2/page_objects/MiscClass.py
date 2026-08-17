from playwright.sync_api import Page, expect

class MiscClass:

    def __init__(self, page):
        self.page = page

    def generated_0(self, locator_arg_0, locator_arg_1, locator_arg_2, action_arg_0, locator_arg_3, modifiers_0, modifiers_1):
        self.page.get_by_text(locator_arg_0).click()
        self.page.get_by_text(locator_arg_1).click()
        self.page.locator(locator_arg_2).select_option(action_arg_0)
        self.page.locator(locator_arg_3).filter(has_text=modifiers_0).nth(modifiers_1).click()

    def generated_1(self, locator_arg_0, action_arg_0, locator_arg_1, action_arg_1, locator_arg_2):
        self.page.locator(locator_arg_0).fill(action_arg_0)
        self.page.locator(locator_arg_1).fill(action_arg_1)
        self.page.locator(locator_arg_2).click()

    def generated_2(self, action_keyword_0, action_keyword_1, action_keyword_2, action_keyword_3, action_keyword_4, locator_arg_0, locator_arg_1, action_arg_0, locator_arg_2, action_arg_1, action_keyword_5, action_keyword_6, action_keyword_7, action_keyword_8, action_keyword_9, action_keyword_10):
        self.generated_1(locator_arg_0=action_keyword_0, action_arg_0=action_keyword_1, locator_arg_1=action_keyword_2, action_arg_1=action_keyword_3, locator_arg_2=action_keyword_4)
        expect(self.page.locator(locator_arg_0)).to_be_visible()
        expect(self.page.locator(locator_arg_1)).to_contain_text(action_arg_0)
        expect(self.page.locator(locator_arg_2)).to_have_value(action_arg_1)
        self.generated_0(locator_arg_0=action_keyword_5, locator_arg_1=action_keyword_6, locator_arg_2=locator_arg_2, action_arg_0=action_keyword_7, locator_arg_3=action_keyword_8, modifiers_0=action_keyword_9, modifiers_1=action_keyword_10)