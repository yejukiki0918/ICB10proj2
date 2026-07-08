"""
카토그램(블록 맵) 방식으로 지역별 버거지수를 시각화하는 페이지입니다.
작성일: 2026-07-04
"""
import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

st.set_page_config(page_title="카토그램 지도", page_icon="🧩", layout="wide")
st.title("🧩 전국 시군구단위 버거지수 카토그램")

# 윈도우 환경 폰트 설정 (한글 깨짐 방지)
if os.name == 'nt':
    plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_and_map_data(filter_threshold):
    # 1. 원본 데이터 로드
    data_path = os.path.join("burger_index", "data", "region_brand_crosstab.csv")
    df_data = pd.read_csv(data_path, encoding='utf-8-sig')
    
    # 필터링 적용
    if filter_threshold > 0:
        df_data = df_data[df_data['총합'] >= filter_threshold]
        
    # 2. 카토그램 격자 데이터 로드
    carto_path = os.path.join("burger_index", "data", "data_draw_korea.csv")
    df_carto = pd.read_csv(carto_path)
    
    # 3. 매핑 함수 정의
    def get_mapped_name(sido_sigungu):
        parts = sido_sigungu.split()
        if len(parts) >= 2:
            sido = parts[0]
            sigungu = parts[1]
            
            sido_dict = {
                '서울특별시': '서울', '부산광역시': '부산', '대구광역시': '대구',
                '인천광역시': '인천', '광주광역시': '광주', '대전광역시': '대전',
                '울산광역시': '울산', '세종특별자치시': '세종', '경기도': '경기',
                '강원도': '강원', '충청북도': '충북', '충청남도': '충남',
                '전라북도': '전북', '전라남도': '전남', '경상북도': '경북',
                '경상남도': '경남', '제주특별자치도': '제주'
            }
            sido_abbr = sido_dict.get(sido, sido[:2])
            
            # 예외 처리
            if sigungu == '고성군': return '고성(강원)' if sido == '강원도' else '고성(경남)'
            if sigungu == '여주군': sigungu = '여주시'
            if sigungu == '미추홀구': return '인천 남구' # 과거 지명 매핑
            if sido == '경기도' and sigungu == '화성시': return '화성' # 화성시 하위 구 통합
            
            # 창원시, 천안시 등 3단어 처리
            if len(parts) == 3 and parts[1].endswith('시') and parts[2].endswith('구'):
                if parts[1] == '창원시':
                    if '마산합포구' in parts[2]: return '창원 합포'
                    if '마산회원구' in parts[2]: return '창원 회원'
                    if '진해구' in parts[2]: return '창원 진해'
                    if '성산구' in parts[2]: return '창원 성산'
                    if '의창구' in parts[2]: return '창원 의창'
                if parts[1] == '천안시':
                    if '동남구' in parts[2]: return '천안 동남'
                    if '서북구' in parts[2]: return '천안 서북'
                if parts[1] == '전주시':
                    if '덕진구' in parts[2]: return '전주 덕진'
                    if '완산구' in parts[2]: return '전주 완산'
                if parts[1] == '청주시':
                    if '상당구' in parts[2]: return '청주 상당'
                    if '서원구' in parts[2]: return '청주 서원'
                    if '흥덕구' in parts[2]: return '청주 흥덕'
                    if '청원구' in parts[2]: return '청주 청원'
                if parts[1] == '포항시':
                    if '남구' in parts[2]: return '포항 남구'
                    if '북구' in parts[2]: return '포항 북구'
                if parts[1] == '성남시':
                    if '분당구' in parts[2]: return '성남 분당'
                    if '수정구' in parts[2]: return '성남 수정'
                    if '중원구' in parts[2]: return '성남 중원'
                if parts[1] == '안양시':
                    if '동안구' in parts[2]: return '안양 동안'
                    if '만안구' in parts[2]: return '안양 만안'
                if parts[1] == '안산시':
                    if '단원구' in parts[2]: return '안산 단원'
                    if '상록구' in parts[2]: return '안산 상록'
                if parts[1] == '고양시':
                    if '덕양구' in parts[2]: return '고양 덕양'
                    if '일산동구' in parts[2]: return '고양 일산동'
                    if '일산서구' in parts[2]: return '고양 일산서'
                if parts[1] == '용인시':
                    if '기흥구' in parts[2]: return '용인 기흥'
                    if '수지구' in parts[2]: return '용인 수지'
                    if '처인구' in parts[2]: return '용인 처인'
                if parts[1] == '수원시':
                    if '권선구' in parts[2]: return '수원 권선'
                    if '영통구' in parts[2]: return '수원 영통'
                    if '장안구' in parts[2]: return '수원 장안'
                    if '팔달구' in parts[2]: return '수원 팔달'
                if parts[1] == '부천시':
                    if '소사구' in parts[2]: return '부천 소사'
                    if '오정구' in parts[2]: return '부천 오정'
                    if '원미구' in parts[2]: return '부천 원미'
                
                si_abbr = parts[1][:-1]
                gu_abbr = parts[2][:-1]
                return f"{si_abbr} {gu_abbr}"
                
            # 일반 시/군/구 (2글자 구역 포함)
            if sigungu.endswith('시') or sigungu.endswith('군') or sigungu.endswith('구'):
                sig_abbr = sigungu[:-1] if len(sigungu) > 2 else sigungu
                if sido_abbr in ['서울', '부산', '대구', '인천', '광주', '대전', '울산']:
                    return f"{sido_abbr} {sig_abbr}"
                elif sido_abbr == '세종':
                    return '세종'
                else:
                    return sig_abbr
                        
        return sido_sigungu

    df_data['ID'] = df_data['시도시군구명'].apply(get_mapped_name)
    
    # ID 단위로 통합 (화성시 분리된 구역 등)
    grouped = df_data.groupby('ID')[['KFC', '롯데리아', '맥도날드', '버거킹', '총합']].sum().reset_index()
    # 버거지수 재계산 (분모 0 방지)
    grouped['롯데리아_adj'] = grouped['롯데리아'].replace(0, 1) # inf 방지용
    grouped['버거지수'] = (grouped['KFC'] + grouped['맥도날드'] + grouped['버거킹']) / grouped['롯데리아_adj']
    
    # inf 처리
    max_finite = grouped.loc[grouped['버거지수'] != np.inf, '버거지수'].max()
    grouped['버거지수_시각화용'] = grouped['버거지수'].replace(np.inf, max_finite + 1.0)
    
    # 카토그램 좌표 데이터와 병합
    map_data = pd.merge(df_carto, grouped, how='left', on='ID')
    return map_data

