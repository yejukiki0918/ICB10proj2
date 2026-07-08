"""
Klook의 검색 API를 사용하여 대한민국 관련 여행 상품 정보를 수집하고,
그 결과를 SQLite 데이터베이스 파일에 페이지별로 즉시 저장하는 크롤링 프로그램입니다.
"""
import os
import time
import random
import sqlite3
import json
from scrapling import Fetcher

DB_DIR = "klook/data"
DB_PATH = os.path.join(DB_DIR, "klook_products.db")

def init_db():
    """
    SQLite 데이터베이스 및 테이블을 초기화합니다.
    새로운 수집을 위해 기존 테이블이 존재할 경우 삭제 후 새로 생성합니다.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 기존 테이블 삭제 (초기화)
    cursor.execute("DROP TABLE IF EXISTS klook_products")
    
    # 테이블 생성
    cursor.execute("""
        CREATE TABLE klook_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            sub_title TEXT,
            city_name TEXT,
            price_raw TEXT,
            rating_star TEXT,
            review_count TEXT,
            booking_count TEXT,
            deep_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("SQLite 데이터베이스 및 klook_products 테이블 초기화 완료.")

def save_to_db(products):
    """
    수집한 상품 리스트를 SQLite DB에 저장합니다.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.executemany("""
        INSERT INTO klook_products (
            title, sub_title, city_name, price_raw, rating_star, review_count, booking_count, deep_link
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            p["title"],
            p["sub_title"],
            p["city_name"],
            p["price_raw"],
            p["rating_star"],
            p["review_count"],
            p["booking_count"],
            p["deep_link"]
        ) for p in products
    ])
    
    conn.commit()
    conn.close()

def fetch_klook_products():
    # DB 초기화
    init_db()
    
    url = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3"
    
    # 쿼리 파라미터 설정
    params = {
        "location": "158,157,156,25723,5031,8928,24975,28741,545,6166,6268,703649,703648,705582,6955,15088,701102,16467,707516,26374,7204,20296,28972,28785,8898,23546,30633,15378,16365,28742,10956,26961,10093,16560,25178,30570,7558,7741,11925,24865,25140,707332,8989,10706,11364,11745,13523,14446,15281,15603,16655,18214,18323,20392,22390,22675,23237,24520,24762,25060,26454,27895,29136,29872,30051,30265,30376,30466,31247,7030,705101,9079",
        "sort": "most_relevant",
        "tab_key": "0",
        "query": "대한민국",
        "size": "15",
        "search_scope": "main_search",
        "k_lang": "ko_KR",
        "k_currency": "KRW"
    }

    # 요청 헤더 (요청 사항 반영)
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ko_KR",
        "baggage": "sentry-environment=production,sentry-release=web_ssr-platform_20260623_7acde2fb,sentry-public_key=919ae3dd598137e1aa2a88c31e161bb3,sentry-trace_id=f58bdd1f067f452e9a7de0055c9a2c4f,sentry-transaction=SearchResult,sentry-sampled=false,sentry-sample_rand=0.5150356711438143,sentry-sample_rate=0",
        "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&search_scope=main_search",
        "sec-ch-device-memory": "32",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-arch": "arm",
        "sec-ch-ua-full-version-list": '"Google Chrome";v="149.0.7827.155", "Chromium";v="149.0.7827.155", "Not)A;Brand";v="24.0.0.0"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "x-platform": "desktop",
        "x-requested-with": "XMLHttpRequest"
    }

    fetcher = Fetcher()
    
    start = 1
    page_count = 1
    total_count = None
    total_saved = 0
    
    print("Klook 대한민국 상품 정보 수집 및 SQLite DB 저장 시작...")
    
    while True:
        params["start"] = str(start)
        
        try:
            print(f"오프셋 {start} (페이지 {page_count}) 수집 중 (예상 전체: {total_count if total_count else '확인 중'})...")
            response = fetcher.get(url, params=params, headers=headers)
            
            if getattr(response, "status", None) != 200:
                print(f"오류 발생 (HTTP {getattr(response, 'status', None)}). 수집을 중단합니다.")
                break
                
            data = response.json()
            if not data.get("success"):
                print("API 응답 success가 False입니다. 수집을 중단합니다.")
                break
                
            search_result = data.get("result", {}).get("search_result", {})
            
            # 최초 1회 전체 상품 개수 획득
            if total_count is None:
                total_count = search_result.get("total", 0)
                print(f"총 수집 대상 상품 개수: {total_count}")
                
            cards = search_result.get("cards", [])
            if not cards:
                print("더 이상 반환된 상품 데이터가 없습니다. 수집을 종료합니다.")
                break
                
            page_products = []
            for card in cards:
                card_data = card.get("data", {})
                if not card_data:
                    continue
                
                review_obj = card_data.get("review_obj") or {}
                price_obj = card_data.get("price") or {}
                
                product = {
                    "title": card_data.get("title"),
                    "sub_title": card_data.get("sub_title"),
                    "city_name": card_data.get("city_name"),
                    "price_raw": price_obj.get("selling_price"),
                    "rating_star": review_obj.get("star"),
                    "review_count": review_obj.get("number"),
                    "booking_count": review_obj.get("booked"),
                    "deep_link": card_data.get("deep_link")
                }
                page_products.append(product)
                
            # 페이지별 즉시 DB 저장
            if page_products:
                save_to_db(page_products)
                total_saved += len(page_products)
                print(f"현재 페이지 {len(page_products)}개 저장 완료. (누적 저장: {total_saved}개)")
            
            # 10페이지 도달 시 수집 중단
            if page_count >= 10:
                print("지정한 10페이지까지의 수집을 완료했습니다.")
                break
                
            # 다음 페이지 번호 계산 (Klook API의 start 파라미터는 페이지 번호)
            start += 1
            page_count += 1
            
            # 전체 개수를 넘어서거나 반환된 cards가 요청한 size보다 적을 경우 수집 중단
            if total_count and start > total_count:
                print("모든 상품 수집을 완료했습니다.")
                break
                
            # 페이지별 0.1 ~ 1.0초 무작위 딜레이 적용
            delay = random.uniform(0.1, 1.0)
            print(f"지연 대기 시간: {delay:.2f}초...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"요청 중 예외 발생: {e}")
            break
            
    print(f"\n성공적으로 수집 완료! 총 {total_saved}개의 상품 정보를 SQLite DB('{DB_PATH}')에 저장했습니다.")

if __name__ == "__main__":
    fetch_klook_products()
