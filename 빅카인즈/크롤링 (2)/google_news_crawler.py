from bs4 import BeautifulSoup
from selenium import webdriver
from pathlib import Path

import pandas as pd
import argparse
import os


def google_crawler(origin_keyword, start, end):
    # parser = argparse.ArgumentParser()

    # parser.add_argument('--keyword', required=True, help="검색할 키워드")
    # parser.add_argument('--start', required=True, help="시작할 날짜 ex. 3/15/2021")
    # parser.add_argument('--end', required=True, help="끝나는 날짜 ex. 3/16/2021")

    # args = parser.parse_args()

    keyword = origin_keyword.replace(" ", "+")
    start = list(start.split('-'))
    end = list(end.split('-'))

    start_date = start[1]+'/'+start[2]+'/'+start[0]
    end_date = end[1]+'/'+end[2]+'/'+end[0]

    # print(start_date, end_date)
    path = os.getcwd() + "/chromedriver"

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(path, chrome_options=options)
    driver.get(
        f"https://www.google.com/search?q={keyword}&hl=en&tbas=0&biw=1920&bih=760&source=lnt&tbs=cdr%3A1%2Ccd_min%3A{start_date}%2Ccd_max%3A{end_date}&tbm=nws")

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    dbsr = soup.select('.dbsr')

    titles = []
    links = []
    dates = []
    sites = []
    cnt = 0
    while True:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        dbsr = soup.select('.dbsr')
        for i in dbsr:
            title = i.select_one('.JheGif.nDgy9d').text
            link = i.a.attrs['href']
            date = i.select_one('.WG9SHc').text
            site = i.select_one('.XTjFC.WF4CUc').text
            titles.append(title)
            links.append(link)
            dates.append(date)
            sites.append(site)
        cnt += 1
        try:
            driver.find_element_by_link_text("Next").click()
        except:
            driver.quit()
            break
        driver.implicitly_wait(1)

    driver.quit()

    dir_keyword = origin_keyword.replace(" ", "")

    def toKoreanStyle(temp_str):
        temp_list = temp_str.split("/")
        for i, v in enumerate(temp_list):
            if len(v) == 1:
                temp_list[i] = "0" + temp_list[i]
        temp = temp_list[-1] + "".join(temp_list[:-1])
        return temp

    dir_start = toKoreanStyle(start_date)
    dir_end = toKoreanStyle(end_date)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    dir_keyword = origin_keyword.replace(" ", "")
    dir_name = BASE_DIR+f"./media/{dir_keyword}"
    Path(dir_name).mkdir(parents=True, exist_ok=True)

    data = {'title': titles, 'link': links,  'site': sites, 'date': dates}
    df = pd.DataFrame(data, columns=['title', 'link', 'site', 'date'])
    df.to_csv(os.path.join(
        BASE_DIR, f'media/{dir_keyword}/google_{dir_start}_{dir_end}.csv'))
    # print("Complete")
    return ((f'google_{dir_start}_{dir_end}.csv'), os.path.join(BASE_DIR, f'media/{dir_keyword}/google_{dir_start}_{dir_end}.csv'))
