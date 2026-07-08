"""
klook/src/test_request.py

requests로 Klook 상세페이지를 직접 가져와 실제 HTML 구조를 분석하는 스크립트.
__NEXT_DATA__, meta 태그, JSON-LD 등에서 데이터 추출 가능성을 확인한다.

작성자: Antigravity
생성일: 2026-06-27
"""
import sys
import os
import re
import json
import requests

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(base_dir, "data")

act_id = "96156"
url = f"https://www.klook.com/ko/activity/{act_id}-everland-ticket-gyeonggi-yongin/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "Upgrade-Insecure-Requests": "1",
}

r = requests.get(url, headers=headers, timeout=20)
print("status:", r.status_code)
print("content-type:", r.headers.get("content-type"))
print("len:", len(r.text))

# HTML 저장
html_path = os.path.join(out_dir, "debug_requests.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(r.text)
print(f"HTML 저장: {html_path}")

# title
title_m = re.search(r"<title[^>]*>([^<]+)</title>", r.text)
if title_m:
    print("title:", title_m.group(1).strip()[:120])

# meta description
meta_m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', r.text, re.IGNORECASE)
if meta_m:
    print("meta desc:", meta_m.group(1)[:200])

# og:title
og_title_m = re.search(r'property=["\']og:title["\']\s+content=["\'](.*?)["\']', r.text, re.IGNORECASE)
if og_title_m:
    print("og:title:", og_title_m.group(1)[:150])

# og:description
og_desc_m = re.search(r'property=["\']og:description["\']\s+content=["\'](.*?)["\']', r.text, re.IGNORECASE)
if og_desc_m:
    print("og:description:", og_desc_m.group(1)[:200])

# __NEXT_DATA__
next_m = re.search(r'id="__NEXT_DATA__"[^>]*>(.+?)</script>', r.text, re.DOTALL)
if next_m:
    raw = next_m.group(1).strip()
    print(f"__NEXT_DATA__ 발견! 길이={len(raw)}")
    try:
        nd = json.loads(raw)
        next_path = os.path.join(out_dir, "debug_next_data.json")
        with open(next_path, "w", encoding="utf-8") as f:
            json.dump(nd, f, ensure_ascii=False, indent=2)
        print(f"저장: {next_path}")
        # 상위 키 출력
        print("keys:", list(nd.keys()))
        if "props" in nd:
            pp = nd.get("props", {}).get("pageProps", {})
            print("pageProps.keys:", list(pp.keys())[:20])
    except Exception as e:
        print("파싱 실패:", e)
else:
    print("__NEXT_DATA__ 없음 - 봇 탐지 차단 가능성")
    # 서버 응답 처음 500자 출력
    print("\n--- HTML 앞부분 ---")
    print(r.text[:500])
