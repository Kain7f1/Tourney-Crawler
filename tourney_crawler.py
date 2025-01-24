#############################
# 만든이 : Kain7f1 (Hansol Lee)
# 생성일 : 2024-12-16
# 사용 전제 조건 : C:\Users 폴더에 현재 크롬 버전에 맞는 chromedriver.exe를 다운받아주세요
#############################

from datetime import datetime
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup
import crawling_tool as cr
import utility_module as util
import time


# url : 타겟 url - limitlesstcg 종료된 토너먼트
# start_date_str : 날짜 범위 - 시작
# end_date_str : 날짜 범위 - 끝
# min_players : 최소 플레이어 수 제한 - 적으면 수집 안함
def crawl_tourney_result(url, start_date_str, end_date_str=None, min_players=64):
    print("[기본값 세팅]")
    # end_date 설정안하면 오늘로 설정
    if end_date_str is None:
        today = date.today()
        end_date_str = today.strftime("%Y-%m-%d")

    # -------------------------------------

    print("[크롤링 시작]")
    data = []   # 데이터 저장용. df로 만들 2차원 리스트

    soup = cr.get_soup(url)
    tr_list = soup.select('div.main div tr')

    # 첫번째 tr은 내용 없음
    for tr in tr_list[1:]:
        # 1. 날짜
        datetime_html = tr.select_one('a.date')
        date_str, time_str = cr.extract_data_time(datetime_html)    # 날짜, 시간 추출
        if not cr.is_date_between(date_str, start_date_str, end_date_str):
            # print("기간이 안맞아서 continue")
            continue

        # 2. 플레이어 수
        players = int(tr.select('td')[5].text)
        if players < min_players:
            # print("인원수가 적어서 continue")
            continue

        # 3. 나머지 정보들
        tourney_name = util.clean_text(tr.select('td')[2].text)     # 특수문자 정제
        organizer = util.clean_text(tr.select('td')[3].text)        # 특수문자 정제
        winner = util.clean_text(tr.select_one('div.winner').text)  # 특수문자 정제
        try:
            country = tr.select_one('img.flag')['data-tooltip']
        except:
            country = "Unknown"

        limitlesstcg_url_base = "https://play.limitlesstcg.com"
        tourney_url = limitlesstcg_url_base + tr.select('td')[2].select_one('a')['href']
        tourney_url = tourney_url[:-10]     # 뒤에 standings 없애기

        #
        date_list = [date_str, tourney_name, organizer, players, winner, country, tourney_url]
        data.append(date_list)

    # -------------------------------------

    print("[엑셀 형태로 저장]")

    # 수집한 데이터를 데이터프레임 형태로 변환
    df = pd.DataFrame(data, columns=["date", "tourney_name", "organizer", "players", "winner", "country", "url"])

    # 엑셀 파일로 저장
    end_time = datetime.now().replace(microsecond=0)  # 시작 시각
    str_end_time = str(end_time)[2:10].replace("-", "") + "_" + str(end_time)[11:].replace(":", "")
    result_file_name = f"tourney_result_{str_end_time}.csv"   # 엑셀 파일 이름. 종료시간을 덧붙어 unique하게 만들어 여러번 실행해도 파일이 덧씌워지지 않음.
    util.create_folder("./tourney_result")
    df.to_csv("./tourney_result/" + result_file_name, encoding="utf-8", index=False)  # 엑셀로 저장

    print(f"총 {len(df)}건의 데이터가 수집되었습니다.")
    print(f"데이터가 {result_file_name} 파일로 저장되었습니다.")
    #
    print("crawl_tourney_result() 종료")


def crawl_tourney_meta(tourney_result_file_name):
    df_url = pd.read_csv("./tourney_result/" + tourney_result_file_name, encoding='utf-8')

    print(df_url.head())

    util.create_folder("./tourney_meta")

    return
