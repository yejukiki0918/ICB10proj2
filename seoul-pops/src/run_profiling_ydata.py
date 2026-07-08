import pandas as pd
from ydata_profiling import ProfileReport

def run_profile():
    print("1. 데이터 로드 및 샘플링 (1% 추출)...")
    file_path = "seoul-pops/data/LOCAL_PEOPLE_DONG_202606_tidy.parquet"
    df = pd.read_parquet(file_path)
    df_sample = df.sample(frac=0.01, random_state=42)
    
    print("2. 프로파일링 리포트 생성 중...")
    profile = ProfileReport(df_sample, title="Seoul Pops Data Profiling Report", explorative=True)
    report_path = "seoul-pops/report/data_profile.html"
    profile.to_file(report_path)
    print(f"3. 완료! 프로파일링 리포트가 생성되었습니다: {report_path}")

if __name__ == "__main__":
    run_profile()
