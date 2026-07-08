"""
지역별 브랜드 교차표 데이터를 기반으로 '버거지수' 파생변수를 계산하는 스크립트.
버거지수 = (버거킹 + 맥도날드 + KFC) / 롯데리아
"""
import os
import pandas as pd
import numpy as np

def main():
    data_path = os.path.join("burger_index", "data", "region_brand_crosstab.csv")
    output_path = os.path.join("burger_index", "data", "region_burger_index.csv")
    
    # 데이터 로드 (인덱스는 지역명)
    df = pd.read_csv(data_path, index_col=0, encoding='utf-8-sig')
    
    # '총합' 행 제거 (분석 대상 지역만)
    if '총합' in df.index:
        df = df.drop('총합', axis=0)
    
    # 브랜드별 컬럼이 있는지 확인하고 누락된 경우 0으로 채움
    for brand in ['버거킹', '맥도날드', 'KFC', '롯데리아']:
        if brand not in df.columns:
            df[brand] = 0
            
    # 버거지수 계산
    # 롯데리아 매장이 0인 경우를 대비해 0으로 나누기 에러 방지 (np.where 사용)
    df['버거지수'] = np.where(df['롯데리아'] > 0, 
                             (df['버거킹'] + df['맥도날드'] + df['KFC']) / df['롯데리아'], 
                             float('inf'))
    
    # 버거지수가 높은 순서대로 정렬
    df = df.sort_values(by='버거지수', ascending=False)
    
    # 결과를 새로운 CSV 파일로 저장
    df.to_csv(output_path, encoding='utf-8-sig')
    
    # 기존 파일 덮어쓰기 (사용자의 편의를 위해 원본 파일도 업데이트)
    df.to_csv(data_path, encoding='utf-8-sig')
    
    print(f"버거지수가 계산되어 {data_path} 및 {output_path}에 저장되었습니다.")
    print("\n[ 버거지수 상위 5개 지역 ]")
    print(df[['버거킹', '맥도날드', 'KFC', '롯데리아', '버거지수']].head())

if __name__ == "__main__":
    main()
