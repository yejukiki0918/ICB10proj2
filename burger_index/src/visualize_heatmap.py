"""
지역별 브랜드 빈도수 교차표 데이터를 기반으로 
상관계수를 계산하여 히트맵(Heatmap)으로 시각화하는 스크립트.
"""
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    # Windows 한글 폰트 설정
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    data_path = os.path.join("burger_index", "report", "region_brand_crosstab.csv")
    output_path = os.path.join("burger_index", "report", "brand_corr_heatmap.png")
    
    # 교차표 데이터 로드
    df = pd.read_csv(data_path, index_col=0, encoding='utf-8-sig')
    
    # '총합' 제외
    if '총합' in df.index:
        df = df.drop('총합', axis=0)
    if '총합' in df.columns:
        df = df.drop('총합', axis=1)
        
    brands = [col for col in df.columns if col in ['KFC', '롯데리아', '맥도날드', '버거킹']]
    
    # 피어슨 상관계수 계산
    corr_matrix = df[brands].corr()
    
    # 시각화 설정
    plt.figure(figsize=(8, 6))
    
    # 히트맵 시각화 (마스크 없이 전체 표시, 값 표기, 색상 맵 설정)
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm",
                vmin=-1, vmax=1, square=True, linewidths=.5, cbar_kws={"shrink": .8})
    
    plt.title('지역별 버거 브랜드 매장 수 상관계수 히트맵', fontsize=16, pad=15)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12, rotation=0)
    
    # 이미지 파일로 저장
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"상관계수 히트맵 이미지가 {output_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()
