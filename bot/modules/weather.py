import json
import time, re, urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def get_url():
    url = f"https://www.cwa.gov.tw/V8/C/P/Warning/FIFOWS.html"
    service = Service(r"C:\MyApps\earthquake\bot\driver\chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 背景執行
    browser = webdriver.Chrome(service=service, options=options)

    browser.get(url)
    time.sleep(0.2)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    warn = bsoup.find('div', {'class', "warn-list"})
    a_tag = warn.find("a")
    href_value = a_tag["href"]

    return href_value

def get_data(link):
    url = f"https://www.cwa.gov.tw/{link}"
    service = Service(r"C:\MyApps\earthquake\bot\driver\chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 背景執行
    browser = webdriver.Chrome(service=service, options=options)

    browser.get(url)
    time.sleep(0.2)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    title = bsoup.find('h2', {'class': "main-title"}).get_text().strip()
    datetime = bsoup.find('span', {'class': 'datetime'}).get_text().strip()
    content = bsoup.find('p', {'id': "WarnContent"}).get_text().strip()

    new_wea = {
        "title": title,
        "time": datetime,
        "content": content
        }

    return new_wea

# 讀取上一次天氣警報
def load_latest():
    try:
        with open("latest_wea.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    
# 儲存最新天氣警報
def save_new(new_wea):
    with open("latest_wea.json", "w", encoding="utf-8") as f:
        json.dump(new_wea, f, ensure_ascii=False, indent=2)

# 比較新舊數據
def compare_data(previous_wea, new_wea):
    now = time.localtime()
    formatted_time = time.strftime("%H:%M", now)
    if previous_wea is None or previous_wea["time"] != new_wea["time"]:
        print(f"{formatted_time} 發現新氣象並且更新資料")
        return True
    print(f"{formatted_time} 沒有發現新氣象資料")
    # print(new_wea)
    return False

if __name__ == '__main__':
    link = get_url()
    data = get_data(link)

    for row in data:
        print(row)