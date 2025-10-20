import json
import time, re, urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def get_data():
    url = f"https://www.cwa.gov.tw/V8/C/E/index.html"
    service = Service(r"C:\MyApps\earthquake\broadcast\bot\driver\chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox") # 停用沙箱模式(避免權限不足)
    options.add_argument("--disable-dev-shm-usage") # 停用 /dev/shm 的共享記憶體機制 (強制使用 /tmp，避免網頁卡死)
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080") # 設定視窗大小 (虛擬螢幕解析度)
    browser = webdriver.Chrome(service=service, options=options)

    browser.get(url)
    time.sleep(0.2)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')

    tbody = bsoup.find('tbody', {'class': 'eq_list eq'})
    tr = tbody.find('tr', {'id': 'eq-1'})
    max_intensity = tr.find('td', {'class': 'eq_lv-1'}).get_text()[:-1]
    information = tr.find('td', {'headers': 'information'})
    time_div = information.find('div', {'class': 'eq-detail'})
    times = time_div.find('span').get_text()
    if times[-3:] == "NEW":
        times = times[:-3]
    location = information.find('li', {'style': 'word-break:normal;'}).get_text()
    location = location[2:]

    li_list = information.find_all('li')
    
    scale = li_list[1].get_text()
    scale = scale[2:-2]
    deeth = li_list[2].get_text()
    deeth = deeth[4:]

    new_eq = {
        "max_intensity": max_intensity,   # 最大震度
        "location": location,    # 地點
        "time": times,        # 發生時間
        "depth": scale,       # 深度
        "magnitude": deeth    # 地震規模
        }
    
    return new_eq

# 讀取上一次地震
def load_latest():
    try:
        with open("latest_eq.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    
# 儲存最新地震
def save_new(new_eq):
    with open("latest_eq.json", "w", encoding="utf-8") as f:
        json.dump(new_eq, f, ensure_ascii=False, indent=2)

# 比較新舊數據
def compare_data(previous_eq, new_eq):
    now = time.localtime()
    formatted_time = time.strftime("%H:%M", now)
    if previous_eq is None or previous_eq["time"] != new_eq["time"]:
        print(f"{formatted_time} 發現新地震並且更新資料")
        return True
    print(f"{formatted_time} 沒有發現新地震資料")
    # print(new_eq)
    return False


if __name__ == '__main__':
    new_eq = get_data()

    # 寫入 JSON
    previous_eq = load_latest()

    # 判斷是否與前一次不同

    if previous_eq is None or previous_eq["time"] != new_eq["time"]:
        print("發現新地震並且更新資料")
        # 儲存新資料
        save_new(new_eq)
    else:
        print("地震資料沒有更新")