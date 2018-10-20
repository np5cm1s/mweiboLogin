# -*- coding: utf-8 -*-
import io
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from PIL import Image
# import numpy as np
# from ims import ims
import json


class WeiboLogin(object):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.browser, 20)
        self.username = ""
        self.passwd = ""

    def login(self):
        """
        登陆
        :return:
        """
        self.browser.get("https://passport.weibo.cn/signin/login?refer=https://m.weibo.cn")
        time.sleep(2)
        user = self.wait.until(EC.presence_of_element_located((By.ID, "loginName")))
        user.clear()
        user.send_keys(self.username)
        passwd = self.wait.until(EC.presence_of_element_located((By.ID, "loginPassword")))
        passwd.clear()
        passwd.send_keys(self.passwd)
        passwd.send_keys(Keys.ENTER)

    def get_screenshot(self):
        """
        获取网页截图
        :return:
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(io.BytesIO(screenshot))
        return screenshot

    def get_position(self):
        """
        获取验证码位置
        :return:
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'patt-shadow')))
        time.sleep(2)  # 适当延迟,避免截图过早
        size = img.size  # 图片大小
        location = img.location  # 图片在网页中的位置
        top, buttom, left, right = location["y"], location["y"]+size["height"],location["x"],location["x"]+size["width"]
        return top, buttom, left, right

    def get_image(self):
        """
        获取验证码图片
        :return:
        """
        # 获取验证码图片位置
        top, buttom, left, right = self.get_position()
        # 获取网页截图
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, buttom))
        captcha.save('captcha.png')
        return captcha

    def contrast(self, captcha):
        """
        匹配图片
        :return: 拖动顺序
        """
        return str(self.getidf(captcha))

    def move(self, order):
        time.sleep(2)
        dots = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "patt-dots")))
        elements = [dots[int(i)-1] for i in order]  # 给获取到的四个点排序
        times = 50
        for i in range(4):
            if i != 0:
                x, y = elements[i].location["x"]-elements[i-1].location["x"], elements[i].location["y"]-elements[i-1].location["y"]
                for k in range(times):
                    ActionChains(self.browser).move_by_offset(xoffset=x/times, yoffset=y/times).perform()
            else:
                ActionChains(self.browser).move_to_element(elements[i]).click_and_hold().perform()
        ActionChains(self.browser).release().perform()
        time.sleep(3)

    def run(self):
        # 登陆
        self.login()
        # 获取验证码对象
        captcha = self.get_image()
        # 获取匹配出来的拖动顺序
        order = self.contrast(captcha)
        print("拖动顺序:", order)
        # 按顺序拖动
        self.move(order)
        time.sleep(5)
        self.browser.save_screenshot('mweibo.png')
        self.browser.get("https://www.weibo.com")
        time.sleep(5)
        self.browser.save_screenshot('weibocom.png')
        cookies = self.browser.get_cookies()
        jsonCookies = json.dumps(cookies)
        with open('cookies.json', 'w') as f:
        	f.write(jsonCookies)
        
    def getidf(self,im):
        im = im.convert("L")
        data = im.load()
        idfdata = [data[80,30],data[30,80],data[130,80],data[80,130]]
        idfdata2 = [9,data[78,28],data[82,38],data[28,78],data[28,82],
                    data[132,78],data[132,82],data[78,132],data[82,132],
                    data[100,60]]
        idf =''
        for pix in idfdata:
            idf = idf+('0' if pix > 200 else '1')
        for pix in idfdata2:
            idfdata2[idfdata2.index(pix)] = 0 if pix > 200 else 1
        # 判断idf的值
        if idf == '0111':
            if idfdata2[3] > idfdata2[4]: return 1342
            else: return 2431
        elif idf == '1011':
            if idfdata2[1] > idfdata2[2]: return 1243
            else: return 3421
        elif idf == '1101':
            if idfdata2[1] > idfdata2[2]: return 4312
            else: return 2134
        elif idf == '1110':
            if idfdata2[1] > idfdata2[2]: return 3124
            else: return 4213

        elif idf == '1000':
            if idfdata2[1] > idfdata2[2]: return 4123
            else: return 3214
        elif idf == '0100':
            if idfdata2[3] > idfdata2[4]: return 4132
            else: return 2431
        elif idf == '0010':
            if idfdata2[5] > idfdata2[6]: return 3241
            else: return 1423
        elif idf == '0001':
            if idfdata2[7] > idfdata2[8]: return 2341
            else: return 1432
            
        elif idf == '1010':
            if idfdata2[9] > 0:
                if idfdata2[1] > idfdata2[2]: return 1234
                else: return 4321
            else:
                if idfdata2[1] > idfdata2[2]: return 3412
                else: return 2143
        elif idf == '0101':
            if idfdata2[9] > 0:
                if idfdata2[3] > idfdata2[4]: return 1324
                else: return 4231
            else:
                if idfdata2[2] > idfdata2[3]: return 2413
                else: return 3142

        else:
            return (1234)


if __name__ == "__main__":
    weibo = WeiboLogin()
    weibo.run()

