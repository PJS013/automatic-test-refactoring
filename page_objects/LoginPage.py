class LoginPage:
    def __init__(self, page):
        self.page = page

    def login(self, locator, login, password):
        self.page.locator(locator).fill(login)
        self.page.locator(selector="[data-test=\"password\"]").fill(password)
        self.page.locator("[data-test=\"login-button\"]").click()

    # def select(self, option_selector, option_value, modifier_value):
    #     self.page.locator(option_selector).select_option(option_value)
    #     self.page.locator('div').filter(has_text='Swag Labs').nth(modifier_value).click()