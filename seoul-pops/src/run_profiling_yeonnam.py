"""
연남동 데이터만 추출하여 fg-data-profiling으로 프로파일링하는 스크립트.
"""

import pandas as pd
from ydata_profiling import ProfileReport
import webbrowser
import os

def run():
    print("1. 매핑 정보에서 연남동 행정동코드 찾기...")
    mapping_df = pd.read_excel("seoul-pops/data/행정동코드_매핑정보_20241218.xlsx")
    
    # 행자부기준 행정동코드 찾기
    yeonnam_rows = mapping_df[mapping_df['행정동명'].str.contains('연남동', na=False)]
    if yeonnam_rows.empty:
        print("연남동 매핑 정보를 찾을 수 없습니다.")
        return
    
    yeonnam_code = yeonnam_rows.iloc[0]['행자부행정동코드']
    print(f"연남동 행정동코드: {yeonnam_code}")
    
    print("2. 데이터 로드 및 연남동 필터링...")
    file_path = "seoul-pops/data/LOCAL_PEOPLE_DONG_202606_tidy.parquet"
    df = pd.read_parquet(file_path)
    
    df_yeonnam = df[df['행정동코드'].astype(str) == str(yeonnam_code)]
    
    # fg-data-profiling 버그(IndexError, KeyError) 방지를 위해 카테고리 및 다운캐스트 데이터타입 원복
    # pandas astype() 버그를 우회하기 위해 순수 값으로 새 DataFrame 생성
    df_clean = pd.DataFrame()
    for col in df_yeonnam.columns:
        if df_yeonnam[col].dtype.name == 'category':
            # 카테고리 타입은 문자열 리스트로 직접 변환
            df_clean[col] = [str(x) for x in df_yeonnam[col]]
        else:
            # 나머지는 순수 numpy 배열로 복사 후 타입 변환
            df_clean[col] = df_yeonnam[col].values
            
    for col in df_clean.select_dtypes(['int8', 'int16', 'int32']).columns:
        df_clean[col] = df_clean[col].astype('int64')
    for col in df_clean.select_dtypes(['float32']).columns:
        df_clean[col] = df_clean[col].astype('float64')
    
    print(f"연남동 데이터 행 수: {len(df_clean)}")
    
    print("3. fg-data-profiling 리포트 생성 중...")
    # KeyError: 'value_counts_without_nan' 등의 에러를 방지하기 위해 minimal=True 사용
    profile = ProfileReport(df_clean, title="Yeonnam-dong Data Profiling Report", minimal=True)
    
    report_path = "seoul-pops/report/yeonnam_profile.html"
    profile.to_file(report_path)
    print(f"4. 완료! 프로파일링 리포트가 생성되었습니다: {os.path.abspath(report_path)}")

if __name__ == "__main__":
    run()
