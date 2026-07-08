"""
klook/src/scrape_detail.py

klook_products.db에서 상위 10개 상품의 상세페이지 URL(deep_link)을 읽어
Playwright 실제 브라우저로 접근한 뒤, 상세페이지에서 수집 가능한 모든 정보를 추출하여
klook_product_details 테이블에 저장하는 스크립트.

수집 항목:
  - product_id (상품 테이블 FK), url
  - title, subtitle
  - summary_description (요약 설명)
  - full_description (전체 설명 HTML)
  - highlights (하이라이트 목록, JSON)
  - what_to_expect (기대사항, JSON)
  - inclusions (포함 사항, JSON)
  - exclusions (불포함 사항, JSON)
  - know_before_you_go (가기 전 알아야 할 것, JSON)
  - meeting_point (만남 장소)
  - reviews_count (리뷰 수)
  - review_score (리뷰 점수)
  - categories (카테고리)
  - cancellation_policy (취소 정책)
  - raw_html (전체 원본 HTML, 디버깅용)

작성자: Antigravity
생성일: 2026-06-27
"""

import sqlite3
import json
import os
import sys
import time

# Windows cp949 환경에서 한글/유니코드 출력이 깨지지 않도록 stdout을 UTF-8로 설정
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup



# ─────────────────────────────────────────────────────────────
# 데이터베이스 초기화
# ─────────────────────────────────────────────────────────────
def init_detail_table(conn):
    """상세페이지 테이블 생성 (없으면 생성, 있으면 유지)."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS klook_product_details (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id          INTEGER,
            url                 TEXT,
            title               TEXT,
            subtitle            TEXT,
            summary_description TEXT,
            full_description    TEXT,
            highlights          TEXT,  -- JSON 배열
            what_to_expect      TEXT,  -- JSON 배열
            inclusions          TEXT,  -- JSON 배열
            exclusions          TEXT,  -- JSON 배열
            know_before_you_go  TEXT,  -- JSON 배열
            meeting_point       TEXT,
            reviews_count       TEXT,
            review_score        TEXT,
            categories          TEXT,
            cancellation_policy TEXT,
            opening_hours       TEXT,
            raw_html            TEXT,
            scraped_at          TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES klook_products(id)
        )
    """)
    conn.commit()


# ─────────────────────────────────────────────────────────────
# 상위 10개 상품의 ID·URL 조회
# ─────────────────────────────────────────────────────────────
def get_top_products(conn, limit=10):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, link FROM klook_products WHERE link != '' AND link IS NOT NULL LIMIT ?",
        (limit,)
    )
    return cursor.fetchall()


# ─────────────────────────────────────────────────────────────
# HTML 파싱 → 정보 추출
# ─────────────────────────────────────────────────────────────
def parse_detail_page(html: str, url: str) -> dict:
    """BeautifulSoup으로 상세페이지 HTML을 파싱하여 정보를 추출한다."""
    soup = BeautifulSoup(html, "lxml")

    def text(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else ""

    def texts(selector):
        return [el.get_text(strip=True) for el in soup.select(selector) if el.get_text(strip=True)]

    # ── 제목 ──────────────────────────────────────────────────
    title = (
        text("h1.activity-name") or
        text("h1[class*='title']") or
        text("h1") or
        text("title")
    )

    # ── 부제목 ────────────────────────────────────────────────
    subtitle = text("[class*='subtitle']") or text("[class*='sub-title']")

    # ── 요약 설명 ──────────────────────────────────────────────
    summary_description = (
        text("[class*='summary']") or
        text("[class*='brief']") or
        text('meta[name="description"]')
    )
    if not summary_description:
        meta = soup.find("meta", {"name": "description"})
        if meta:
            summary_description = meta.get("content", "")

    # ── 전체 설명 (HTML 유지) ──────────────────────────────────
    desc_el = (
        soup.select_one("[class*='activity-desc']") or
        soup.select_one("[class*='description']") or
        soup.select_one("[class*='content-body']")
    )
    full_description = str(desc_el) if desc_el else ""

    # ── 하이라이트 ─────────────────────────────────────────────
    highlights = (
        texts("[class*='highlight'] li") or
        texts("[class*='highlights'] li") or
        texts("[class*='feature'] li")
    )

    # ── what to expect ────────────────────────────────────────
    what_to_expect = texts("[class*='itinerary'] li") or texts("[class*='schedule'] li")

    # ── 포함 / 불포함 ──────────────────────────────────────────
    inclusions = texts("[class*='inclusion'] li") or texts("[class*='include'] li")
    exclusions = texts("[class*='exclusion'] li") or texts("[class*='exclude'] li")

    # ── 가기 전 알아야 할 것 ──────────────────────────────────
    know_before = texts("[class*='know-before'] li") or texts("[class*='important'] li")

    # ── 만남 장소 ──────────────────────────────────────────────
    meeting_point = (
        text("[class*='meeting-point']") or
        text("[class*='meetup']") or
        text("[class*='departure']")
    )

    # ── 리뷰 ──────────────────────────────────────────────────
    review_score = (
        text("[class*='review-score']") or
        text("[class*='rating-score']") or
        text("[class*='score']")
    )
    reviews_count = (
        text("[class*='review-count']") or
        text("[class*='review-total']") or
        text("[class*='reviewCount']")
    )

    # ── 카테고리 ──────────────────────────────────────────────
    categories = " > ".join(texts("[class*='breadcrumb'] a") or texts("nav a"))

    # ── 취소 정책 ──────────────────────────────────────────────
    cancellation_policy = (
        text("[class*='cancel']") or
        text("[class*='refund']")
    )

    # ── 영업시간 ──────────────────────────────────────────────
    opening_hours = text("[class*='opening-hours']") or text("[class*='open-hour']")

    # ── JSON-LD 구조화 데이터에서 추가 정보 추출 ──────────────
    for script_tag in soup.find_all("script", type="application/ld+json"):
        try:
            ld = json.loads(script_tag.string)
            items = ld if isinstance(ld, list) else [ld]
            for item in items:
                if item.get("@type") in ("TouristAttraction", "Event", "Product", "TouristTrip"):
                    if not title:
                        title = item.get("name", "")
                    if not summary_description:
                        summary_description = item.get("description", "")
                    if not review_score:
                        agg = item.get("aggregateRating", {})
                        review_score = str(agg.get("ratingValue", ""))
                        reviews_count = str(agg.get("reviewCount", ""))
        except Exception:
            pass

    # ── Open Graph에서 이미지 및 설명 보완 ──────────────────
    if not summary_description:
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            summary_description = og_desc.get("content", "")

    return {
        "url": url,
        "title": title,
        "subtitle": subtitle,
        "summary_description": summary_description,
        "full_description": full_description,
        "highlights": json.dumps(highlights, ensure_ascii=False),
        "what_to_expect": json.dumps(what_to_expect, ensure_ascii=False),
        "inclusions": json.dumps(inclusions, ensure_ascii=False),
        "exclusions": json.dumps(exclusions, ensure_ascii=False),
        "know_before_you_go": json.dumps(know_before, ensure_ascii=False),
        "meeting_point": meeting_point,
        "reviews_count": reviews_count,
        "review_score": review_score,
        "categories": categories,
        "cancellation_policy": cancellation_policy,
        "opening_hours": opening_hours,
    }


# ─────────────────────────────────────────────────────────────
# 상세페이지 저장
# ─────────────────────────────────────────────────────────────
def insert_detail(conn, product_id: int, data: dict, raw_html: str):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO klook_product_details
          (product_id, url, title, subtitle, summary_description, full_description,
           highlights, what_to_expect, inclusions, exclusions, know_before_you_go,
           meeting_point, reviews_count, review_score, categories,
           cancellation_policy, opening_hours, raw_html)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        product_id,
        data["url"],
        data["title"],
        data["subtitle"],
        data["summary_description"],
        data["full_description"],
        data["highlights"],
        data["what_to_expect"],
        data["inclusions"],
        data["exclusions"],
        data["know_before_you_go"],
        data["meeting_point"],
        data["reviews_count"],
        data["review_score"],
        data["categories"],
        data["cancellation_policy"],
        data["opening_hours"],
        raw_html,
    ))
    conn.commit()


