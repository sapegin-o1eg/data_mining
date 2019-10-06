# -*- coding: utf-8 -*-
import scrapy
from facebookscraper.items import FacebookProfileItem
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from scrapy.loader import ItemLoader
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time
import re


class FacebookSpider(scrapy.Spider):
    name = 'facebook'
    allowed_domains = ['facebook.com']
    start_urls = ['https://facebook.com/']

    def __init__(self, login, pwd, target_users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.pwd = pwd
        self.target_users = target_users
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(chrome_options=self.options)

    def __del__(self):
        self.driver.close()

    def parse(self, response):
        self.driver.get(response.url)
        user_input = self.driver.find_element_by_xpath('//input[@name="email"]')
        pwd_input = self.driver.find_element_by_xpath('//input[@name="pass"]')

        user_input.send_keys(self.login)
        pwd_input.send_keys(self.pwd)
        pwd_input.send_keys(Keys.RETURN)

        for user in self.target_users:
            self.driver.get(f'{self.start_urls[0]}{user}')

            about_btn = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//a[@data-tab-key="about"]')))
            about_btn.click()

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "h3#medley_header_about")))

            name = self.driver.title

            contact_info_btn = self.driver.find_element_by_xpath('//a[@label="Контактная и основная информация"]')
            contact_info_btn.click()

            xpath_birthday = '//div[@id="pagelet_basic"]/div/ul/li/div/div/div/div/span[contains(text(), "г.")]'
            birthday = self.get_attr_by_xpath('textContent', xpath_birthday)

            fbid = self.driver.find_element_by_xpath('//meta[@property="al:android:url"]').get_attribute('content')

            avatar_btn = self.driver.find_element_by_xpath('//a[contains(@class, "profilePicThumb")]')
            avatar_btn.click()

            avatar_img_url = []
            while True:
                time.sleep(1)
                url = self.get_attr_by_xpath('src', '//img[@class="spotlight"]')

                if url:
                    avatar_img_url.append(url)
                    counter = self.get_attr_by_xpath('textContent', '//span[@class="mlm count"]')
                    counter = counter.split('из')
                    counter = [c.strip() for c in counter]
                    if len(counter) == 2 and counter[0] == counter[1]:
                        break
                    next_btn = self.driver.find_element_by_xpath('//a[@title="Далее"]')
                    try:
                        next_btn.click()
                    except ElementNotInteractableException:
                        break
                else:
                    break

            self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)

            friends_btn = self.driver.find_element_by_xpath('//a[@data-tab-key="friends"]')
            friends_btn.click()

            total_friends_count = 0
            while True:
                time.sleep(2)
                friends_in_view = len(self.driver.find_elements_by_xpath('//div[@class="uiProfileBlockContent"]'))
                self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

                if total_friends_count == friends_in_view:
                    break
                total_friends_count = friends_in_view

            friends = self.driver.find_elements_by_xpath('//div[@class="uiProfileBlockContent"]/div/div/div/a')

            friends_dict = {}
            for friend in friends:
                f_name = friend.get_attribute('textContent')
                f_url = friend.get_attribute('href')
                f_id = friend.get_attribute('data-hovercard')
                f_id = re.search(r'id=(\d+)', f_id).group(1)
                friends_dict[f_id] = {'name': f_name, 'profile_url': f_url}

            loader = ItemLoader(item=FacebookProfileItem(), response=response)
            loader.add_value('fbid', fbid)
            loader.add_value('name', name)
            loader.add_value('birthday', birthday)
            loader.add_value('friends', friends_dict)
            loader.add_value('avatar_images', avatar_img_url)

            yield loader.load_item()

    def get_attr_by_xpath(self, attr, xpath):
        try:
            value = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, xpath))).get_attribute(attr)
            return value
        except TimeoutException:
            return None
