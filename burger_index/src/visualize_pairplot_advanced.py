"""
지역별 브랜드 빈도수 교차표 데이터를 기반으로 
상삼각행렬에 회귀선과 상관계수를 포함한 페어플롯을 생성하는 스크립트.
"""
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

def main():
    # Windows 한글 폰트 설정
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    data_path = os.path.join("burger_index", "report", "region_brand_crosstab.csv")
    output_path = os.path.join("burger_index", "report", "brand_pairplot_advanced.png")
    
    # 교차표 데이터 로드
    df = pd.read_csv(data_path, index_col=0, encoding='utf-8-sig')
    
    # '총합' 제외
    if '총합' in df.index:
        df = df.drop('총합', axis=0)
    if '총합' in df.columns:
        df = df.drop('총합', axis=1)
        
    brands = [col for col in df.columns if col in ['KFC', '롯데리아', '맥도날드', '버거킹']]
    
    # PairGrid 생성
    g = sns.PairGrid(df[brands], height=2.5)
    
    # 대각선: KDE 밀도 추정
    g.map_diag(sns.kdeplot)
    
    # 상삼각: 산점도 및 회귀선, 상관계수 텍스트 추가
    def corrfunc(x, y, **kws):
        r, _ = pearsonr(x, y)
        ax = plt.gca()
        ax.annotate(f'r = {r:.2f}', xy=(0.95, 0.95), xycoords='axes fraction', 
                    ha='right', va='top', fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8, ec='gray'))
    
    g.map_upper(sns.regplot, scatter_kws={'alpha':0.6}, line_kws={'color':'red'})
    g.map_upper(corrfunc)
    
    # 하삼각: 마스크 처리 (빈 공간으로 두기 위해 축 숨김)
    for i in range(len(brands)):
        for j in range(len(brands)):
            if i > j:  # 하삼각행렬
                g.axes[i, j].set_visible(False)
    
    g.fig.suptitle('지역별 버거 브랜드 매장 수: 상관관계 및 회귀선 (상삼각)', y=1.02)
    
    # 이미지 파일로 저장
    g.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"고급 페어플롯 이미지가 {output_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()
