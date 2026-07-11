"""
SQLite 데이터베이스 빌드 스크립트
작성자: Antigravity
주요 기능:
- 대용량 파켓(Parquet) 데이터를 읽어 효율적인 조회용 집계(Aggregation) 테이블을 생성
- SQLite 파일(dashboard.db)로 저장
"""

import pandas as pd
import sqlite3
import os

# --- Paths ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PARQUET_PATH = os.path.join(DATA_DIR, "LOCAL_PEOPLE_DONG_202606_tidy.parquet")
EXCEL_PATH = os.path.join(DATA_DIR, "행정동코드_매핑정보_20241218.xlsx")
DB_PATH = os.path.join(DATA_DIR, "dashboard.db")

def build_db():
    print("1. 데이터 로드 시작...")
    df_dong = pd.read_excel(EXCEL_PATH)
    df = pd.read_parquet(PARQUET_PATH)
    
    print("2. 데이터 조인 및 전처리...")
    df_dong_map = df_dong[['행자부행정동코드', '시군구명', '행정동명']].drop_duplicates()
    df_dong_map['행자부행정동코드'] = pd.to_numeric(df_dong_map['행자부행정동코드'], errors='coerce')
    df_dong_map = df_dong_map.dropna(subset=['행자부행정동코드'])
    df_dong_map['행자부행정동코드'] = df_dong_map['행자부행정동코드'].astype(int)
    
    df = pd.merge(df, df_dong_map, left_on='행정동코드', right_on='행자부행정동코드', how='left')
    df['시군구명'] = df['시군구명'].fillna('알수없음')
    df['행정동명'] = df['행정동명'].fillna('알수없음')
    
    print("3. 사전 집계(Pre-aggregation) 테이블 생성...")
    # (1) 구 단위 마스터 집계 (필터용 차원 모두 포함)
    # 30일 * 24시간 * 25구 * 14연령 * 2성별 = 약 50만건 내외
    agg_gu = df.groupby(['기준일ID', '시간대구분', '시군구명', '연령대', '성별'])['인구수'].sum().reset_index()
    
    # (2) 동 단위 지도 시각화 전용 집계 (연령/성별 제외하여 용량 압축)
    # 30일 * 24시간 * 425동 = 약 30만건
    agg_dong = df.groupby(['기준일ID', '시간대구분', '시군구명', '행정동명'])['인구수'].sum().reset_index()
    
    print("4. SQLite DB 저장...")
    # 파일이 존재하면 삭제 (초기화)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    agg_gu.to_sql('agg_gu', conn, index=False, if_exists='replace')
    agg_dong.to_sql('agg_dong', conn, index=False, if_exists='replace')
    
    # 원본 미리보기를 위한 샘플 데이터(1,000건) 저장
    df.head(1000).to_sql('sample_raw', conn, index=False, if_exists='replace')
    
    # 인덱스 생성으로 쿼리 속도 최적화
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX idx_gu ON agg_gu(기준일ID, 시간대구분, 시군구명);")
    cursor.execute("CREATE INDEX idx_dong ON agg_dong(기준일ID, 시간대구분);")
    conn.commit()
    conn.close()
    
    print("✅ 성공적으로 DB 생성을 완료했습니다:", DB_PATH)

if __name__ == "__main__":
    build_db()
