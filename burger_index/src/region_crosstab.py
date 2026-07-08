"""
burger.csv 파일에서 시도명과 시군구명을 합쳐 '시도시군구명' 파생변수를 만들고,
해당 지역명과 브랜드명 간의 교차표를 생성하여 CSV 파일로 저장하는 스크립트입니다.
"""
import os
import pandas as pd

def main():
    data_path = os.path.join("burger_index", "data", "burger.csv")
    output_path = os.path.join("burger_index", "report", "region_brand_crosstab.csv")
    
    df = pd.read_csv(data_path, encoding='utf-8')
    
    # 시도명, 시군구명 컬럼 찾기 (정확한 매핑을 위해 부분 일치 사용)
    sido_col = [c for c in df.columns if '시도명' in c][0]
    sigungu_col = [c for c in df.columns if '시군구명' in c][0]
    brand_col = '브랜드명'
    
    # '시도시군구명' 파생변수 생성 (예: '서울특별시 강남구')
    df['시도시군구명'] = df[sido_col].astype(str).str.strip() + ' ' + df[sigungu_col].astype(str).str.strip()
    
    # 교차표 생성: 인덱스(시도시군구명), 컬럼(브랜드명)
    crosstab_result = pd.crosstab(df['시도시군구명'], df[brand_col], margins=True, margins_name='총합')
    
    # CSV 파일로 저장
    crosstab_result.to_csv(output_path, encoding='utf-8-sig')
    
    print(f"교차표가 성공적으로 생성되어 {output_path}에 저장되었습니다.")
    print("생성된 교차표 미리보기 (상위 5개 지역):")
    print(crosstab_result.head())

if __name__ == "__main__":
    main()
