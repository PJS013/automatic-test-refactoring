from playwright.sync_api import Page, expect

class MiscClass:

    def __init__(self, page, loginpage):
        self.page = page
        self.loginpage = loginpage

    def generated_0(self, locator_arg_0, locator_arg_1, locator_arg_2, action_arg_0, locator_arg_3, modifiers_0, modifiers_1):
        self.page.get_by_text(locator_arg_0).click()
        self.page.get_by_text(locator_arg_1).click()
        self.page.locator(locator_arg_2).select_option(action_arg_0)
        self.page.locator(locator_arg_3).filter(has_text=modifiers_0).nth(modifiers_1).click()

    def generated_1(self, action_keyword_0, action_keyword_1, action_keyword_2, action_keyword_3, action_keyword_4, action_keyword_5, action_keyword_6, locator_arg_0, locator_keyword_0, locator_arg_1, action_keyword_7, action_keyword_8, action_keyword_9, locator_arg_2, action_arg_0):
        self.generated_0(locator_arg_0=action_keyword_0, locator_arg_1=action_keyword_1, locator_arg_2=action_keyword_2, action_arg_0=action_keyword_3, locator_arg_3=action_keyword_4, modifiers_0=action_keyword_5, modifiers_1=action_keyword_6)
        self.page.get_by_role(locator_arg_0, name=locator_keyword_0).click()
        self.page.locator(locator_arg_1).click()
        self.loginpage.login(locator=action_keyword_7, login=action_keyword_8, password=action_keyword_9)
        expect(self.page.locator(locator_arg_2)).to_contain_text(action_arg_0)