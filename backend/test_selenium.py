from unittest import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from web_server import app
import time

class FlaskAppTests(TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.app = app.test_client()
        cls.app_context = app.app_context()
        cls.app_context.push()

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(10)
        cls.base_url = 'http://127.0.0.1:5000'

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.app_context.pop()

    def test_home_page(cls):
        cls.driver.get(cls.base_url)
        cls.assertIn("Добро пожаловать на сайт!", cls.driver.page_source)

        nav_links = cls.driver.find_elements(By.TAG_NAME, 'a')
        cls.assertEqual(len(nav_links), 3)

        about_link = cls.driver.find_element(By.LINK_TEXT, 'О нас')
        about_link.click()
        cls.assertIn("О нашей компании", cls.driver.page_source)

    def test_login_functionality(self):
        self.driver.get(f"{self.base_url}/login")

        # Поля формы
        username_field = self.driver.find_element(By.ID, 'username')
        password_field = self.driver.find_element(By.ID, 'password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        # Тест с неверными учетными данными
        username_field.send_keys('wrong_user')
        password_field.send_keys('wrong_pass')
        submit_button.click()

        # Проверяем сообщение об ошибке
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        self.assertIn("Неверное имя пользователя или пароль!", self.driver.page_source)
        self.driver.get(f"{self.base_url}/login")

        # Тест с верными учетными данными
        username_field = self.driver.find_element(By.ID, 'username')
        password_field = self.driver.find_element(By.ID, 'password')
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        username_field.send_keys('Admin')
        password_field.send_keys('admin_password')
        submit_button.click()

        # Проверяем успешный вход
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        self.assertIn("Вы успешно вошли на сайт, Admin!", self.driver.page_source)

    def test_navigation(self):
        self.driver.get(self.base_url)

        # Переход на страницу "О нас"
        about_link = self.driver.find_element(By.LINK_TEXT, 'О нас')
        about_link.click()
        self.assertIn("О нашей компании", self.driver.page_source)

        # Возврат на главную страницу
        home_link = self.driver.find_element(By.LINK_TEXT, 'Вернуться на главную')
        home_link.click()
        self.assertIn("Добро пожаловать на сайт!", self.driver.page_source)

    if __name__ == '__main__':
        pass