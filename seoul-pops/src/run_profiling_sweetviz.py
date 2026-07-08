"""
데이터 프로파일링 스크립트 (Sweetviz 활용)
fg-data-profiling 라이브러리의 내부 버그(KeyError: 'value_counts_without_nan')로 인해
대안으로 Sweetviz를 사용하여 데이터 프로파일링 리포트를 생성합니다.
"""

import pandas as pd
import sweetviz as sv
import webbrowser
import os

def run_profile():
    print("1. 데이터 로드 및 샘플링 (1% 추출)...")
    file_path = "seoul-pops/data/LOCAL_PEOPLE_DONG_202606_tidy.parquet"
    df = pd.read_parquet(file_path)
    df_sample = df.sample(frac=0.01, random_state=42)
    
    print("2. Sweetviz 프로파일링 리포트 생성 중...")
    report = sv.analyze(df_sample)
    
    report_path = "seoul-pops/report/data_profile.html"
    report.show_html(filepath=report_path, open_browser=False)
    print(f"3. 완료! 프로파일링 리포트가 생성되었습니다: {os.path.abspath(report_path)}")

if __name__ == "__main__":
    run_profile()
