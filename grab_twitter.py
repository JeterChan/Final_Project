from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup #爬蟲用

import pandas as pd
import os


ACCOUNT_NAME = "your_account_name"
PASS_WORD = "your password"
PHONE = "your phone"
subtopic = "味全龍"
keyword = "林智勝"

current_dir = os.getcwd()
driver_name = "chromedriver.exe"
driver_path = current_dir+"\\"+driver_name


#下面這一串資料是在把通知關掉

def output_title_to_database(sub_topic,keyword,titles,URLs):
    df = pd.DataFrame(columns=['Sub_Topic','Keyword','Title', 'URL'])
    for title, URL in zip(titles,URLs):
        row = pd.DataFrame({'Sub_Topic':[sub_topic],'Keyword':[keyword],'Title': [title], 'URL': [URL]})
        df = pd.concat([df, row], ignore_index=True)
    print(df)
    df.to_excel('data/twitter_data.xlsx', index=False)

def grab_twitter_usersearch():
    options = webdriver.ChromeOptions()  
    prefs = {'profile.default_content_setting_values':{'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome(executable_path=driver_path,chrome_options=options)
    driver.get('https://twitter.com')
    time.sleep(5)
    xpath_login = "//*[@id=\"layers\"]/div/div[1]/div/div/div/div/div/div/div/div[1]/a"  # 使用部分文本来定位登录按钮
    elem_login = driver.find_element("xpath",xpath_login)
    ActionChains(driver).click(elem_login).perform()
    #xpath_account_input = "//*[@id=\"layers\"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input"
    time.sleep(6)

    elem_account = driver.find_element(By.NAME, "text")
    ActionChains(driver).click(elem_account).perform()
    elem_account.send_keys(ACCOUNT_NAME)
    elem_account.send_keys(Keys.RETURN)
    time.sleep(10)

    elem_phone = driver.find_element(By.NAME, "text")
    ActionChains(driver).click(elem_phone).perform()
    elem_phone.send_keys(PHONE)
    elem_phone.send_keys(Keys.RETURN)
    time.sleep(10)

    elem_password = driver.find_element(By.NAME, "password")
    ActionChains(driver).click(elem_password).perform()
    elem_password.send_keys(PASS_WORD)
    elem_password.send_keys(Keys.RETURN)
    time.sleep(10)

    xpath_search = "//*[@id=\"react-root\"]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input"
    elem_search = driver.find_element("xpath",xpath_search)
    ActionChains(driver).click(elem_search).perform()
    time.sleep(6)
    elem_search.send_keys("林智勝")
    elem_search.send_keys(Keys.RETURN)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") 
    s_num = 0
    e_num = 1
    i = 0
    print('載入資料開始...')
    while e_num > s_num:
        i = i+1
        elements = driver.find_elements(By.CSS_SELECTOR, '#react-root > div > div > div > main > div > div > div > div > div > div:nth-child(3) > div > section > div > div > div > div > div > article > div > div > div > div > div:nth-child(2)')
        s_num = len(elements)

        elements[s_num - 1].location_once_scrolled_into_view  # 捲動加载資料
        time.sleep(5)  # 延遲1秒

        elements = driver.find_elements(By.CSS_SELECTOR, '#react-root > div > div > div > main > div > div > div > div > div > div:nth-child(3) > div > section > div > div > div > div > div > article > div > div > div > div > div:nth-child(2)')
        e_num = len(elements)
        print('捲動頁面到底部第 %d 次, 前次筆數= %d, 現在筆數= %d' % (i, s_num, e_num))
    print("載入資料結束...")
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    titles_elem = soup.select('#react-root > div > div > div > main > div > div > div > div > div > div:nth-child(3) > div > section > div > div > div > div > div > article > div > div > div > div > div:nth-child(2)')
    URLs_elem = soup.select('#react-root > div > div > div > main > div > div > div > div > div > div:nth-child(3) > div > section > div > div > div > div > div > article > div > div > div > div> div > div > div> div > div > div > div > div > a')
    driver.close()
    titles = []
    URLs = []

    count = 1

    for URL in URLs_elem:
        if count%3==0:
            URL = 'https://twitter.com'+str(URL['href'])
            URLs.append(URL)
        count+=1
        print(URL)

    for title,URL in zip(titles_elem,URLs):
        title = title.text
        titles.append(title)
    
    output_title_to_database(subtopic,keyword,titles,URLs)

grab_twitter_usersearch()