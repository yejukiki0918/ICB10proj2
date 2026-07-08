"""
klook/src/scrape_klook.py

klook 검색 결과 API를 호출하여 1~10페이지 데이터를 수집하고,
sqlite 데이터베이스(klook/data/klook_products.db)에 저장하는 스크립트.
작성자: Antigravity
생성일: 2026-06-27
"""

import requests
import sqlite3
import json
import os
import time

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS klook_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            city TEXT,
            category TEXT,
            selling_price TEXT,
            market_price TEXT,
            star REAL,
            review_count TEXT,
            link TEXT,
            image_url TEXT,
            location TEXT
        )
    ''')
    conn.commit()
    return conn

def fetch_klook_data(page_index):
    url = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3"
    
    # 쿼리 파라미터. start는 페이지네이션의 인덱스.
    params = {
        "location": "158,157,156,20544,25723,5031,8928,24975,28741,545,6166,6268,703649,703648,705582,6955,15088,701102,16467,707516,26374,7204,20296,28785,28972,8898,23546,30633,15378,16365,28742,10956,26961,10093,16560,25178,7741,11925,24865,25140,30570,7030,707332,7558,8989,10706,11364,11745,13523,14446,15281,15603,16655,18214,18323,20392,22390,22675,23237,24520,24762,25060,26454,27895,29136,29872,30051,30265,30376,30466,31247,705101,9079",
        "sort": "most_relevant",
        "tab_key": "0",
        "start": str(page_index),
        "query": "대한민국",
        "size": "15",
        "search_scope": "main_search",
        "k_lang": "ko_KR",
        "k_currency": "KRW"
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ko_KR",
        "priority": "u=1, i",
        "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "x-klook-market": "global",
        "x-klook-user-residence": "10_KR",
        "x-platform": "desktop",
        "x-requested-with": "XMLHttpRequest"
    }
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch page {page_index + 1}, status code: {response.status_code}")
        return None

def parse_and_insert(conn, data):
    cursor = conn.cursor()
    cards = data.get("result", {}).get("search_result", {}).get("cards", [])
    
    if not cards:
        print(data) # 디버깅용
        return 0

    count = 0
    for card in cards:
        card_data = card.get("data", {})
        if not card_data:
            continue
            
        title = card_data.get("title", "")
        city = card_data.get("city_name", "")
        category = card_data.get("category", "")
        
        # Prices
        price_obj = card_data.get("price", {})
        if not isinstance(price_obj, dict):
            price_obj = {}
        sell_price = price_obj.get("selling_price") or ""
        market_price = price_obj.get("market_price") or ""
        
        # Reviews
        review_obj = card_data.get("review_obj", {})
        if not isinstance(review_obj, dict):
            review_obj = {}
        star = review_obj.get("star", 0)
        review_count_num = review_obj.get("count", 0)
        review_count = f"({review_count_num})" if review_count_num else ""
        
        # Link & Image
        link = card_data.get("deep_link", "")
        image_url = card_data.get("cover_url", "")
        
        # Location
        location = card_data.get("location", "")
        
        cursor.execute('''
            INSERT INTO klook_products (title, city, category, selling_price, market_price, star, review_count, link, image_url, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, city, category, sell_price, market_price, star, review_count, link, image_url, location))
        count += 1
        
    conn.commit()
    return count

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'klook_products.db')
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = init_db(db_path)
    print(f"Database initialized at {db_path}")
    
    total_saved = 0
    # 1페이지~10페이지. start 파라미터는 0, 15, 30 방식이거나 0, 1, 2 방식일 수 있음.
    # 제공된 파일에서 start=2 이므로 0부터 9까지라고 가정. (만약 10페이지면 0~9, 또는 0, 15, 30..)
    # 우선 start=0 부터 9까지 호출. (만약 start가 offset이면 0, 15, 30, ..., 135로 해야함)
    
    # 첫 페이지를 호출해서 offset 방식인지 page 방식인지 확인
    test_data_0 = fetch_klook_data(0)
    test_data_1 = fetch_klook_data(1)
    
    if test_data_0 and test_data_1:
        cards_0 = test_data_0.get("result", {}).get("search_result", {}).get("cards", [])
        cards_1 = test_data_1.get("result", {}).get("search_result", {}).get("cards", [])
        
        # start=1 과 start=0 의 결과가 같거나, start=15 여야 다음 페이지인 경우
        if len(cards_0) > 0 and len(cards_1) > 0:
            if cards_0[0].get("data", {}).get("title") == cards_1[0].get("data", {}).get("title"):
                print("start parameter seems to be offset based (0, 15, 30...) or start=1 is same as 0")
                use_offset = True
            else:
                print("start parameter seems to be page index (0, 1, 2...)")
                use_offset = False
        else:
            use_offset = False
    else:
        use_offset = False
    
    # 실제 수집 루프
    # 만약 offset 기반이라면 0, 15, 30... 
    # 페이지 기반이면 0, 1, 2...
    start_values = [i * 15 for i in range(10)] if use_offset else [i for i in range(10)]
    
    for i, start_val in enumerate(start_values):
        print(f"Fetching page {i + 1} (start={start_val})...")
        data = fetch_klook_data(start_val)
        if data:
            count = parse_and_insert(conn, data)
            total_saved += count
            print(f"Saved {count} items from page {i + 1}.")
        else:
            print(f"No data returned for page {i + 1}.")
        time.sleep(1)
        
    conn.close()
    print(f"Scraping completed. Total {total_saved} items saved to {db_path}.")

if __name__ == "__main__":
    main()
