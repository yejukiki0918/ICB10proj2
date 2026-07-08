"""
klook/src/inspect_stealth.py

playwright-stealth을 사용해 Cloudflare 봇 탐지를 우회하고
Klook 상세페이지의 __NEXT_DATA__ JSON에서 실제 데이터를 추출하는 테스트 스크립트.

작성자: Antigravity
생성일: 2026-06-27
"""
import sys
import os
import re
import json
import time

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(base_dir, "data")

TEST_URL = "https://www.klook.com/ko/activity/96156-everland-ticket-gyeonggi-yongin/"

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={"width": 1440, "height": 900},
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9",
                "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            },
        )
        page = context.new_page()

        # Stealth 적용 (봇 탐지 우회)
        stealth_sync(page)

        print(f"접속 중: {TEST_URL}")
        page.goto(TEST_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        html = page.content()
        print(f"HTML 길이: {len(html)}")

        # title 확인
        title_m = re.search(r"<title[^>]*>([^<]+)</title>", html)
        if title_m:
            print(f"title: {title_m.group(1).strip()}")

        # meta description
        meta_m = re.search(r'name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
        if meta_m:
            print(f"meta desc: {meta_m.group(1)[:200]}")

        # __NEXT_DATA__ 확인
        next_m = re.search(r'id="__NEXT_DATA__"[^>]*>(.+?)</script>', html, re.DOTALL)
        if next_m:
            raw = next_m.group(1).strip()
            print(f"__NEXT_DATA__ 발견! 길이={len(raw)}")
            try:
                nd = json.loads(raw)
                next_path = os.path.join(out_dir, "debug_next_data.json")
                with open(next_path, "w", encoding="utf-8") as f:
                    json.dump(nd, f, ensure_ascii=False, indent=2)
                print(f"저장: {next_path}")
                print("keys:", list(nd.keys()))
                pp = nd.get("props", {}).get("pageProps", {})
                if pp:
                    print("pageProps.keys:", list(pp.keys())[:20])
            except Exception as e:
                print(f"파싱 실패: {e}")
        else:
            print("__NEXT_DATA__ 없음")

        # cloudflare challenge 여부
        if "cf-chl" in html.lower() or "enable js" in html.lower() or len(html) < 2000:
            print("경고: Cloudflare 챌린지 또는 봇 차단 감지됨")

        # HTML 저장
        html_path = os.path.join(out_dir, "debug_stealth.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML 저장: {html_path}")

        browser.close()

if __name__ == "__main__":
    main()
