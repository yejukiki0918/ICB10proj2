"""
이 스크립트는 이전에 전처리한 파케이 파일을 불러와 범주형 변수를 변환하고,
기술 통계를 구한 후 추가적인 다운캐스팅을 진행하고 결과를 출력합니다.
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
    
    print("Converting ID and DongCode to category...")
    df['기준일ID'] = df['기준일ID'].astype('category')
    df['행정동코드'] = df['행정동코드'].astype('category')
    
    # Calculate descriptive statistics
    print("Calculating descriptive statistics...")
    numeric_stats = df.describe(include=['number'])
    category_stats = df.describe(include=['category'])
    
    # Further downcasting
    # Since they are floats, let's see if we can use float32
    print("Further downcasting float64 to float32...")
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype('float32')
        
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    # info
    print("Capturing final info...")
    final_info = capture_info(df)
    
    # Write report
    report_content = f"""# 2차 다운캐스팅 및 기술 통계 리포트

## 기술 통계 (수치형 변수)
{numeric_stats.to_markdown()}

## 기술 통계 (범주형 변수)
{category_stats.to_markdown()}

## 최종 데이터 정보 (info())
```text
{final_info}
```
"""
    with open("seoul-pops/report/downcast_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("Done! Report saved to seoul-pops/report/downcast_report.md")

if __name__ == "__main__":
    main()
