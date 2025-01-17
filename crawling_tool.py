import re
import os
import time
import requests
from datetime import datetime
import pandas as pd
import utility_module as util
from bs4 import BeautifulSoup
from selenium import webdriver


#############################################################################
#                                 << 설정값 >>
# dcinside 헤더 :  dcinside 봇 차단을 위한 헤더 설정
headers_dc = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "sec-ch-ua-mobile": "?0",
        "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ko-KR,ko;q=0.9"
    }

# 목적에 맞는 헤더를 설정한다
headers = headers_dc


###############################################################################
#                                 << 함수들 >>                                 #
###############################################################################
# get_driver()
# 사용 전제 조건 : Users 폴더에 버전에 맞는 chromedriver.exe를 다운받아주세요
# 기능 : driver를 반환합니다
# 리턴값 : driver
def get_driver():
    CHROME_DRIVER_PATH = "C:/Users/chromedriver.exe"    # (절대경로) Users 폴더에 chromedriver.exe를 설치했음
    options = webdriver.ChromeOptions()                 # 옵션 선언
    # [옵션 설정]
    # options.add_argument("--start-maximized")         # 창이 최대화 되도록 열리게 한다.
    options.add_argument("--headless")                  # 창이 없이 크롬이 실행이 되도록 만든다
    options.add_argument("disable-infobars")            # 안내바가 없이 열리게 한다.
    options.add_argument("disable-gpu")                 # 크롤링 실행시 GPU를 사용하지 않게 한다.
    options.add_argument("--disable-dev-shm-usage")     # 공유메모리를 사용하지 않는다
    options.add_argument("--blink-settings=imagesEnabled=false")    # 이미지 로딩 비활성화
    options.add_argument('--disk-cache-dir=/path/to/cache-dir')     # 캐시 사용 활성화
    options.page_load_strategy = 'none'             # 전체 페이지가 완전히 로드되기를 기다리지 않고 다음 작업을 수행 (중요)
    options.add_argument('--log-level=3')           # 웹 소켓을 통한 로그 메시지 비활성화
    options.add_argument('--no-sandbox')            # 브라우저 프로파일링 비활성화
    options.add_argument('--disable-plugins')       # 다양한 플러그인 및 기능 비활성화
    options.add_argument('--disable-extensions')    # 다양한 플러그인 및 기능 비활성화
    options.add_argument('--disable-sync')          # 다양한 플러그인 및 기능 비활성화
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    return driver


#############################################################################
# get_soup()
# 기능 : url을 받아 requests를 사용하여 soup를 리턴하는 함수입니다
# 특징 : 오류발생 시 재귀하기 때문에, 성공적으로 soup를 받아올 수 있습니다.
def get_soup(url, time_sleep=0, max_retries=600):
    try:
        if max_retries <= 0:
            print("[최대 재시도 횟수 초과 : get_soup()]")
            return None
        with requests.Session() as session:
            response = session.get(url, headers=headers)
            time.sleep(time_sleep)
        soup = BeautifulSoup(response.text, "html.parser")
        if len(soup) == 0:  # 불러오는데 실패하면
            print(f"[soup 로딩 실패, 반복] [get_soup(time_sleep=1)]")
            soup = get_soup(url, 1)
    except Exception as e:
        print(f"[오류 발생, 반복] [get_soup(time_sleep=1)] ", e)
        soup = get_soup(url, 1, max_retries-1)
    return soup


# 날짜 추출 함수
def extract_data_time(html):
    match = re.search(r'data-time="(\d+)"', str(html))
    if match:
        timestamp_ms = int(match.group(1))
        timestamp_s = timestamp_ms / 1000

        try:
            dt = datetime.fromtimestamp(timestamp_s)
            date_str = dt.strftime("%Y-%m-%d")  # 날짜를 YYYY-MM-DD 형식으로 포맷
            time_str = dt.strftime("%H:%M:%S")  # 시간을 HH:MM:SS 형식으로 포맷
            return date_str, time_str

        except Exception as e:
            print(f"Error converting timestamp: {e}")
            return None, None

    else:
        return None, None


# 주어진 날짜가 두 날짜 사이에 있는지 검사합니다. (두 날짜 포함)
def is_date_between(target_date_str, start_date_str, end_date_str):
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        if start_date <= target_date <= end_date:
            return True
        else:
            return False

    except ValueError:
        print("잘못된 날짜 형식입니다. YYYY-MM-DD 형식을 사용하세요.")
        return False


# 텍스트를 정제하여 영어, 숫자, 공백, ASCII 특수문자만 남깁니다.
def clean_text(text):
    pattern = r"[^a-zA-Z0-9\s!\"#$%&'()*+,\-./:;<=>?@\[\\\]\^_`{|}~\u00C0-\u00FF]"
    cleaned_text = re.sub(pattern, "", text)
    if cleaned_text and len(cleaned_text) >= 1:
        return cleaned_text
    else:
        return "temp_name"
