"""
위도와 경도를 기반으로 지역별 버거지수 산점도를 Plotly를 이용해 
인터랙티브한 HTML로 시각화하는 스크립트.
"""
import os
import pandas as pd
import numpy as np
import plotly.express as px

def main():
    data_path = os.path.join("burger_index", "data", "region_brand_crosstab.csv")
    out_all_path = os.path.join("burger_index", "report", "burger_index_scatter_all.html")
    out_filtered_path = os.path.join("burger_index", "report", "burger_index_scatter_filtered.html")
    
    # 데이터 로드
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    
    # 결측치 처리 (위도, 경도가 없는 지역 제외)
    df = df.dropna(subset=['중앙_위도', '중앙_경도', '버거지수'])
    
    # 무한대(inf) 값 처리: 롯데리아가 0개여서 발생한 inf를 유한한 최대값 + 1.0으로 조정
    max_finite = df.loc[df['버거지수'] != np.inf, '버거지수'].max()
    df['버거지수_시각화용'] = df['버거지수'].replace(np.inf, max_finite + 1.0)
    
    # hover(마우스 오버) 시 보여줄 정보 포맷팅을 위해 인덱스를 '시도시군구명'으로 명시
    if '시도시군구명' not in df.columns:
        df.reset_index(names='시도시군구명', inplace=True)
        
    hover_info = {
        '중앙_경도': False,
        '중앙_위도': False,
        '버거지수_시각화용': False,
        '시도시군구명': True,
        '버거지수': ':.2f',
        '총합': True,
        'KFC': True,
        '롯데리아': True,
        '맥도날드': True,
        '버거킹': True
    }
    
    # 1. 전체 데이터 시각화
    fig_all = px.scatter(
        df,
        x='중앙_경도', y='중앙_위도',
        size='버거지수_시각화용',
        color='버거지수_시각화용',
        hover_name='시도시군구명',
        hover_data=hover_info,
        color_continuous_scale=px.colors.sequential.YlOrRd,
        title='지역별 버거지수 산점도 (전체 데이터)',
        labels={'중앙_경도': '경도', '중앙_위도': '위도', '버거지수_시각화용': '버거지수'}
    )
    # 실제 지도 비율 유지
    fig_all.update_yaxes(scaleanchor="x", scaleratio=1)
    fig_all.write_html(out_all_path)
    
    # 2. 총합 >= 5 조건으로 필터링한 데이터 시각화 (왜곡 방지)
    df_filtered = df[df['총합'] >= 5].copy()
    
    fig_filtered = px.scatter(
        df_filtered,
        x='중앙_경도', y='중앙_위도',
        size='버거지수_시각화용',
        color='버거지수_시각화용',
        hover_name='시도시군구명',
        hover_data=hover_info,
        color_continuous_scale=px.colors.sequential.YlOrRd,
        title='지역별 버거지수 산점도 (매장 총합 5개 이상 지역)',
        labels={'중앙_경도': '경도', '중앙_위도': '위도', '버거지수_시각화용': '버거지수'}
    )
    fig_filtered.update_yaxes(scaleanchor="x", scaleratio=1)
    fig_filtered.write_html(out_filtered_path)
    
    # 3. 버거지수 상위 10개 지역 도출 (필터링된 데이터 기준)
    top10_filtered = df_filtered.sort_values('버거지수_시각화용', ascending=False).head(10)
    
    print("=== 버거지수 상위 10개 지역 (총합 5개 이상) ===")
    print(top10_filtered[['시도시군구명', '버거지수', '총합', 'KFC', '롯데리아', '맥도날드', '버거킹']].to_markdown(index=False))
    
if __name__ == "__main__":
    main()
