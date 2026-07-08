"""
이 스크립트는 사람인 마케터 채용공고 데이터를 기반으로 한 Streamlit 대시보드 애플리케이션입니다.
탐색적 데이터 분석(EDA) 및 심층 스펙 분석 결과를 인터랙티브하게 제공하며,
데이터 로딩 최적화(캐싱), 필터링, Plotly 기반 시각화를 포함합니다.
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import os
import re

# ---------------------------------------------------------
# 설정 및 레이아웃 초기화
# ---------------------------------------------------------
st.set_page_config(
    page_title="마케터 취업/채용 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'marketing_project', 'marketing_jobs.csv')

# 정규식 패턴 (Advanced EDA 기준)
SKILLS = {
    'GA / GA4': r'\b(?:ga4?|google analytics)\b',
    'SQL': r'\bsql\b',
    'Python': r'\bpython\b|파이썬',
    'Tableau': r'\btableau\b|태블로',
    'Excel / 엑셀': r'\bexcel\b|엑셀',
    'Adobe': r'adobe|포토샵|일러스트레이터|photoshop|illustrator',
    'Figma': r'\bfigma\b|피그마',
    '프리미어/에펙': r'프리미어|에프터이펙트|premiere|after\s*effect|영상편집',
    'Notion/Slack': r'notion|slack|노션|슬랙'
}
EXP = {
    '에이전시/대행사': r'에이전시|대행사',
    '인턴 경험': r'인턴',
    'SNS 운영': r'sns 채널|sns 운영|인스타그램 운영|유튜브 운영',
    '퍼포먼스 캠페인': r'퍼포먼스 캠페인|매체 운영|광고 집행',
    '브랜드/서비스 런칭': r'브랜드 런칭|서비스 런칭|신규 런칭'
}
RED_FLAGS = {
    '식대/간식 강조': r'식대|간식 무한|간식 제공',
    '강한 체력/책임감': r'체력|강한 책임감|열정',
    '빠른 실행력 (야근)': r'빠른 실행|빠른 호흡',
    '멀티태스킹': r'멀티\s*태스킹|올라운더|all\s*rounder|다양한 업무',
    'A부터 Z까지': r'a부터 z까지|a to z'
}

# ---------------------------------------------------------
# 데이터 로딩 및 전처리 (캐싱)
# ---------------------------------------------------------
@st.cache_data(show_spinner="데이터를 불러오고 전처리하는 중입니다...")
def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df.drop_duplicates(subset=['job_id']).copy()
    
    df['detail_text'] = df['detail_text'].fillna('').str.lower()
    df['title'] = df['title'].fillna('').str.lower()
    df['company_name'] = df['company_name'].fillna('').str.lower()
    df['conditions'] = df['conditions'].fillna('')
    
    # 1. 경력 파싱
    def parse_exp(cond):
        if '경력무관' in cond: return '경력무관'
        if '신입·경력' in cond: return '신입·경력'
        if '신입' in cond: return '신입'
        m = re.search(r'경력\s*(\d+)~(\d+)년', cond)
        if m: return f"{m.group(1)}~{m.group(2)}년"
        m = re.search(r'경력\s*(\d+)년↑', cond)
        if m: return f"{m.group(1)}년 이상"
        return '기타/미상'
    df['experience'] = df['conditions'].apply(parse_exp)
    
    # 2. 직무군 파싱
    def categorize(title):
        if re.search(r'퍼포먼스|ae|광고 기획|매체|데이터|그로스', title): return '퍼포먼스/데이터'
        if re.search(r'콘텐츠|컨텐츠|에디터|sns|유튜브|영상', title): return '콘텐츠/브랜드'
        if re.search(r'b2b|제휴|솔루션|영업', title): return 'B2B/제휴'
        if re.search(r'it|플랫폼|앱|app|웹|프로덕트', title): return 'IT/플랫폼'
        return '일반/기타 마케팅'
    df['category'] = df['title'].apply(categorize)

    # 3. 기업 규모 파싱
    def classify_company(row):
        text = row['detail_text']
        comp = row['company_name']
        if re.search(r'스타트업|시리즈\s*[a-z]|투자 유치|스톡옵션|초기 런칭|유니콘', text):
            return '스타트업'
        if re.search(r'대기업|중견기업|상장|코스피|코스닥', text) or re.search(r'그룹|홀딩스|네트웍스', comp):
            return '중견/대기업'
        return '중소/일반기업'
    df['company_size'] = df.apply(classify_company, axis=1)
    
    # 4. 레드플래그 스코어
    def count_rf(text):
        return sum(1 for p in RED_FLAGS.values() if re.search(p, text))
    df['rf_score'] = df['detail_text'].apply(count_rf)

    return df

# 데이터 로드
try:
    df_raw = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 데 실패했습니다: {e}")
    st.stop()

# ---------------------------------------------------------
# 사이드바 필터
# ---------------------------------------------------------
st.sidebar.title("🔍 필터 설정")

all_categories = ['전체'] + list(df_raw['category'].unique())
selected_category = st.sidebar.selectbox("직무군 선택", all_categories)

all_experience = ['전체'] + list(df_raw['experience'].unique())
selected_experience = st.sidebar.selectbox("요구 경력 선택", all_experience)

all_sizes = ['전체'] + list(df_raw['company_size'].unique())
selected_size = st.sidebar.selectbox("기업 규모 선택", all_sizes)

# 데이터 필터링 적용
df = df_raw.copy()
if selected_category != '전체':
    df = df[df['category'] == selected_category]
if selected_experience != '전체':
    df = df[df['experience'] == selected_experience]
if selected_size != '전체':
    df = df[df['company_size'] == selected_size]

st.sidebar.markdown("---")
st.sidebar.info("데이터 출처: 사람인 마케터 공고\n\n최종 업데이트: 2026.07")

# ---------------------------------------------------------
# 메인 화면 UI
# ---------------------------------------------------------
st.title("📊 마케터 채용 시장 심층 대시보드")
st.markdown("탐색적 데이터 분석(EDA)과 텍스트 마이닝을 통한 마케터 취업/이직 핵심 인사이트를 제공합니다.")

# KPI 카드
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="분석 대상 공고 수", value=f"{len(df):,}건")
with col2:
    top_cat = df['category'].mode()[0] if not df.empty else "N/A"
    st.metric(label="최다 채용 직무군", value=top_cat)
with col3:
    high_rf = len(df[df['rf_score'] >= 2])
    rf_pct = (high_rf / len(df) * 100) if len(df) > 0 else 0
    st.metric(label="블랙기업 위험 공고율", value=f"{rf_pct:.1f}%")
with col4:
    startup_cnt = len(df[df['company_size'] == '스타트업'])
    st.metric(label="스타트업 공고 수", value=f"{startup_cnt}건")

st.markdown("---")

if df.empty:
    st.warning("선택한 필터 조건에 맞는 데이터가 없습니다. 필터를 조정해 주세요.")
    st.stop()

# ---------------------------------------------------------
# 탭 구성
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📌 기본 직무 요약", "🛠 핵심 스펙 분석", "🚨 기업 문화 & Action Item"])

# ==========================================
# TAB 1: 기본 요약
# ==========================================
with tab1:
    st.subheader("1. 요구 경력 및 직무군 분포")
    
    c1, c2 = st.columns(2)
    with c1:
        # 경력 분포 Bar Chart
        exp_counts = df['experience'].value_counts().reset_index()
        exp_counts.columns = ['experience', 'count']
        fig_exp = px.bar(exp_counts, x='experience', y='count', title="요구 경력 분포",
                         text='count', color='count', color_continuous_scale='Blues')
        fig_exp.update_layout(xaxis_title="경력", yaxis_title="공고 수", showlegend=False)
        st.plotly_chart(fig_exp, use_container_width=True)
        
    with c2:
        # 직무군 Pie Chart
        cat_counts = df['category'].value_counts().reset_index()
        cat_counts.columns = ['category', 'count']
        fig_cat = px.pie(cat_counts, names='category', values='count', title="직무군별 채용 비중", hole=0.4)
        fig_cat.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("2. 기업 규모별 요구 경력 차이")
    size_exp = df.groupby(['company_size', 'experience']).size().reset_index(name='count')
    fig_size_exp = px.bar(size_exp, x='company_size', y='count', color='experience', barmode='stack',
                          title="스타트업 vs 대기업 경력 요건 비교")
    st.plotly_chart(fig_size_exp, use_container_width=True)

# ==========================================
# TAB 2: 고급 스펙 분석
# ==========================================
with tab2:
    st.subheader("💡 채용 공고 내 필수/우대 스펙 등장 빈도")
    st.markdown("JD 본문(상세내용)에 기재된 툴 스택과 경험 요건을 텍스트 마이닝하여 추출한 결과입니다.")
    
    @st.cache_data
    def get_skill_counts(text_series, _pattern_dict):
        counts = {k: 0 for k in _pattern_dict.keys()}
        for text in text_series:
            for key, pattern in _pattern_dict.items():
                if re.search(pattern, text):
                    counts[key] += 1
        return pd.DataFrame(list(counts.items()), columns=['Keyword', 'Count']).sort_values('Count', ascending=True)

    skills_df = get_skill_counts(df['detail_text'].tolist(), SKILLS)
    exp_df = get_skill_counts(df['detail_text'].tolist(), EXP)

    c3, c4 = st.columns(2)
    with c3:
        fig_skills = px.bar(skills_df, x='Count', y='Keyword', orientation='h', 
                            title="하드스킬 & 툴 스택", text='Count', color='Count', color_continuous_scale='Teal')
        fig_skills.update_layout(xaxis_title="출현 공고 수", yaxis_title="")
        st.plotly_chart(fig_skills, use_container_width=True)
        
    with c4:
        fig_exp_req = px.bar(exp_df, x='Count', y='Keyword', orientation='h', 
                             title="경험 요건", text='Count', color='Count', color_continuous_scale='Purp')
        fig_exp_req.update_layout(xaxis_title="출현 공고 수", yaxis_title="")
        st.plotly_chart(fig_exp_req, use_container_width=True)

# ==========================================
# TAB 3: 기업 문화 & Action Item
# ==========================================
with tab3:
    st.subheader("🚨 '블랙기업' 위험 시그널 모니터링")
    st.markdown("공고문에 내포된 과도한 업무 강도, 모호한 R&R, 야근 등을 암시하는 키워드 분포입니다.")
    
    rf_df = get_skill_counts(df['detail_text'].tolist(), RED_FLAGS)
    fig_rf = px.bar(rf_df, x='Keyword', y='Count', title="위험 시그널 출현 빈도", 
                    text='Count', color='Count', color_continuous_scale='Reds')
    st.plotly_chart(fig_rf, use_container_width=True)
    
    st.error(f"⚠️ 현재 필터링된 {len(df)}건 중 **{high_rf}건({rf_pct:.1f}%)**의 공고가 위험 시그널 키워드를 2개 이상 포함하고 있습니다.")

    st.markdown("---")
    st.subheader("🎯 구직자 Action Item 요약")
    st.info("""
    **✅ 지금 당장 갖춰야 할 필수 스펙 TOP 3 (기본기)**
    1. **에이전시/대행사 경험**: 경험 요건 1위. 멀티태스킹과 협업 증명의 최고 무기입니다.
    2. **콘텐츠 디자인 (Adobe/Figma)**: 하드스킬 1, 2위. 단순 기획을 넘어 시각화 능력을 절대적으로 요구합니다.
    3. **SNS 운영 경험**: 바닥부터 채널을 키워본 성과 위주 경험이 필요합니다.
    
    **📈 가성비 우대 스펙 TOP 3 (서류 합격 치트키)**
    1. **GA4 / 퍼포먼스 데이터**: 연봉 테이블을 바꾸는 강력한 무기입니다.
    2. **기초 숏폼 편집 (프리미어)**: 우대사항 최상위권. 고도의 기술보다 컷편집/자막 능력을 봅니다.
    3. **협업 툴 (Notion/Slack)**: 스타트업 조직 문화 핏(Fit)을 맞추는 가장 쉬운 방법입니다.
    """)
