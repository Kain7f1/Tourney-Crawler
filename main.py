#############################################################################
# 만든이 : Kain7f1 (Hansol Lee)
# 생성일 : 2025-01-17
# 사용 전제 조건 : C:\Users 폴더에 현재 크롬 버전에 맞는 chromedriver.exe를 다운받아주세요

from tourney_crawler import crawl_tourney_result, crawl_tourney_meta


# --------------------------------------------------
# 1. 모든 Tourney url 수집

target_url = "https://play.limitlesstcg.com/tournaments/completed?game=POCKET&show=499&format=STANDARD&platform=all&type=online&time=all"
start_date_str = '2024-12-19'
end_date_str = '2025-01-16'

crawl_tourney_result(target_url, start_date_str)

# --------------------------------------------------
# 2. 덱 별 배틀 결과 수집

tourney_result_file_name = "tourney_result_250117_050044.csv"

# crawl_tourney_meta(tourney_result_file_name)


