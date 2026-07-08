"""
klook/src/inspect_page.py

Klook 상세페이지의 실제 HTML 구조를 분석하기 위한 디버깅 스크립트.
Playwright로 페이지를 로드한 후 HTML을 파일로 저장하고,
window.__NEXT_DATA__ 또는 window.__INITIAL_STATE__ 등의 초기 상태 데이터를 추출한다.

작성자: Antigravity
생성일: 2026-06-27
"""

import sys
import os
import json
import time

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# 분석할 URL (1번 상품)
TEST_URL = "https://www.klook.com/ko/activity/96156-everland-ticket-gyeonggi-yongin/"

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(base_dir, "data")

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9",
            },
            viewport={"width": 1440, "height": 900},
        )
        page = context.new_page()

        print(f"접속 중: {TEST_URL}")
        page.goto(TEST_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)

        # 스크롤
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(1)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        html = page.content()

        # HTML 저장
        html_path = os.path.join(out_dir, "debug_detail.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML 저장: {html_path}")

        # ── title 확인 ──────────────────────────────────────────
        soup = BeautifulSoup(html, "lxml")
        print(f"\n<title>: {soup.title.string if soup.title else 'N/A'}")

        # ── h1 확인 ─────────────────────────────────────────────
        h1 = soup.find("h1")
        print(f"<h1>: {h1.get_text(strip=True) if h1 else 'N/A'}")

        # ── meta description ────────────────────────────────────
        meta = soup.find("meta", {"name": "description"})
        if meta:
            print(f"meta description: {meta.get('content', '')[:200]}")

        # ── og:title ────────────────────────────────────────────
        og_title = soup.find("meta", property="og:title")
        if og_title:
            print(f"og:title: {og_title.get('content', '')}")

        # ── og:description ──────────────────────────────────────
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            print(f"og:description: {og_desc.get('content', '')[:200]}")

        # ── JSON-LD 분석 ────────────────────────────────────────
        print("\n=== JSON-LD 스크립트 ===")
        for i, script in enumerate(soup.find_all("script", type="application/ld+json")):
            try:
                ld = json.loads(script.string)
                print(f"[{i}] @type: {ld.get('@type') if isinstance(ld, dict) else 'list'}")
                print(f"     keys: {list(ld.keys()) if isinstance(ld, dict) else '(list)'}")
            except:
                pass

        # ── window.__NEXT_DATA__ 분석 ───────────────────────────
        print("\n=== Next.js __NEXT_DATA__ ===")
        try:
            next_data_raw = page.evaluate("JSON.stringify(window.__NEXT_DATA__)")
            if next_data_raw:
                next_data = json.loads(next_data_raw)
                # 최상위 키만 출력
                print(f"keys: {list(next_data.keys())}")
                if "props" in next_data:
                    props = next_data["props"]
                    print(f"props.keys: {list(props.keys())}")
                    if "pageProps" in props:
                        pp = props["pageProps"]
                        print(f"pageProps.keys: {list(pp.keys())[:20]}")
                        # JSON으로 저장
                        pp_path = os.path.join(out_dir, "debug_next_data.json")
                        with open(pp_path, "w", encoding="utf-8") as f:
                            json.dump(next_data, f, ensure_ascii=False, indent=2)
                        print(f"__NEXT_DATA__ 저장: {pp_path}")
            else:
                print("__NEXT_DATA__ 없음")
        except Exception as e:
            print(f"__NEXT_DATA__ 추출 실패: {e}")

        # ── 실제 사용된 클래스명 샘플 ───────────────────────────
        print("\n=== 페이지 주요 클래스 샘플 ===")
        for tag in ["h1", "h2", "h3", "p", "div"]:
            els = soup.find_all(tag, limit=3)
            for el in els:
                cls = el.get("class")
                text = el.get_text(strip=True)[:60]
                if cls and text:
                    print(f"  <{tag} class='{' '.join(cls)}'> {text}")

        browser.close()

if __name__ == "__main__":
    main()
