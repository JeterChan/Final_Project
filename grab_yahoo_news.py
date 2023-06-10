#模擬按鍵行為用套件
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 
import requests
import json
import pandas as pd

#爬蟲用
from bs4 import BeautifulSoup 

import time
import os

current_dir = os.getcwd()
driver_name = "chromedriver.exe"
driver_path = current_dir+"\\"+driver_name

def output_title_to_database(main_topic,sub_topic,titles,URLs):
    df = pd.DataFrame(columns=['Main_Topic','Sub_Topic','Title', 'URL'])
    count=1
    for title, URL in zip(titles,URLs):
        if (count%4)!=2:
            row = pd.DataFrame({'Main_Topic':[main_topic],'Sub_Topic':[sub_topic],'Title': [title], 'URL': [URL]})
            df = pd.concat([df, row], ignore_index=True)
        count+=1
    print(df)
    df.to_excel('data/news_data.xlsx', index=False)


def grab_yahoo_usersearch_new():
    subtopic = "棒球"
    options = webdriver.ChromeOptions()  
    prefs = {'profile.default_content_setting_values':{'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome(executable_path=driver_path,chrome_options=options)

    driver.get('https://tw.news.yahoo.com/')
    time.sleep(5)

    #找到關鍵字的element 並且將關鍵字輸入
    elem = driver.find_element(By.NAME, "p")
    elem.clear()
    ActionChains(driver).double_click(elem).perform()
    elem.send_keys(subtopic)
    elem.send_keys(Keys.RETURN)
    time.sleep(5)

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") 
    s_num = 0
    e_num = 1
    i = 0
    count = 0
    print('載入資料開始...')
    while count<3:
        i = i+1
        elements = driver.find_elements(By.CSS_SELECTOR, '#stream-container-scroll-template > li> div > div > div > div > h3')
        s_num = len(elements)

        elements[s_num - 1].location_once_scrolled_into_view  # 捲動加载資料
        time.sleep(5)  # 延遲1秒

        elements = driver.find_elements(By.CSS_SELECTOR, '#stream-container-scroll-template > li> div > div > div > div > h3')
        e_num = len(elements)
        print('捲動頁面到底部第 %d 次, 前次筆數= %d, 現在筆數= %d' % (i, s_num, e_num))
        count = count+1
    print("載入資料結束...")


    soup = BeautifulSoup(driver.page_source, 'lxml')
    titles_elem = soup.select('#stream-container-scroll-template > li> div > div > div > div > h3')
    URLs_elem = soup.select('#stream-container-scroll-template > li> div > div > div > div > h3 > a')

    URLs = []
    titles = []

    for title,URL in zip(titles_elem,URLs_elem):
        URL = 'https://tw.news.yahoo.com/'+URL['href']
        URLs.append(URL)
        title = title.text
        titles.append(title)
    output_title_to_database("運動",subtopic,titles,URLs)
    driver.close()


grab_yahoo_usersearch_new()
