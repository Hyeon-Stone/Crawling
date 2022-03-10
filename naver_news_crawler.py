from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path

import os
import csv
import argparse


def naver_crawler(origin_keyword, start, end):
    # parser = argparse.ArgumentParser()

    # parser.add_argument('--keyword', required=True, help="검색할 키워드")
    # parser.add_argument('--start', required=True, help="시작할 날짜")
    # parser.add_argument('--end', required=True, help="끝나는 날짜")

    # args = parser.parse_args()

    keyword = origin_keyword.replace(" ", "+")

    start_date = start.replace("-", "")
    end_date = end.replace("-", "")

    start = start.replace("-", ".")
    end = end.replace("-", ".")
    # keyword = "코로나"
    # start_date = "20191201"
    # end_date = "20191231"
    path = os.getcwd() + "/chromedriver"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')

    driver = webdriver.Chrome(path, options=chrome_options)

    url = f"https://search.naver.com/search.naver?where=news&"\
        f"query={keyword}&sort=0&ds={start}&de={end}&nso=so:r,p:"\
        f"from{start_date}to{end_date},a:all&field=1"

    infos = []

    driver.get(url)
    driver.implicitly_wait(10)

    cnt = 1
    before_date = ""

    while True:
        html = driver.page_source
        bs = BeautifulSoup(html, 'html.parser')
        infos += bs.find("ul", class_="list_news").find_all("li")
        next_page = bs.find("div", class_="sc_page").find_all("a")[-1]

        if (next_page["aria-disabled"] != "false") and (cnt != 400):
            break

        cnt += 1
        if cnt <= 400:
            driver.get("https://search.naver.com/search.naver" +
                       next_page["href"])
            driver.implicitly_wait(10)
        else:
            temp_date = infos[-1].find("div",
                                       class_="info_group").find("span", class_="info").text
            temp_date = temp_date.replace(".", "")
            if temp_date == before_date:
                if int(end_date) == int(temp_date):
                    break
                else:
                    temp_date = str(int(temp_date) + 1)

            before_date = temp_date

            url = f"https://search.naver.com/search.naver?where=news&"\
                f"query={keyword}&sort=0&ds={start}&de={end}&nso=so:r,p:"\
                f"from{temp_date}to{end_date},a:all&field=1"
            driver.get(url)
            driver.implicitly_wait(10)
            cnt = 1

    # print("Finish crawl infos")

    # 중복 제거 코드
    temp = []

    for i in infos:
        if i not in temp:
            temp.append(i)

    infos = temp

    result = []

    # print("Start get info")
    cnt = 0
    for info in infos:
        if info.find("a", class_="news_tit") is None:
            continue
        link = info.find("a", class_="news_tit")["href"]
        # link = info.find("dl").find("a")["href"]

        title = info.find("a", class_="news_tit")["title"]
        # title = info.find("dl").find("a")["title"]

        if info.find("div", class_="info_group").find("a", class_="info press") is None:
            continue
        where = info.find("div", class_="info_group").find(
            "a", class_="info press").text

        date = info.find("div", class_="info_group").find_all(
            "span", class_="info")
        if len(date) > 1:
            date = date[-1].text
        else:
            date = date[0].text

        # temp = info.find("dl").find("dd").text
        result.append([cnt, title, link, where, date])
        cnt += 1
        # print([date, title, where, link])

        # try :
        #     pattern = '\d+.\d+.\d+.'
        #     r = re.compile(pattern)
        #     date = r.search(temp).group(0)
        # except AttributeError:
        #     pattern = '\w* (\d\w*)'
        #     r = re.compile(pattern)
        #     date = r.search(temp).group(1)

    # 파일 저장 하기

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    dir_keyword = origin_keyword.replace(" ", "")
    dir_name = BASE_DIR+f"./media/{dir_keyword}"
    Path(dir_name).mkdir(parents=True, exist_ok=True)

    # print(dir_keyword)
    # print(dir_name)
    # print(os.path.join(BASE_DIR, f'{dir_keyword}/naver_{start_date}_{end_date}.csv'))

    f = open(os.path.join(
        BASE_DIR, f'media\\{dir_keyword}\\naver_{start_date}_{end_date}.csv'), "w", newline="", encoding="utf-8")

    wr = csv.writer(f)

    wr.writerow(["","date", "title", "where", "link"])

    for i in result:
        wr.writerow(i)

    f.close()
    driver.quit()
    return (f'naver_{start_date}_{end_date}.csv', os.path.join(BASE_DIR, f'media\\{dir_keyword}\\naver_{start_date}_{end_date}.csv'))
