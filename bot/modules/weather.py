import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import asyncio
from functools import partial
import amaindb

CHROME_DRIVER_PATH = r"C:\MyApps\earthquake\broadcast\bot\driver\chromedriver.exe"

# --- 同步抓取函數 ---
def _get_city_weather(num):
    print("收到爬蟲資訊", num)
    url = f"https://www.cwa.gov.tw/V8/C/W/County/County.html?CID={num}"
    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)
    time.sleep(0.2)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')
    browser.quit()

    city = bsoup.find('h2', {'class': 'main-title'}).get_text()[-3:]

    marquee = bsoup.find('a', {'class': 'marquee'}).get_text()[:-3]
    # print(city, marquee)

    # 日期
    date_list = [th.get_text() for th in bsoup.find_all('th', {'scope': 'col'})[:7]]

    tbody = bsoup.find('tbody')

    # 解析行
    def parse_row(tr_class, span_class):
        tr = tbody.find('tr', {'class': tr_class})
        row = []
        for td in tr.find_all('td'):
            s = td.find('span', {'class': span_class})
            row.append(s.get_text() if s else "—")
        return row

    daytime_tem = parse_row('day', 'tem-C is-active')
    night_tem = parse_row('night', 'tem-C is-active')
    feel_tr = tbody.find('tr', {'id': 'lo-temp'})
    feel_like_tem = [td.find('span', {'class': 'tem-C is-active'}).get_text() for td in feel_tr.find_all('td')]
    ultra_tr = tbody.find('tr', {'id': 'ultra'})
    ultraviolet = [td.find('span', {'class': 'sr-only'}).get_text() for td in ultra_tr.find_all('td')]

    data = []
    for i in range(7):
        data.append([date_list[i], daytime_tem[i], night_tem[i], feel_like_tem[i], ultraviolet[i]])
    print("爬蟲完畢並回傳")
    return data, city, marquee

# --- 非同步封裝 ---
async def get_city_weather(num):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_get_city_weather, num))

# 同步抓取最新警報 URL
def _get_url():
    url = "https://www.cwa.gov.tw/V8/C/P/Warning/FIFOWS.html"
    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)
    time.sleep(0.2)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')
    browser.quit()

    warn = bsoup.find('div', {'class': "warn-list"})
    a_tag = warn.find("a")
    return a_tag["href"]

async def get_url():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_url)

# 同步抓取警報內容
def _get_data(link):
    url = f"https://www.cwa.gov.tw/{link}"
    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)
    time.sleep(0.2)
    bsoup = BeautifulSoup(browser.page_source, 'html.parser')
    browser.quit()

    title = bsoup.find('h2', {'class': "main-title"}).get_text().strip()
    datetime = bsoup.find('span', {'class': 'datetime'}).get_text().strip()
    content = bsoup.find('p', {'id': "WarnContent"}).get_text().strip()

    return {"title": title, "time": datetime, "content": content}

async def get_data(link):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_get_data, link))

# 讀取/儲存最新警報
def load_latest():
    try:
        with open("latest_wea.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

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
    return False

# 測試
if __name__ == '__main__':
    import asyncio
    data, city, massage = asyncio.run(get_city_weather("09020"))
    print(data, city, massage)
