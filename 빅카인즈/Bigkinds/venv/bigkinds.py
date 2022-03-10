from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
from selenium.webdriver.common.keys import Keys

import time

import os
import csv
import argparse

from datetime import datetime as dt
# parser = argparse.ArgumentParser()
# parser.add_argument('--keyword', required=True, help="검색할 키워드")
# parser.add_argument('--start', required=True, help="시작할 날짜")
# parser.add_argument('--end', required=True, help="끝나는 날짜")

# args = parser.parse_args()

keyword = "코로나백신"
start_date = "2020-12-18"
end_date = "2021-02-25"

path = os.getcwd() + "/chromedriver"

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('headless')

driver = webdriver.Chrome(path)

url = f"https://twitter.com/search?q={keyword}&src=recent_search_click"

infos = []

driver.get(url)
driver.implicitly_wait(10)

driver.find_element_by_id('collapse-step-1').click()
driver.implicitly_wait(3)
#언론사선택? 들어갈자리

###############################기간선택
driver.find_element_by_xpath('//*[@id="collapse-step-1-body"]/div[3]/div/div[1]/div[1]/a').click()
driver.implicitly_wait(3)

input_begin = driver.find_element_by_id('search-begin-date')
input_begin.send_keys(Keys.CONTROL + "a")
input_begin.send_keys(Keys.DELETE)
driver.implicitly_wait(3)
input_begin.send_keys(start_date)
driver.implicitly_wait(3)

input_end = driver.find_element_by_id('search-end-date')
input_end.send_keys(Keys.CONTROL + "a")
input_end.send_keys(Keys.DELETE)
driver.implicitly_wait(3)
input_end.send_keys(end_date)
driver.implicitly_wait(3)
##############################키워드 검색
driver.find_element_by_id('total-search-key').send_keys(keyword)
driver.find_element_by_id('total-search-key').send_keys(Keys.ENTER)

##############################페이지 수 추출
time.sleep(1)

MAX_PAGE = driver.find_element_by_class_name('lastNum').get_attribute('data-page')
############################## 기사 추출
result = []
cnt = 1
for _ in range(int(MAX_PAGE)):

    news_results = driver.find_elements_by_css_selector('.cont a div strong span')
    print(news_results)
    for news in news_results:
        news.click()
        time.sleep(.2)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        try:
            link = soup.find("button", class_="btn btn-xsm btn-light")["onclick"]
            link = link[42:-1]    # window.open('about:blank').location.href='https://news.imaeil.com/Economy/2020120113515371230'
        except:
            link = ''
        title = soup.find("h1", class_="title").text
        date = soup.find("ul", class_="info").find("li").text
        date = dt.strptime(date, '%Y-%m-%d').strftime("%d.%b.%y")
        journal = soup.find("p", class_="provider").find("img")["onerror"]
        journal = journal[37:-2]            # javascript:noImageHeaderError(this, '매일신문')
        subtitle = ""
        data = soup.find("div", class_="news-view-body").text
        if soup.find("div", class_="news-view-body").find("h5") is not None:
            subtitle = soup.find("div", class_="news-view-body").find("h5", style = "font-size: 16px !important;").text
            data = data[len(subtitle)+1 : ]
            
        result.append([cnt,title,date,link,journal,subtitle.strip(),data.strip()])
        cnt += 1
        driver.find_element_by_xpath('//*[@id="news-detail-modal"]/div/div/div[2]/button').click()

    driver.find_element_by_xpath('//*[@id="news-results-tab"]/div[6]/div[1]/div/div/div/div[4]/a').click()
    time.sleep(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dir_keyword = keyword.replace(" ", "")
dir_name = BASE_DIR+f"./media/{dir_keyword}"
Path(dir_name).mkdir(parents=True, exist_ok=True)

f = open(os.path.join(
    BASE_DIR, f'media\\{dir_keyword}\\Bigkinds_{start_date}_{end_date}.csv'), "w", newline="", encoding="utf-8")

wr = csv.writer(f)

wr.writerow(["", "Title","Date","Link", "Journal", "Subtitle", "data"])

for i in result:
    wr.writerow(i)

f.close()
driver.quit()