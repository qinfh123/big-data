# -*- coding: utf-8 -*-
import scrapy
import os
import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


chrome_options = Options()
prefs = {
        'profile.default_content_setting_values':
            {
                'notifications': 2
            }
    }
chrome_options.add_experimental_option('prefs', prefs)

#MAC版本
#browser = webdriver.Chrome(chrome_options=chrome_options)

# Windows版本
chrome_driver=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"  #修改webdriver的绝对位置
browser = webdriver.Chrome(chrome_options=chrome_options,executable_path=chrome_driver)

wait = WebDriverWait(browser, 10)
browser.implicitly_wait(1800)
def get():

    url = "https://www.zhihu.com/signin?next=%2F"

    browser.get(url)
    time.sleep(3)
    browser.find_element_by_xpath('//div[@class = "SignFlow-qrcodeTab"]').click()
    time.sleep(30)
    # browser.find_element_by_xpath('//div[@class="SignFlow-tab"]').click()
    #
    # time.sleep(3)  # 延时的原因是等网页加载完毕再去获取字段
    # browser.find_element_by_xpath('//input[@name="username"]').send_keys("18852003365")  # 用户名输入框
    # browser.find_element_by_xpath('//input[@name="password"]').send_keys("a2430366645")  # 密码输入框
    # try:
    #     browser.find_element_by_xpath('//*[@type="submit"]').click()  # 登录按钮
    # except:
    #     time.sleep(10)
    #     browser.find_element_by_xpath('//*[@type="submit"]').click()
    # time.sleep(3)
    cookies = browser.get_cookies()  # 获取登录后的 cookies
    print(cookies)
    cookie = {}
    for item in cookies:
        cookie[item['name']] = item['value']
    outputPath = open('zhihuCookies.pickle', 'wb')
    pickle.dump(cookie, outputPath)
    outputPath.close()
    return cookie

def read():
    if os.path.exists('zhihuCookies.pickle'):
        readPath = open('zhihuCookies.pickle','rb')
        zhihuCookies = pickle.load(readPath)
    else:
        zhihuCookies = get()
    return zhihuCookies

if __name__ == "__main__":
    zhihuCookies = read()
    browser.get("https://www.zhihu.com/signin?next=%2F")
    for cookie in zhihuCookies:
        browser.add_cookie({
        "domain":".zhihu.com",
        "name":cookie,
        "value":zhihuCookies[cookie],
        "path":'/',
        "expires":None
    })
    browser.get("https://www.zhihu.com/signin?next=%2F")


