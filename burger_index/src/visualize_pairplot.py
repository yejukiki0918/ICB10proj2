"""
지역별 브랜드 빈도수 교차표 데이터를 기반으로 
브랜드 간의 상관관계를 시각화하는 페어플롯(Pairplot) 생성 스크립트입니다.
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
    output_path = os.path.join("burger_index", "report", "brand_pairplot.png")
    
    # 교차표 데이터 로드 (인덱스는 첫 번째 열인 시도시군구명)
    df = pd.read_csv(data_path, index_col=0, encoding='utf-8-sig')
    
    # '총합' 행과 '총합' 열 제외 (순수 지역별 브랜드 데이터만 플로팅)
    if '총합' in df.index:
        df = df.drop('총합', axis=0)
    if '총합' in df.columns:
        df = df.drop('총합', axis=1)
        
    # 데이터에 존재하는 브랜드명 컬럼 확인
    brands = [col for col in df.columns if col in ['KFC', '롯데리아', '맥도날드', '버거킹']]
    
    # 페어플롯 시각화 생성
    # sns.pairplot은 각 변수간 산점도와 히스토그램/KDE를 보여줍니다.
    plot = sns.pairplot(df[brands], kind='reg', diag_kind='kde', height=2.5)
    plot.fig.suptitle('지역별 버거 브랜드 매장 수 페어플롯 (Pairplot)', y=1.02)
    
    # 이미지 파일로 저장
    plot.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"페어플롯 이미지가 {output_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()
