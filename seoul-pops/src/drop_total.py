"""
이 스크립트는 총생활인구수 컬럼을 제외하고 최적화된 형식으로 파케이 파일을 다시 저장합니다.
"""
import pandas as pd
import io

def capture_info(df):
    buffer = io.StringIO()
    df.info(buf=buffer)
    return buffer.getvalue()

def main():
    file_path = "seoul-pops/data/LOCAL_PEOPLE_DONG_202606_tidy.parquet"
    print("Reading parquet data...")
    df = pd.read_parquet(file_path)
    
    print("Dropping '총생활인구수' column...")
    if '총생활인구수' in df.columns:
        df = df.drop(columns=['총생활인구수'])
        
    print("Re-applying downcasting and categorizations...")
    df['기준일ID'] = df['기준일ID'].astype('category')
    df['행정동코드'] = df['행정동코드'].astype('category')
    
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype('float32')
        
    for col in df.select_dtypes(include=['int64', 'int32']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    print("Capturing final info...")
    final_info = capture_info(df)
    
    print("Saving to parquet...")
    df.to_parquet(file_path, index=False)
    
    # Write report
    report_content = f"""# 총생활인구수 제외 및 최적화 리포트

## 변경 후 상위 5개 행
{df.head().to_markdown()}

## 최종 데이터 정보 (info())
```text
{final_info}
```
"""
    with open("seoul-pops/report/drop_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("Done! Report saved to seoul-pops/report/drop_report.md")

if __name__ == "__main__":
    main()
