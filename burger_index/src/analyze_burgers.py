"""
추출된 burger.csv 파일에서 브랜드명(버거킹, 맥도날드, KFC, 롯데리아) 파생변수를 생성하고,
상권업종대분류명과의 교차표(Cross Tabulation)를 생성하여 빈도수를 계산하는 스크립트입니다.
"""
import os
import pandas as pd

def get_brand(shop_name):
    name = str(shop_name).lower()
    if '버거킹' in name or 'burger king' in name:
        return '버거킹'
    elif '맥도날드' in name or 'mcdonald' in name:
        return '맥도날드'
    elif 'kfc' in name:
        return 'KFC'
    elif '롯데리아' in name or 'lotteria' in name:
        return '롯데리아'
    else:
        return '기타'

def main():
    data_path = os.path.join("burger_index", "data", "burger.csv")
    
    try:
        df = pd.read_csv(data_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(data_path, encoding='cp949')

    # Create derived variable '브랜드명'
    df['브랜드명'] = df['상호명'].apply(get_brand)

    # Filter out '기타' if any anomalies exist (though previous script only extracted the 4 brands)
    df = df[df['브랜드명'] != '기타']

    # Identify the column name for '상권업종대분류명'. It could have quotes or spaces
    target_col = None
    for col in df.columns:
        if '상권업종대분류명' in col:
            target_col = col
            break
            
    if target_col is None:
        print("상권업종대분류명 column not found. Available columns:")
        print(df.columns)
        return

    # Create cross tab
    crosstab_result = pd.crosstab(df['브랜드명'], df[target_col], margins=True, margins_name='총합')
    
    print("\n[브랜드별 상권업종대분류명 교차표 빈도수]")
    print("-" * 50)
    print(crosstab_result)
    print("-" * 50)

if __name__ == "__main__":
    main()