# ─────────────────────────────────────────────────────────────
# 조인 쿼리 결과 출력
# ─────────────────────────────────────────────────────────────
def print_join_result(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            p.id AS product_id,
            p.title AS product_title,
            p.city,
            p.selling_price,
            p.star,
            p.review_count,
            d.id AS detail_id,
            d.summary_description,
            d.highlights,
            d.inclusions,
            d.review_score AS detail_review_score,
            d.reviews_count AS detail_reviews_count,
            d.cancellation_policy,
            d.url
        FROM klook_products p
        JOIN klook_product_details d ON p.id = d.product_id
        ORDER BY p.id
    """)
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]

    print("\n" + "=" * 80)
    print("=== 상품 + 상세페이지 조인 결과 ===")
    print("=" * 80)
    for row in rows:
        row_dict = dict(zip(col_names, row))
        print(f"\n[상품 ID: {row_dict['product_id']}] {row_dict['product_title']}")
        print(f"  도시: {row_dict['city']}")
        print(f"  가격: {row_dict['selling_price']}")
        print(f"  별점(목록): {row_dict['star']}  리뷰수(목록): {row_dict['review_count']}")
        print(f"  별점(상세): {row_dict['detail_review_score']}  리뷰수(상세): {row_dict['detail_reviews_count']}")
        print(f"  요약 설명: {(row_dict['summary_description'] or '')[:100]}...")
        print(f"  취소정책: {(row_dict['cancellation_policy'] or '')[:80]}")
        print(f"  URL: {row_dict['url']}")


# ─────────────────────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────────────────────
def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "klook_products.db")

    conn = sqlite3.connect(db_path)
    init_detail_table(conn)

    products = get_top_products(conn, limit=10)
    print(f"수집 대상: {len(products)}개 상품")

    with sync_playwright() as pw:
        # 실제 브라우저처럼 보이도록 설정
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/149.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "upgrade-insecure-requests": "1",
            },
            viewport={"width": 1440, "height": 900},
        )
        page = context.new_page()

        for product_id, product_title, url in products:
            print(f"\n  [{product_id}] 접근 중: {url}")
            try:
                # 페이지 로드 (최대 30초 대기, 네트워크 유휴 상태 기준)
                page.goto(url, wait_until="networkidle", timeout=30000)
                time.sleep(2)  # JS 렌더링 여유 시간

                # 스크롤을 내려 lazy-load 콘텐츠 로드
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                time.sleep(1)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

                html = page.content()
                data = parse_detail_page(html, url)
                insert_detail(conn, product_id, data, html)

                print(f"  [OK] 저장 완료: {data['title'][:50]}")
                print(f"    요약: {(data['summary_description'] or '')[:80]}...")
                print(f"    취소정책: {(data['cancellation_policy'] or '')[:60]}")

            except Exception as e:
                print(f"  [FAIL] 실패: {e}")

            time.sleep(2)  # 요청 간격 (봇 탐지 회피)

        browser.close()

    print("\n\n" + "=" * 60)
    print("모든 상세페이지 수집 완료!")
    print_join_result(conn)
    conn.close()


if __name__ == "__main__":
    main()