st.sidebar.header("설정")
filter_option = st.sidebar.selectbox("데이터 필터링 (최소 매장 수)", ["총합 5개 이상 (권장)", "총합 3개 이상", "필터링 없음 (전체 데이터)"])

threshold = 0
if "5개" in filter_option:
    threshold = 5
elif "3개" in filter_option:
    threshold = 3

map_data = load_and_map_data(threshold)

# BORDER_LINES (행정구역 경계선 굵게)
BORDER_LINES = [
    [(3, 2), (5, 2), (5, 3), (9, 3), (9, 1)], # 인천
    [(2, 5), (3, 5), (3, 4), (8, 4), (8, 7), (7, 7), (7, 9), (4, 9), (4, 7), (1, 7)], # 서울
    [(1, 6), (1, 9), (3, 9), (3, 10), (8, 10), (8, 9),
     (9, 9), (9, 8), (10, 8), (10, 5), (9, 5), (9, 3)], # 경기
    [(9, 12), (9, 10), (8, 10)], # 강원
    [(10, 5), (11, 5), (11, 4), (12, 4), (12, 5), (13, 5),
     (13, 4), (14, 4), (14, 2)], # 충남
    [(11, 5), (12, 5), (12, 6), (15, 6), (15, 7), (13, 7),
     (13, 8), (11, 8), (11, 9), (10, 9), (10, 8)], # 충북
    [(14, 4), (15, 4), (15, 6)], # 대전
    [(14, 7), (14, 9), (13, 9), (13, 11), (13, 13)], # 경북
    [(14, 8), (16, 8), (16, 10), (15, 10),
     (15, 11), (14, 11), (14, 12), (13, 12)], # 대구
    [(15, 11), (16, 11), (16, 13)], # 울산
    [(17, 1), (17, 3), (18, 3), (18, 6), (15, 6)], # 전북
    [(19, 2), (19, 4), (21, 4), (21, 3), (22, 3), (22, 2), (19, 2)], # 광주
    [(18, 5), (20, 5), (20, 6)], # 전남
    [(16, 9), (18, 9), (18, 8), (19, 8), (19, 9), (20, 9), (20, 10)], # 부산
]

