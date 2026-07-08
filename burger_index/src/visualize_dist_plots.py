"""
지역별 브랜드 빈도수 분포를 보여주기 위해
박스플롯(Boxplot)과 바이올린 플롯(Violin plot)으로 시각화하는 스크립트.
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
    output_path = os.path.join("burger_index", "report", "brand_dist_plots.png")
    
    # 데이터 로드
    df = pd.read_csv(data_path, index_col=0, encoding='utf-8-sig')
    
    # '총합' 제외
    if '총합' in df.index:
        df = df.drop('총합', axis=0)
    if '총합' in df.columns:
        df = df.drop('총합', axis=1)
        
    brands = [col for col in df.columns if col in ['KFC', '롯데리아', '맥도날드', '버거킹']]
    
    # 데이터를 long format으로 변환 (seaborn 시각화에 적합)
    df_melted = df[brands].melt(var_name='브랜드', value_name='매장 수')
    
    # 1행 2열의 서브플롯 생성
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 박스플롯 (Boxplot)
    sns.boxplot(x='브랜드', y='매장 수', data=df_melted, ax=axes[0], palette='Set2')
    axes[0].set_title('브랜드별 지역 매장 수 분포 (Boxplot)', fontsize=14)
    axes[0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # 바이올린 플롯 (Violin plot)
    sns.violinplot(x='브랜드', y='매장 수', data=df_melted, ax=axes[1], palette='Set2', inner='quartile')
    axes[1].set_title('브랜드별 지역 매장 수 분포 (Violin plot)', fontsize=14)
    axes[1].grid(axis='y', linestyle='--', alpha=0.7)
    
    # 레이아웃 조정 및 저장
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"분포 시각화 이미지가 {output_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()
