"""
이 스크립트는 연남동과 성수동의 생활인구수 데이터를 시간대별, 연령대별로 시각화합니다.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # 윈도우 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    file_path = "seoul-pops/data/LOCAL_PEOPLE_DONG_202606_tidy.parquet"
    print("Reading parquet data...")
    df = pd.read_parquet(file_path)
    
    # 동 매핑
    dong_map = {
        11200650: '성수1가1동',
        11200660: '성수1가2동',
        11200670: '성수2가1동',
        11200690: '성수2가3동',
        11440710: '연남동'
    }
    
    # 코드 필터링
    print("Filtering data...")
    df_filtered = df[df['행정동코드'].isin(dong_map.keys())].copy()
    
    # 카테고리 타입이면 map 적용 전 astype 변환 필요
    df_filtered['행정동코드'] = df_filtered['행정동코드'].astype(int)
    df_filtered['행정동명'] = df_filtered['행정동코드'].map(dong_map)
    
    # 집계 (남녀 합산)
    print("Aggregating data...")
    df_agg = df_filtered.groupby(['시간대구분', '행정동명', '연령대'], observed=True)['인구수'].sum().reset_index()
    
    # 시각화: x=시간대, y=인구수, hue=행정동, facet=연령대
    print("Plotting...")
    g = sns.relplot(
        data=df_agg,
        x='시간대구분',
        y='인구수',
        hue='행정동명',
        col='연령대',
        col_wrap=4,
        kind='line',
        height=3,
        aspect=1.2,
        marker='o'
    )
    
    g.set_axis_labels("시간대", "생활인구수")
    g.set_titles("{col_name}")
    g.fig.suptitle("연남동 vs 성수동 시간대별/연령대별 생활인구수 (행정동별)", y=1.05)
    
    out_path = "seoul-pops/report/seongsu_yeonnam_population.png"
    g.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {out_path}")
    
    # 사용자 요청 중 "y축에 연령대"라는 부분을 반영하여 히트맵 형태도 하나 생성해둠
    # (선그래프에서는 연령대를 y축으로 하기 모호하므로 대안으로 제공)
    df_heat = df_agg.groupby(['시간대구분', '연령대'], observed=True)['인구수'].sum().reset_index()
    df_pivot = df_heat.pivot(index='연령대', columns='시간대구분', values='인구수')
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(df_pivot, cmap='YlOrRd', annot=False)
    plt.title("전체(연남+성수) 시간대별/연령대별 생활인구수 히트맵")
    plt.xlabel("시간대")
    plt.ylabel("연령대")
    heat_path = "seoul-pops/report/seongsu_yeonnam_heatmap.png"
    plt.savefig(heat_path, dpi=300, bbox_inches='tight')
    print(f"Saved heatmap to {heat_path}")

if __name__ == "__main__":
    main()
