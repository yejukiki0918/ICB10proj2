"""
지역별 브랜드 교차표를 이용해 각 브랜드 전체 매장 수(총 빈도수)를 계산하고
막대그래프로 시각화하는 스크립트입니다.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Windows 한글 폰트 설정
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    data_path = os.path.join('burger_index', 'report', 'region_brand_crosstab.csv')
    output_path = os.path.join('burger_index', 'report', 'brand_total_counts.png')
    
    # 교차표 데이터 로드 (인덱스가 지역명)
    df = pd.read_csv(data_path, index_col=0, encoding='utf-8-sig')
    
    # 총합 행/열 제거
    if '총합' in df.index:
        df = df.drop('총합', axis=0)
    if '총합' in df.columns:
        df = df.drop('총합', axis=1)
    
    # 브랜드 컬럼 리스트 (예시 브랜드만)
    brands = [col for col in df.columns if col in ['KFC', '롯데리아', '맥도날드', '버거킹']]
    
    # 각 브랜드 전체 매장 수 합산
    total_counts = df[brands].sum().sort_values(ascending=False)
    
    # 막대그래프 생성
    plt.figure(figsize=(8, 5))
    bars = plt.bar(total_counts.index, total_counts.values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    plt.title('브랜드별 전체 매장 수', fontsize=16, pad=12)
    plt.ylabel('매장 수', fontsize=12)
    plt.xlabel('브랜드', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    # 값 라벨 표기
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f'{int(height):,}',
                 ha='center', va='bottom', fontsize=11)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'브랜드별 총 매장 수 막대그래프가 {output_path}에 저장되었습니다.')

if __name__ == "__main__":
    main()
