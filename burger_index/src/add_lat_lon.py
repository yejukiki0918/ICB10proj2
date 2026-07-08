"""
burger.csv에서 각 지역(시도시군구명)별 위도와 경도의 중간값(median)을 구한 후,
이를 버거지수가 포함된 region_brand_crosstab.csv에 파생변수로 추가하는 스크립트.
"""
import os
import pandas as pd

def main():
    burger_path = os.path.join("burger_index", "data", "burger.csv")
    crosstab_path = os.path.join("burger_index", "data", "region_brand_crosstab.csv")
    
    # 1. 원본 burger.csv 로드
    df_burger = pd.read_csv(burger_path, encoding='utf-8')
    
    # 시도명, 시군구명 컬럼 찾기 (정확한 매핑을 위해 부분 일치 사용)
    sido_col = [c for c in df_burger.columns if '시도명' in c][0]
    sigungu_col = [c for c in df_burger.columns if '시군구명' in c][0]
    lon_col = [c for c in df_burger.columns if '경도' in c][0]
    lat_col = [c for c in df_burger.columns if '위도' in c][0]
    
    # 시도시군구명 생성
    df_burger['시도시군구명'] = df_burger[sido_col].astype(str).str.strip() + ' ' + df_burger[sigungu_col].astype(str).str.strip()
    
    # 지역별 위도/경도의 중간값(median) 계산
    # 경도와 위도를 숫자로 변환 (오류 시 NaN 처리)
    df_burger[lon_col] = pd.to_numeric(df_burger[lon_col], errors='coerce')
    df_burger[lat_col] = pd.to_numeric(df_burger[lat_col], errors='coerce')
    
    # 중앙값 도출
    grouped_loc = df_burger.groupby('시도시군구명')[[lat_col, lon_col]].median().reset_index()
    grouped_loc.rename(columns={lat_col: '중앙_위도', lon_col: '중앙_경도'}, inplace=True)
    
    # 2. 기존 region_brand_crosstab.csv 로드
    df_crosstab = pd.read_csv(crosstab_path, index_col=0, encoding='utf-8-sig')
    
    # 3. 데이터 병합 (Merge)
    # df_crosstab의 인덱스가 시도시군구명이므로, 인덱스 기준으로 병합
    df_merged = df_crosstab.merge(grouped_loc, left_index=True, right_on='시도시군구명', how='left')
    
    # 시도시군구명을 다시 인덱스로 설정
    df_merged.set_index('시도시군구명', inplace=True)
    
    # 기존에 총합 행/열 처리가 있었으면 유지하되, 정렬 기준이 되는 버거지수가 있는지 확인
    # 컬럼 순서 재배치: 중앙_위도와 중앙_경도를 버거지수 옆에 위치시킴
    cols = list(df_merged.columns)
    if '버거지수' in cols:
        cols.remove('중앙_위도')
        cols.remove('중앙_경도')
        idx = cols.index('버거지수') + 1
        cols.insert(idx, '중앙_위도')
        cols.insert(idx + 1, '중앙_경도')
        df_merged = df_merged[cols]
    
    # 4. 결과 저장 (덮어쓰기)
    df_merged.to_csv(crosstab_path, encoding='utf-8-sig')
    
    # 확인용으로 burger_index 파일도 동일하게 업데이트
    idx_path = os.path.join("burger_index", "data", "region_burger_index.csv")
    df_merged.to_csv(idx_path, encoding='utf-8-sig')
    
    print(f"위도/경도 중간값이 성공적으로 추가되어 {crosstab_path}에 저장되었습니다.")
    print("\n[ 결과 데이터 미리보기 ]")
    preview_cols = ['버거지수', '중앙_위도', '중앙_경도']
    print(df_merged[preview_cols].head())

if __name__ == "__main__":
    main()
