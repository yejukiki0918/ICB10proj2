"""
Klook 제품 정보 수집 스크립트
작성자: Antigravity
생성일: 2026-06-24
설명: Klook 검색 API를 호출하여 제품 정보(제목, 가격, 카테고리, 리뷰 등)를 수집하고, 결과를 klook/data 폴더에 CSV 파일로 저장합니다.
"""

import requests
import pandas as pd
import json

def fetch_klook_data():
    url = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3?location=158%2C157%2C156%2C20544%2C25723%2C5031%2C8928%2C24975%2C28741%2C545%2C6166%2C6268%2C703649%2C703648%2C705582%2C6955%2C15088%2C701102%2C16467%2C707516%2C26374%2C7204%2C20296%2C28785%2C28972%2C8898%2C23546%2C30633%2C15378%2C16365%2C28742%2C10956%2C26961%2C10093%2C16560%2C25178%2C7741%2C11925%2C24865%2C25140%2C30570%2C7030%2C707332%2C7558%2C8989%2C10706%2C11364%2C11745%2C13523%2C14446%2C15281%2C15603%2C16655%2C18214%2C18323%2C20392%2C22390%2C22675%2C23237%2C24520%2C24762%2C25060%2C26454%2C27895%2C29136%2C29872%2C30051%2C30265%2C30376%2C30466%2C31247%2C705101%2C9079&sort=most_relevant&tab_key=0&start=2&query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&size=15&search_scope=main_search&k_lang=ko_KR&k_currency=KRW"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ko_KR",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "x-klook-market": "global",
        "x-platform": "desktop",
        "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&search_scope=main_search"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        cards = data.get("result", {}).get("search_result", {}).get("cards", [])
        
        products = []
        for card in cards:
            card_data = card.get("data", {})
            
            title = card_data.get("title")
            city_name = card_data.get("city_name")
            category = card_data.get("category")
            
            price_info = card_data.get("price", {})
            selling_price = price_info.get("selling_price")
            market_price = price_info.get("market_price")
            
            review_info = card_data.get("review_obj", {}) or {}
            star = review_info.get("star")
            review_count = review_info.get("number")
            
            deep_link = card_data.get("deep_link")
            cover_url = card_data.get("cover_url")
            location = card_data.get("location")
            
            products.append({
                "Title": title,
                "City": city_name,
                "Category": category,
                "Selling Price": selling_price,
                "Market Price": market_price,
                "Star": star,
                "Review Count": review_count,
                "Link": deep_link,
                "Image URL": cover_url,
                "Location": location
            })
            
        return products
    except Exception as e:
        print(f"데이터 수집 중 오류 발생: {e}")
        return []

if __name__ == "__main__":
    print("Klook 데이터 수집을 시작합니다...")
    products = fetch_klook_data()
    
    if products:
        df = pd.DataFrame(products)
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "..", "data", "klook_products.csv")
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"데이터 수집 완료! 총 {len(products)}개의 제품이 {output_path}에 저장되었습니다.")
    else:
        print("수집된 데이터가 없습니다.")
