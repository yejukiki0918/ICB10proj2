"""
이 스크립트는 사람인(Saramin) 사이트에서 '마케터' 관련 채용공고를 스크래핑하여 SQLite 데이터베이스에 저장하는 역할을 합니다.
주요 기능:
- 1~10페이지의 채용공고 리스트 수집
- 각 공고의 상세 페이지 데이터 수집
- 데이터베이스에 중복 방지(업데이트) 방식으로 저장
"""
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import json
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'saramin_jobs.db')

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'connection': 'keep-alive',
    'cookie': 'PCID=17554864216358143340984; ab180ClientId=b80ec89c-e9c2-4efe-9cf0-419b3dcc53f7; Mtype=P; saramin_last_login_provider=naver; _ga_DBVYV88LS9csn=VDJ5REsrWGFJVmdnY2RoeTB2YkMvZz09=GS2.1.s1768233669$o1$g0$t1768233669$j60$l0$h0; airbridge_user__saramin=%7B%22externalUserID%22%3A%2213720210%22%2C%22alias%22%3A%7B%22amplitude_id%22%3A%2213720210%22%7D%7D; saramin_login_tab_default=p; AMP_a687efd08d=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJDYVV5bWRudkcyYmpNTzdrYjNtSnJ6JTIyJTJDJTIydXNlcklkJTIyJTNBJTIyMTM3MjAyMTAlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzc2Njg2NDE0MzYyJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc3NjY4NjQxNDM2NCUyQyUyMmxhc3RFdmVudElkJTIyJTNBNCUyQyUyMnBhZ2VDb3VudGVyJTIyJTNBMCU3RA==; HideEditConditionTooltip=y; _ga_DBVYV88LS9=GS2.1.s1777689639$o7$g1$t1777689665$j34$l0$h0; ab.storage.deviceId.a2ac6b71-3416-464a-ac48-ef2cff5c2026=%7B%22g%22%3A%227370b821-d22d-fe39-302a-7f224487414d%22%2C%22c%22%3A1755486553296%2C%22l%22%3A1780316655818%7D; ab.storage.userId.a2ac6b71-3416-464a-ac48-ef2cff5c2026=%7B%22g%22%3A%2213720210%22%2C%22c%22%3A1761491761236%2C%22l%22%3A1780316655819%7D; amp_a687ef=QHmcO52-IXKquDl3xqLIFi.MTM3MjAyMTA=..1jq1i8k5s.1jq1m06gf.h.4j.54; ab.storage.sessionId.a2ac6b71-3416-464a-ac48-ef2cff5c2026=%7B%22g%22%3A%22d162b38d-171e-30ba-53c1-c3b88300379f%22%2C%22e%22%3A1780322373972%2C%22c%22%3A1780316655817%2C%22l%22%3A1780320573972%7D; _ga_L2PN791WR5=GS2.1.s1780317607$o30$g1$t1780320677$j60$l0$h0; _ga_0PN5NFZW7P=GS2.1.s1780317607$o30$g1$t1780320677$j60$l0$h0; PHPSESSID=267la9qosv9ilqac71fma1jg4o2cvpu86tq437o9eqbe0g7alt; _gid=GA1.3.1313774138.1782541454; _gcl_au=1.1.92811635.1782541455; airbridge_migration_metadata__saramin=%7B%22version%22%3A%221.11.12%22%7D; _ga_58W0W855T7=GS2.1.s1782541454$o34$g0$t1782541457$j57$l0$h0; RSRVID=web31|aj9xb|aj9sk; cto_bundle=WjJHC19mUUFGbGdoUkxPdGF0SiUyRlA5elpvb1ZxV3o0dnBGT1ppWjNKTjNvZHdOZWNtSEUzVzFKSTlQVGhPWGVveHJKT054UUlkN3BTUFE0dlVXTDY2QlJ4eFNhS2dmNTRXdSUyQnF5UmZlOFRkViUyRmhZbmhwcGhhWVM0MVpwY1REVVBMQW1ja3QzUTdzdjdDb1pZMWprcldXVDFoTnclM0QlM0Q; _ga=GA1.1.1716532447.1755486523; _ga_GR2XRGQ0FK=GS2.1.s1782541454$o50$g1$t1782542698$j58$l0$h0; _ga_E0LMXXGRZK=GS2.1.s1782541458$o3$g1$t1782542698$j58$l0$h0; airbridge_session__saramin=%7B%22id%22%3A%224ae92da8-8a5a-4825-be09-51176ad077ae%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1782541455375%2C%22end%22%3A1782542698804%7D; _ga_X6JZ0HCBFC=GS2.1.s1782541454$o46$g1$t1782542744$j60$l0$h0',
    'host': 'www.saramin.co.kr',
    'referer': 'https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword=%EB%A7%88%EC%BC%80%ED%84%B0',
    'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
}

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS job_listings (
            job_id TEXT PRIMARY KEY,
            company_name TEXT,
            title TEXT,
            conditions TEXT,
            link TEXT,
            json_data TEXT
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS job_details (
            job_id TEXT PRIMARY KEY,
            detail_html TEXT,
            detail_text TEXT,
            FOREIGN KEY (job_id) REFERENCES job_listings(job_id)
        )
    ''')
    
    # In case the table already exists from previous runs without detail_text
    try:
        cur.execute('ALTER TABLE job_details ADD COLUMN detail_text TEXT')
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    return conn

def scrape_listings(conn):
    cur = conn.cursor()
    jobs = []
    
    for page in range(1, 11):
        print(f"Scraping list page {page}/10...")
        url = f"https://www.saramin.co.kr/zf_user/search/recruit?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword=%EB%A7%88%EC%BC%80%ED%84%B0&recruitPage={page}&recruitSort=relation&recruitPageCount=40&inner_com_type=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&show_applied=&quick_apply=&except_read=&ai_head_hunting="
        
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            item_list = soup.select('.item_recruit')
            
            if not item_list:
                print(f"No more items found on page {page}.")
                break
                
            for item in item_list:
                job_id = item.get('value', '')
                
                corp_elem = item.select_one('.corp_name a')
                company_name = corp_elem.text.strip() if corp_elem else ''
                
                title_elem = item.select_one('.job_tit a')
                title = title_elem.text.strip() if title_elem else ''
                link = "https://www.saramin.co.kr" + title_elem['href'] if title_elem and 'href' in title_elem.attrs else ''
                
                cond_elems = item.select('.job_condition span')
                conditions = " / ".join([c.text.strip() for c in cond_elems])
                
                data_dict = {
                    'job_id': job_id,
                    'company_name': company_name,
                    'title': title,
                    'conditions': conditions,
                    'link': link
                }
                json_data = json.dumps(data_dict, ensure_ascii=False)
                
                if job_id:
                    jobs.append(data_dict)
                    cur.execute('''
                        INSERT OR REPLACE INTO job_listings (job_id, company_name, title, conditions, link, json_data)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (job_id, company_name, title, conditions, link, json_data))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error scraping list page {page}: {e}")
            
        time.sleep(random.uniform(0.1, 1.0))
        
    return jobs

