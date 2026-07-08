"""
이 스크립트는 서울 생활인구 데이터를 읽어와서 파싱하고, tidy format으로 변환한 뒤
데이터 타입을 다운캐스팅하여 parquet 형식으로 저장합니다.
생성일: 2026-07-06
"""
import pandas as pd
import zipfile
import io
import sys

def capture_info(df):
    buffer = io.StringIO()
    df.info(buf=buffer)
    return buffer.getvalue()

def process_data():
    file_path = "seoul-pops/data/LOCAL_PEOPLE_DONG_202606.zip"
    
    print("Reading data...")
    # csv file name inside zip is probably LOCAL_PEOPLE_DONG_202606.csv
    try:
        df = pd.read_csv(file_path, encoding='cp949', index_col=False)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='utf-8', index_col=False)

    print("Initial Dataframe info:")
    info_before = capture_info(df)
    
    # Value columns are those representing gender and age.
    # usually named like 남자0세부터9세생활인구수
    value_vars = [c for c in df.columns if c.startswith('남자') or c.startswith('여자')]
    id_vars = [c for c in df.columns if c not in value_vars]
    
    # Check if there are no such columns, maybe the encoding is messed up or names are different.
    if not value_vars:
        print("Warning: Could not find value columns. Column names are:")
        print(df.columns.tolist())
        # Let's try matching '남' and '여' or ending with '인구수' excluding '총생활인구수'
        value_vars = [c for c in df.columns if '인구수' in c and c != '총생활인구수']
        id_vars = [c for c in df.columns if c not in value_vars]
        
    print(f"Melting dataframe... {len(value_vars)} value columns found.")
    df_melt = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='구분', value_name='인구수')
    
    # Extract 성별 and 연령대
    # '남자10세부터14세생활인구수' -> 성별: 남자, 연령대: 10세부터14세
    print("Extracting features...")
    df_melt['성별'] = df_melt['구분'].str[:2] # 남자, 여자
    df_melt['연령대'] = df_melt['구분'].str[2:].str.replace('생활인구수', '')
    
    df_melt = df_melt.drop(columns=['구분'])
    
    # Downcasting
    print("Downcasting data types...")
    # Convert object to category
    for col in df_melt.select_dtypes(['object']).columns:
        df_melt[col] = df_melt[col].astype('category')
        
    # Downcast numeric columns
    for col in df_melt.select_dtypes(['int', 'float']).columns:
        if df_melt[col].dtype == 'float64':
            df_melt[col] = pd.to_numeric(df_melt[col], downcast='float')
        elif df_melt[col].dtype == 'int64':
            df_melt[col] = pd.to_numeric(df_melt[col], downcast='integer')

    print("New Dataframe info:")
    info_after = capture_info(df_melt)
    
    # Save to parquet
    out_path = "seoul-pops/data/LOCAL_PEOPLE_DONG_202606_tidy.parquet"
    print(f"Saving to {out_path}...")
    df_melt.to_parquet(out_path, index=False)
    
    head_str = df_melt.head().to_markdown()
    
    # Write report
    report_content = f"""# 데이터 처리 리포트

## 상위 5개 행 (Tidy Data)
{head_str}

## 원본 데이터 정보 (info())
```
{info_before}
```

## 처리 및 압축 후 데이터 정보 (info())
```
{info_after}
```
"""
    with open("seoul-pops/report/data_process_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("Done!")

if __name__ == "__main__":
    process_data()