# 플롯 그리기
fig, ax = plt.subplots(figsize=(9, 12))
ax.invert_yaxis()

# 데이터 범위를 기반으로 컬러맵 설정
vmin = map_data['버거지수_시각화용'].min() if not map_data['버거지수_시각화용'].isna().all() else 0
vmax = map_data['버거지수_시각화용'].max() if not map_data['버거지수_시각화용'].isna().all() else 1
if np.isnan(vmin): vmin = 0
if np.isnan(vmax): vmax = 1

cmap = plt.get_cmap('Blues')
norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

for idx, row in map_data.iterrows():
    # 텍스트 나누기 (예: "서울 강남" -> "서울\n강남")
    name_lines = row['ID'].split()
    if len(name_lines) == 1:
        if len(row['ID']) == 3:
            name_text = row['ID'][:2] + '\n' + row['ID'][2]
        elif len(row['ID']) == 4:
            name_text = row['ID'][:2] + '\n' + row['ID'][2:]
        else:
            name_text = row['ID']
    else:
        name_text = name_lines[0] + '\n' + name_lines[1]

    # 결측치(데이터 없는 지역)는 회색 혹은 흰색
    if pd.isna(row['버거지수_시각화용']):
        facecolor = 'whitesmoke'
        edgecolor = 'lightgray'
        val_text = ""
    else:
        facecolor = cmap(norm(row['버거지수_시각화용']))
        edgecolor = 'lightgray'
        # 너무 진한 파란색일 경우 텍스트를 흰색으로 변경
        text_color = 'white' if norm(row['버거지수_시각화용']) > 0.6 else 'black'
        val_text = f"{row['버거지수']:.1f}"

    rect = plt.Rectangle((row['x'], row['y']), 1, 1, facecolor=facecolor, edgecolor=edgecolor)
    ax.add_patch(rect)
    
    # 텍스트 색상 결정 (배경에 따라 다르게)
    txt_color = 'white' if not pd.isna(row['버거지수_시각화용']) and norm(row['버거지수_시각화용']) > 0.6 else 'black'
    
    ax.text(row['x'] + 0.5, row['y'] + 0.4, name_text, ha='center', va='center', size=9, color=txt_color, fontweight='bold')
    if val_text:
        ax.text(row['x'] + 0.5, row['y'] + 0.75, val_text, ha='center', va='center', size=7, color=txt_color)

# 경계선 그리기
for path in BORDER_LINES:
    ys, xs = zip(*path)
    ax.plot(xs, ys, c='black', lw=2)

ax.set_aspect('equal')
ax.axis('off')

# 컬러바 추가
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cb = fig.colorbar(sm, ax=ax, shrink=0.5, pad=0.05)
cb.set_label('버거지수')

plt.title('전국 시군구단위 버거지수', fontsize=20, fontweight='bold', pad=20)
plt.tight_layout()

# Streamlit에 표시
st.pyplot(fig)

st.markdown("""
### 📌 카토그램(Cartogram) 특징
* 지리적 면적이 아닌 **동일한 크기의 블록**으로 지역을 표현하여 인구나 상권 밀집지역(수도권 등)의 왜곡을 방지합니다.
* 파란색이 진할수록 해당 지역의 버거지수가 높음(버거킹, 맥도날드, KFC의 비율이 높음)을 의미합니다.
* 매장 수가 너무 적은 지역(필터링 옵션 참조)은 데이터 분석의 통계적 왜곡을 방지하기 위해 빈 블록으로 처리했습니다.
""")