def scrape_details(conn, jobs):
    cur = conn.cursor()
    total = len(jobs)
    
    for i, job in enumerate(jobs, 1):
        job_id = job.get('job_id')
        link = job.get('link')
        
        if not job_id or not link:
            continue
            
        print(f"[{i}/{total}] Scraping details for job_id {job_id}...")
        
        try:
            # 사람인은 실제 모집요강 내용(담당업무, 자격요건 등)을 iframe으로 불러옵니다.
            iframe_url = f"https://www.saramin.co.kr/zf_user/jobs/relay/view-detail?rec_idx={job_id}"
            response = requests.get(iframe_url, headers=HEADERS)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            detail_html = response.text
            soup = BeautifulSoup(detail_html, 'html.parser')
            detail_text = soup.get_text(separator='\n', strip=True)
            
            cur.execute('''
                INSERT OR REPLACE INTO job_details (job_id, detail_html, detail_text)
                VALUES (?, ?, ?)
            ''', (job_id, detail_html, detail_text))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error scraping detail for {job_id}: {e}")
            
        time.sleep(random.uniform(0.1, 1.0))

def main():
    print("Initialize Database...")
    conn = init_db()
    
    print("Start scraping job listings...")
    jobs = scrape_listings(conn)
    print(f"Successfully collected {len(jobs)} job listings.")
    
    print("Start scraping job details...")
    scrape_details(conn, jobs)
    print("Successfully collected job details.")
    
    # CSV로 내보내기 (요구사항 반영)
    print("Exporting data to CSV...")
    query = '''
        SELECT l.job_id, l.company_name, l.title, l.conditions, l.link, d.detail_text, l.json_data
        FROM job_listings l
        LEFT JOIN job_details d ON l.job_id = d.job_id
    '''
    df = pd.read_sql_query(query, conn)
    csv_path = os.path.join(os.path.dirname(DB_PATH), 'saramin_jobs.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"Data successfully exported to {csv_path}")

    conn.close()
    print("All tasks completed.")

if __name__ == "__main__":
    main()
