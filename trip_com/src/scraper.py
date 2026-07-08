"""
Trip.com 호텔 리뷰 스크래핑 및 SQLite 저장 스크립트
작성자: Antigravity
작성일: 2026-06-22

이 스크립트는 trip.com의 특정 호텔 리뷰를 scrapling을 사용해 수집하고,
결과를 trip_com/data/reviews.db 의 reviews 테이블에 저장합니다.
"""

import json
import sqlite3
import os
import time
from scrapling import Fetcher

def setup_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            rating REAL,
            create_date TEXT,
            checkin_date TEXT
        )
    ''')
    conn.commit()
    return conn

def fetch_reviews():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'reviews.db')
    conn = setup_db(db_path)
    cursor = conn.cursor()

    url = "https://kr.trip.com/restapi/soa2/34308/getHotelCommentInfo"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "w-payload-source": "1.0.9@102!Nudtz1KLhCAbOX4SO6An9PKnG2KLOSqZOlbn+6FaG6OaKSbpKET2OSVbOrK2+ET5+rApbbbpOSknKr42+rG2KlqIbEVbKtb5+rbSOEb2KE4p+rKpOr4nKrq/K5bpOSqL+rk/OSKZKrVpQlVROShDKFO3GVd3hbb=",
        "x-ctx-country": "KR",
        "x-ctx-currency": "KRW",
        "x-ctx-locale": "ko-KR",
        "x-ctx-ubt-pageid": "10320668147",
        "x-ctx-ubt-pvid": "7",
        "x-ctx-ubt-sid": "9",
        "x-ctx-ubt-vid": "1754985737191.9877n1SlbHlt",
        "x-ctx-user-recognize": "NON_EU",
        "x-ctx-wclient-req": "0af33fe7acb74bcfe9f82cf404544b46"
    }
    
    fetcher = Fetcher()
    page_index = 1
    page_size = 10
    total_saved = 0

    print("리뷰 수집을 시작합니다...")
    while True:
        payload = {
            "hotelId": 58635410,
            "commentFilterOptions": {
                "pageIndex": page_index,
                "pageSize": page_size,
                "repeatComment": 1
            },
            "sceneTypes": ["CommentList"],
            "head": {
                "platform": "PC",
                "cver": "0",
                "cid": "1754985737191.9877n1SlbHlt",
                "bu": "IBU",
                "group": "trip",
                "aid": "",
                "sid": "",
                "ouid": "",
                "locale": "ko-KR",
                "timezone": "9",
                "currency": "KRW",
                "pageId": "10320668147",
                "vid": "1754985737191.9877n1SlbHlt",
                "guid": "",
                "isSSR": False
            }
        }
        
        try:
            response = fetcher.post(url, headers=headers, json=payload)
            if response.status != 200:
                print(f"Error: API 응답 코드가 {response.status}입니다. 수집을 중단합니다.")
                break

            data = response.json()
            group_list = data.get('data', {}).get('groupList', [])
            
            if not group_list:
                break
                
            comments = group_list[0].get('commentList', [])
            if not comments:
                break

            for c in comments:
                review_id = str(c.get('id', ''))
                title = c.get('title') or c.get('subject') or ''
                content = c.get('content', '')
                rating = float(c.get('rating', 0.0))
                create_date = c.get('createDate', '')
                checkin_date = c.get('checkinDate', '')

                cursor.execute('''
                    INSERT OR REPLACE INTO reviews (id, title, content, rating, create_date, checkin_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (review_id, title, content, rating, create_date, checkin_date))
            
            conn.commit()
            total_saved += len(comments)
            print(f"{page_index}페이지 수집 완료 ({len(comments)}개 저장, 누적 {total_saved}개)")
            
            # 다음 페이지를 위해 page_index 증가 및 약간의 대기시간
            page_index += 1
            time.sleep(1)

        except Exception as e:
            print(f"수집 중 오류 발생: {e}")
            break

    conn.close()
    print("모든 리뷰 수집 및 DB 저장이 완료되었습니다.")

if __name__ == "__main__":
    fetch_reviews()
