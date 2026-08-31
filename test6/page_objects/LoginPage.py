class LoginPage:

    def __init__(self, page):
        self.page = page

    def login(self, locator, login, password):
        self.page.locator(locator).fill(login)
        self.page.locator('[data-test="password"]').fill(password)
        self.page.locator('[data-test="login-button"]').click()