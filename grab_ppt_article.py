# 導入 模組(module) 
import requests 
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import time
from bs4 import BeautifulSoup
from openpyxl import load_workbook
import emotion 

current_dir = os.getcwd()
driver_name = "chromedriver.exe"
driver_path = current_dir+"\\"+driver_name

#這一邊要改成讀資料庫的 需要讀的是 ptt版面跟次主題的那個配對表
def open_ptt_url():
    ptt_url_data = 'data/ptt.xlsx'
    df = pd.read_excel(ptt_url_data)
    return df

#這一邊要改成輸出到資料庫 需要輸出到 存放ptt內容的資料庫
def output_ptt_data_to_database(sub_topics,titles,links,dates,page_indexes,emotion_scores):
    data_list =[]
    for sub_topic,title,link,date,page_index,emotion_score in zip(sub_topics,titles,links,dates,page_indexes,emotion_scores):
        data_list.append([sub_topic,title,link,date,page_index,emotion_score])
    df_ptt_output = pd.DataFrame(data_list)
    print(data_list)
    df_ptt_output.to_excel("data/ptt_data.xlsx", index=False)

#將ptt網址的字串進行處理
def split_ptt_link(URL,already_get_index):
    split_url = URL.split("index")
    base_url = split_url[0]
    page_index = split_url[1].rstrip(".html")

    print("Base URL:", base_url)  
    print("Page Number:", page_index)  

    if int(page_index)>already_get_index:
        return True,page_index
    else:
        return False,page_index
    
# 這一邊要改成讀資料庫的 需要讀的是 ptt版面跟次主題的那個配對表 更新ptt subtopic的配對表的index ***記得要等所有都做完才能更新
def renew_ptt_subtopic_table_index(SUBTOPIC,URL,page_index):
    data_list =[SUBTOPIC,URL,page_index]
    return data_list

def renew_ptt_subtopic_table_to_database(data_list):
    df_ptt_output = pd.DataFrame(data_list)
    print(data_list)
    df_ptt_output.to_excel("data/ptt.xlsx", index=False)


def grab_ptt_article_everyday():
    sub_topics=[]
    titles=[]
    links=[]
    dates=[]
    page_indexes=[]
    emotion_scores=[]

    df_ptt_subtopic = open_ptt_url()
    new_df_ptt_subtopic = []
    
    options = webdriver.ChromeOptions()  
    prefs = {'profile.default_content_setting_values':{'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome(executable_path=driver_path,chrome_options=options)

    for SUBTOPIC,URL,already_get_index in zip (df_ptt_subtopic['Sub_Topic'],df_ptt_subtopic['PTT_URL'],df_ptt_subtopic['PTT_Index']):
        count=1
        driver.get(URL)
        time.sleep(2)
        is_search_next_page = True
        while(is_search_next_page==True):
            elem_last_page =  driver.find_element(By.XPATH, '//*[@id="action-bar-container"]/div/div[2]/a[2]')
            time.sleep(1)
            ActionChains(driver).click(elem_last_page).perform()
            time.sleep(3)
            current_url =driver.current_url
            is_search_next_page,page_index = split_ptt_link(current_url,already_get_index)
            elem_titles = driver.find_elements(By.CSS_SELECTOR, '#main-container > div> div> div.title >a')
            elem_dates = driver.find_elements(By.CSS_SELECTOR, '#main-container > div > div> div> div.date')
            elem_links = driver.find_elements(By.CSS_SELECTOR, '#main-container > div> div> div.title > a')
            if(count==1):
                new_df_ptt_subtopic.append(renew_ptt_subtopic_table_index(SUBTOPIC,URL,page_index))
                count+=1
            print("這是關於"+SUBTOPIC+"的新聞：")
            if(is_search_next_page==True):
                for title,date,link in zip (elem_titles,elem_dates,elem_links):
                    sub_topics.append(SUBTOPIC)
                    titles.append(title.text)
                    links.append(link.get_attribute('href'))
                    dates.append(date.text)
                    page_indexes.append(page_index)
                    print("標題是"+title.text)
                    emotion_scores.append(emotion.run_emotion_ptt(title.text))

    output_ptt_data_to_database(sub_topics,titles,links,dates,page_indexes,emotion_scores)
    renew_ptt_subtopic_table_to_database(new_df_ptt_subtopic)

grab_ptt_article_everyday()


