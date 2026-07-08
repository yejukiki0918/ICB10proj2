"""
klook/src/verify_db.py

수집된 klook_products.db 데이터베이스의 내용을 검증하는 스크립트.
링크, 도시, 가격 등 주요 컬럼이 올바르게 저장되었는지 확인합니다.
작성자: Antigravity
생성일: 2026-06-27
"""

import sqlite3
import os

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'klook_products.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 전체 컬럼 확인
    cursor.execute("PRAGMA table_info(klook_products)")
    columns = cursor.fetchall()
    print("=== 테이블 컬럼 목록 ===")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

    print()

    # 샘플 데이터 5건 출력
    cursor.execute("SELECT id, title, city, selling_price, star, link FROM klook_products LIMIT 5")
    rows = cursor.fetchall()
    print("=== 샘플 데이터 (5건) ===")
    for row in rows:
        print(f"  ID: {row[0]}")
        print(f"  제목: {row[1]}")
        print(f"  도시: {row[2]}")
        print(f"  가격: {row[3]}")
        print(f"  별점: {row[4]}")
        print(f"  링크: {row[5]}")
        print()

    # 링크 채워진 비율 확인
    cursor.execute("SELECT COUNT(*) FROM klook_products")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM klook_products WHERE link != '' AND link IS NOT NULL")
    with_link = cursor.fetchone()[0]

    print(f"=== 링크 통계 ===")
    print(f"  전체 행 수: {total}")
    print(f"  링크 있는 행 수: {with_link}")
    print(f"  링크 없는 행 수: {total - with_link}")

    conn.close()

if __name__ == "__main__":
    main()
