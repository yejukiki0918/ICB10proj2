"""
Klook 상위 10개 상품의 상세페이지 deep link를 통해 상세 설명, 평점, 리뷰 개수 및
패키지 옵션 목록을 수집하여 klook_product_details 테이블에 저장하는 크롤링 프로그램입니다.
"""
import os
import re
import time
import random
import sqlite3
import json
from scrapling import Fetcher

DB_PATH = "klook/data/klook_products.db"

def init_detail_table():
    """
    상세페이지 정보를 저장할 테이블을 초기화합니다.
    새로운 수집을 위해 기존 테이블이 존재할 경우 삭제 후 새로 생성합니다.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 기존 테이블 삭제 (초기화)
    cursor.execute("DROP TABLE IF EXISTS klook_product_details")
    
    # 테이블 생성
    cursor.execute("""
        CREATE TABLE klook_product_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            activity_id TEXT,
            overview TEXT,
            description TEXT,
            options_json TEXT,
            score REAL,
            review_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES klook_products(id)
        )
    """)
    conn.commit()
    conn.close()
    print("klook_product_details 테이블 초기화 완료.")

def fetch_package_options(fetcher, activity_id):
    """
    activity_id를 기반으로 패키지 옵션 API를 직접 호출하여 옵션 목록을 수집합니다.
    """
    url = f"https://www.klook.com/v1/experiencesrv/product/page_service/get_spu_list_section"
    params = {
        "activity_id": str(activity_id),
        "preview": "",
        "translation": "",
        "partner_type": "",
        "from_b": "",
        "sales_channel": "customer"
    }
    
    try:
        response = fetcher.get(url, params=params, impersonate='chrome120')
        if response.status == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("result", {})
                spu_group_info = result.get("spu_group_info", [])
                
                packages = []
                for group in spu_group_info:
                    for spu in group.get("spu_list", []):
                        packages.append({
                            "group_name": group.get("name"),
                            "name": spu.get("spu_name"),
                            "desc": spu.get("spu_desc")
                        })
                return packages
    except Exception as e:
        print(f"  [패키지 옵션 수집 실패] activity_id {activity_id}: {e}")
    return []

def main():
    # 테이블 초기화
    init_detail_table()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 상위 10개 상품 데이터 가져오기
    cursor.execute("SELECT id, title, deep_link FROM klook_products ORDER BY id ASC LIMIT 10")
    products = cursor.fetchall()
    
    fetcher = Fetcher()
    
    print(f"상위 {len(products)}개 상품 상세페이지 수집 시작...")
    
    for product_id, title, deep_link in products:
        print(f"\n[상품 ID {product_id}] {title} 수집 중...")
        print(f"  Deep Link: {deep_link}")
        
        try:
            # WAF 우회를 위해 headers를 비우고 impersonate만 적용
            response = fetcher.get(deep_link, impersonate='chrome120')
            
            if response.status != 200:
                print(f"  [에러] 상세페이지 요청 실패 (HTTP {response.status})")
                continue
                
            html = response.html_content
            
            # window.__KLOOK__ 정규식 파싱
            match = re.search(r'window\.__KLOOK__\s*=\s*(\{.*?\});\s*\(function', html)
            if not match:
                print("  [에러] window.__KLOOK__ 데이터를 찾을 수 없습니다.")
                continue
                
            data = json.loads(match.group(1))
            
            # 상세 데이터 경로 탐색
            activity_detail = data.get("state", {}).get("traveller", {}).get("activity", {}).get("activityDetail", {})
            basic_data = activity_detail.get("basic_data", {})
            seo = basic_data.get("seo", {})
            source = activity_detail.get("source", {})
            
            # activity_id 획득
            activity_id = basic_data.get("activity_id")
            if not activity_id:
                # aggregate_id 시도
                activity_id = basic_data.get("aggregate_id")
                
            if not activity_id:
                print("  [에러] activity_id를 찾을 수 없습니다.")
                continue
                
            print(f"  Activity ID: {activity_id}")
            
            # 상세설명 및 SEO설명
            overview = seo.get("overview")
            description = seo.get("description")
            
            # 평점 및 리뷰 개수 수집
            score = seo.get("score")
            review_count = seo.get("review_count")
            
            # seo 데이터에 없는 경우 score_participants 데이터 참조
            score_data = source.get("v2_activity_score_participants", {}).get("data", {})
            if score_data:
                if score is None:
                    score = score_data.get("score")
                if review_count is None:
                    review_count = score_data.get("review_count")
                    
            print(f"  평점: {score}, 리뷰 개수: {review_count}")
            
            # 패키지 옵션 리스트 API 수집
            print("  패키지 옵션 수집 중...")
            packages = fetch_package_options(fetcher, activity_id)
            options_json = json.dumps(packages, ensure_ascii=False)
            print(f"  수집된 패키지 옵션 수: {len(packages)}")
            
            # DB 저장
            cursor.execute("""
                INSERT INTO klook_product_details (
                    product_id, activity_id, overview, description, options_json, score, review_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_id, str(activity_id), overview, description, options_json, score, review_count))
            conn.commit()
            print(f"  [성공] DB 저장 완료")
            
            # 딜레이 적용
            delay = random.uniform(1.0, 2.5)
            time.sleep(delay)
            
        except Exception as e:
            print(f"  [예외 발생] 수집 중 오류: {e}")
            
    conn.close()
    print("\n상위 10개 상품 상세 수집 완료!")

if __name__ == "__main__":
    main()
