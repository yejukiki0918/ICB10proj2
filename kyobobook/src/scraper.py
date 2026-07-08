"""
교보문고 베스트셀러 목록을 스크래핑하는 스크립트입니다.
지정된 프롬프트의 HTTP 요청 정보를 사용하여 1페이지부터 마지막 페이지까지 전체 데이터를 수집하고,
그 결과를 csv 파일로 저장합니다.
"""

import requests
import pandas as pd
import json
import os
import time

def scrape_kyobobook_bestseller():
    url = "https://store.kyobobook.co.kr/api/gw/best/v2/best-seller/online"
    
    headers = {
        "host": "store.kyobobook.co.kr",
        "referer": "https://store.kyobobook.co.kr/category/domestic/33/best?page=1&per=50",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "x-api-gw-key": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..i35xkkCOngvXqCRx.0CqToQel6sj5d0qOS2ftoDu37jRwb0vtQwMBd1e_G1ynl7KUrTrH_qPJnygVpkc0tExt4BUX_pJ4RepB5QsxWmKLjC8tEuMELKG8SvRLEVn6ambMnSmDaJ85mLbGtHcM-zFiDBzi.3y1-RnxGHFxeLNMK2dWZoQ"
    }

    all_best_sellers = []
    page = 1

    while True:
        print(f"{page}페이지 수집 중...")
        params = {
            "page": str(page),
            "per": "50",
            "saleCmdtClstCode": "33",
            "soldOutExcludeYn": "N",
            "saleCmdtDsplDvsnCode": "KOR",
            "period": "002",
            "dsplDvsnCode": "001",
            "dsplTrgtDvsnCode": "004"
        }

        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            best_sellers = data.get("data", {}).get("bestSeller", [])
            
            if not best_sellers:
                print("더 이상 데이터가 없습니다. 수집을 종료합니다.")
                break
                
            all_best_sellers.extend(best_sellers)
            
            # 교보문고는 보통 1000위(20페이지)까지 제공하는 경우가 많습니다.
            # 하지만 응답에 다음 페이지가 없으면 bestSeller가 빈 리스트로 옵니다.
            page += 1
            time.sleep(1) # 서버에 부담을 주지 않기 위해 지연
        else:
            print(f"요청 실패: {response.status_code}")
            print(response.text)
            break

    if all_best_sellers:
        df = pd.json_normalize(all_best_sellers)
        
        # 워크스페이스 기준 상대 경로 (kyobobook/data) 사용
        output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "bestseller.csv")
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"총 {len(df)}건의 데이터 수집 성공. 저장 위치: {output_file}")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    scrape_kyobobook_bestseller()
