from bs4 import BeautifulSoup
import requests

def get_date(url):
    
    date_string="2023-07-01T00:00:00.000Z"

    response = requests.get(url)
     # 检查响应的状态码
    if response.status_code == 404:
        date_string="2023-07-01T00:00:00.000Z"
    else:
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        caas_attr_time_style = soup.find('div', class_='caas-attr-time-style')  # 選取class為'caas-body'的<div>元素
        # 提取日期字串
        if caas_attr_time_style:
            date_string = caas_attr_time_style.time['datetime']
            

    return date_string