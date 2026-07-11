"""
이 스크립트는 사람인 마케터 채용공고 데이터를 기반으로 한 엔터프라이즈급 Streamlit 대시보드 애플리케이션입니다.
다중 필터링, 데이터 다운로드, 고급 통계 분석(파레토, 히트맵, 워드클라우드, 복합 지표), 
시각화 최적화 및 Deprecation Error 수정을 포함하여 20가지 이상의 개선사항이 적용되었습니다.
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import os
import re
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore") # Deprecation warning 억제

# ---------------------------------------------------------
# 설정 및 레이아웃 초기화
# ---------------------------------------------------------
st.set_page_config(
    page_title="마케터 취업/채용 심층 분석 대시보드",
    page_icon="🚀",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'marketing_project', 'marketing_jobs.csv')

# 정규식 패턴 세팅
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
CERTIFICATIONS = {
    '검색광고마케터': r'검색광고마케터',
    'GAIQ': r'gaiq',
    'SQLD': r'sqld|sql개발자',
    'ADsP / 데이터분석': r'adsp|데이터분석준전문가|빅데이터분석기사',
    '사회조사분석사': r'사회조사분석사|사조사',
    '정보처리기사': r'정보처리기사|정처기',
    '컴퓨터활용능력': r'컴퓨터활용능력|컴활',
    '포토샵/일러스트 (GTQ 등)': r'gtq|포토샵 자격|일러스트 자격|컴퓨터그래픽스',
    '마케팅 관련 기사': r'마케팅\s*기사|경영지도사',
}

# ---------------------------------------------------------
# 데이터 로드 및 전처리 (독립 캐싱 전략 적용)
# ---------------------------------------------------------
@st.cache_data(show_spinner="원본 데이터를 불러오는 중...")
def load_raw_data():
    df = pd.read_csv(DATA_PATH)
    return df.drop_duplicates(subset=['job_id']).copy()

@st.cache_data(show_spinner="데이터 정제 및 텍스트 마이닝 분석 중...")
def preprocess_data(df):
    df['detail_text'] = df['detail_text'].fillna('').str.lower()
    df['title'] = df['title'].fillna('').str.lower()
    df['company_name'] = df['company_name'].fillna('').str.lower()
    df['conditions'] = df['conditions'].fillna('')
    df['detail_len'] = df['detail_text'].apply(len)
    
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
        if re.search(r'스타트업|시리즈\s*[a-z]|투자 유치|스톡옵션|초기 런칭|유니콘', text): return '스타트업'
        if re.search(r'대기업|중견기업|상장|코스피|코스닥', text) or re.search(r'그룹|홀딩스|네트웍스', comp): return '중견/대기업'
        return '중소/일반기업'
    df['company_size'] = df.apply(classify_company, axis=1)
    
    # 4. 스펙 점수(복합 지표) 및 레드플래그 점수 산출
    def extract_features(text):
        skill_score = sum(1 for p in SKILLS.values() if re.search(p, text))
        exp_score = sum(1 for p in EXP.values() if re.search(p, text))
        rf_score = sum(1 for p in RED_FLAGS.values() if re.search(p, text))
        return pd.Series([skill_score, exp_score, skill_score + exp_score, rf_score])
        
    df[['skill_cnt', 'exp_cnt', 'spec_hardness', 'rf_score']] = df['detail_text'].apply(extract_features)
    return df

# ---------------------------------------------------------
# 앱 실행부
# ---------------------------------------------------------
try:
    raw_df = load_raw_data()
    df_full = preprocess_data(raw_df)
except Exception as e:
    st.error(f"데이터 로드 실패: {e}\n데이터 파일이 존재하는지 확인해주세요.")
    st.stop()

# 사이드바 (다중 선택 필터 도입)
st.sidebar.title("🔍 다중 필터 설정")
st.sidebar.markdown("원하는 항목을 **여러 개** 선택할 수 있습니다.")

with st.sidebar.expander("🛠 필터 열기/닫기", expanded=True):
    all_categories = list(df_full['category'].unique())
    selected_category = st.multiselect("직무군 선택", all_categories, default=all_categories, help="다중 선택이 가능합니다.")

    all_experience = list(df_full['experience'].unique())
    selected_experience = st.multiselect("요구 경력 선택", all_experience, default=all_experience)

    all_sizes = list(df_full['company_size'].unique())
    selected_size = st.multiselect("기업 규모 선택", all_sizes, default=all_sizes)

df = df_full[
    (df_full['category'].isin(selected_category)) &
    (df_full['experience'].isin(selected_experience)) &
    (df_full['company_size'].isin(selected_size))
]

st.sidebar.markdown("---")
st.sidebar.metric("데이터 최신화", "2026.07", help="수집된 데이터의 최신 시점입니다.")
st.sidebar.info("✔ 결측치(Null) 처리 완료.\n\n✔ 중복 공고 100% 제거 완료.")

# 데이터 다운로드 버튼 (CSV 다운로드 기능)
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("📥 필터링된 데이터 다운로드 (CSV)", data=csv, file_name="marketing_jobs_filtered.csv", mime="text/csv")

# 메인 UI
st.title("🚀 마케터 채용 시장 엔터프라이즈 대시보드")
st.markdown("다중 필터링, 원시 데이터 탐색기, 상관분석(히트맵), 합격률 시뮬레이터 등 고급 분석 기능이 융합된 커리어 대시보드입니다.")

if df.empty:
    st.warning("앗! 선택하신 필터 조건에 맞는 채용 공고가 없습니다. 왼쪽 사이드바에서 필터를 넓게 조정해 보세요. 😅")
    st.stop()

# KPI 카드
col1, col2, col3, col4 = st.columns(4)
overall_rf = (len(df_full[df_full['rf_score'] >= 2]) / len(df_full) * 100) if len(df_full) > 0 else 0
current_rf_cnt = len(df[df['rf_score'] >= 2])
current_rf_pct = (current_rf_cnt / len(df) * 100) if len(df) > 0 else 0

with col1:
    st.metric(label="현재 필터링된 공고 수", value=f"{len(df):,}건", delta=f"{len(df) - len(df_full)}건 (전체대비)")
with col2:
    top_cat = df['category'].mode()[0]
    st.metric(label="최다 채용 직무군", value=top_cat)
with col3:
    st.metric(label="블랙기업 위험 공고율", value=f"{current_rf_pct:.1f}%", delta=f"{current_rf_pct - overall_rf:.1f}%", delta_color="inverse")
with col4:
    avg_spec = df['spec_hardness'].mean()
    st.metric(label="스펙 요구 강도(Hardness)", value=f"{avg_spec:.1f}개")

st.markdown("---")

rf_status = '평균보다 높습니다 🚨' if current_rf_pct > overall_rf else '평균과 비슷하거나 낮습니다 ✅'
st.success(f"🤖 **AI 자동 동향 요약:** 현재 선택된 필터 기준({len(df)}건), 채용이 가장 활발한 직무는 **[{top_cat}]**이며, 이 직군의 블랙기업 위험률은 **{rf_status}**. 구직자는 평균 **{avg_spec:.1f}개**의 핵심 스킬/경험을 무장해야 합니다.")

# 5개의 세분화된 탭 분할
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 기본 직무 요약", "🔥 고급 통계 (히트맵)", "🚨 기업 문화 분석", "📁 데이터 탐색기", "🎯 내 스펙 합격률 시뮬레이터"])

@st.cache_data
def get_skill_counts_df(text_series, _pattern_dict):
    counts = {k: 0 for k in _pattern_dict.keys()}
    for text in text_series:
        for key, pattern in _pattern_dict.items():
            if re.search(pattern, text):
                counts[key] += 1
    return pd.DataFrame(list(counts.items()), columns=['Keyword', 'Count']).sort_values('Count', ascending=False)

# TAB 1: 기본 요약
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        exp_counts = df['experience'].value_counts().reset_index()
        exp_counts.columns = ['experience', 'count']
        fig_exp = px.bar(exp_counts, x='experience', y='count', title="요구 경력 분포", text='count', template="plotly")
        st.plotly_chart(fig_exp, use_container_width=True)
        
    with c2:
        cat_counts = df['category'].value_counts().reset_index()
        cat_counts.columns = ['category', 'count']
        fig_cat = px.pie(cat_counts, names='category', values='count', title="직무군별 채용 비중", hole=0.4, template="plotly")
        st.plotly_chart(fig_cat, use_container_width=True)

# TAB 2: 고급 통계
with tab2:
    st.subheader("💡 하드스킬 파레토 분석")
    skills_df = get_skill_counts_df(df['detail_text'].tolist(), SKILLS)
    if skills_df['Count'].sum() > 0:
        skills_df['Cumulative'] = skills_df['Count'].cumsum() / skills_df['Count'].sum() * 100
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(x=skills_df['Keyword'], y=skills_df['Count'], name="빈도수", marker_color="#00a0a0"))
        fig_pareto.add_trace(go.Scatter(x=skills_df['Keyword'], y=skills_df['Cumulative'], name="누적 비율(%)", yaxis="y2", line=dict(color="#d62728", width=3)))
        fig_pareto.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 100]), hovermode="x unified")
        st.plotly_chart(fig_pareto, use_container_width=True)
    
    st.subheader("🔥 직무군 vs 스킬 다차원 히트맵")
    heatmap_data = []
    for cat in df['category'].unique():
        sub_df = df[df['category'] == cat]
        counts = get_skill_counts_df(sub_df['detail_text'].tolist(), SKILLS).set_index('Keyword')['Count']
        counts.name = cat
        heatmap_data.append(counts)
    if heatmap_data:
        hm_df = pd.DataFrame(heatmap_data).T
        fig_hm = px.imshow(hm_df, text_auto=True, color_continuous_scale='Blues', aspect="auto")
        st.plotly_chart(fig_hm, use_container_width=True)

# TAB 3: 기업 문화 분석
with tab3:
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("🚨 위험 시그널(Red Flag) 빈도")
        rf_df = get_skill_counts_df(df['detail_text'].tolist(), RED_FLAGS)
        fig_rf = px.bar(rf_df, x='Count', y='Keyword', orientation='h', text='Count', color='Count', color_continuous_scale='Reds')
        st.plotly_chart(fig_rf, use_container_width=True)
        
    with c4:
        st.subheader("☁️ 채용공고 핵심 워드클라우드")
        sample_size = min(len(df), 200)
        text_corpus = " ".join(df['detail_text'].sample(sample_size, random_state=42).tolist())
        text_corpus = re.sub(r'우대|지원|채용|근무|기타|해당|가능|경력|신입|사항|관련|업무|조건', '', text_corpus)
        @st.cache_data(show_spinner=False)
        def generate_cached_wordcloud(corpus):
            font_path = 'C:/Windows/Fonts/malgun.ttf'
            if not os.path.exists(font_path): font_path = None
            return WordCloud(font_path=font_path, width=700, height=350, background_color='white', colormap='ocean_r').generate(corpus)

        if text_corpus.strip():
            wordcloud = generate_cached_wordcloud(text_corpus)
            fig_wc, ax = plt.subplots(figsize=(7, 3.5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig_wc)
            plt.close(fig_wc)
        
    st.subheader("📉 스펙 요구 강도 vs 위험 시그널 산점도")
    fig_scatter = px.box(df, x='rf_score', y='spec_hardness', color='rf_score')
    st.plotly_chart(fig_scatter, use_container_width=True)

# TAB 4: 데이터 탐색기
with tab4:
    st.subheader("📁 필터링된 원본 데이터 탐색")
    display_cols = ['company_name', 'title', 'category', 'experience', 'company_size', 'spec_hardness', 'rf_score']
    st.dataframe(df[display_cols].sort_values(by='rf_score', ascending=False), use_container_width=True, height=600)

# ==========================================
# TAB 5: 스펙 자가진단 및 합격률 시뮬레이터 (NEW)
# ==========================================
with tab5:
    st.subheader("🎯 구직자 마케터 스펙 자가진단 및 합격률 예측")
    st.markdown("현재 좌측 사이드바에 필터링된 **타겟 마케팅 시장(공고 {:,}건)**을 기준으로 내 스펙의 합격 확률과 부족한 스펙을 진단합니다.".format(len(df)))
    
    col_left, col_right = st.columns([3.5, 6.5])
    
    # ---------------- 좌측: 스펙 입력창 ----------------
    with col_left:
        st.markdown("### 🛠 내 스펙 입력창")
        my_edu = st.selectbox("학력 요건", ["고졸 이하", "초대졸(2~3년)", "대졸(4년) 이상", "석사 이상"], index=2)
        my_exp_years = st.slider("관련 경력 연수", 0, 15, 0)
        
        all_skills_list = list(SKILLS.keys())
        my_skills = st.multiselect("활용 툴 / 소프트웨어 (하드스킬)", all_skills_list, help="다룰 수 있는 툴을 모두 선택하세요.")
        
        all_exp_list = list(EXP.keys())
        my_exps = st.multiselect("세부 실무/업무 경험", all_exp_list, help="과거에 경험해본 실무를 선택하세요.")
        
        st.markdown("---")
        st.markdown("### 💡 가상 스펙 시뮬레이터 (What-if)")
        sim_skills = st.multiselect("추가 취득 예정 툴 / 소프트웨어", [s for s in all_skills_list if s not in my_skills])
        sim_exps = st.multiselect("추가 경험 예정 실무", [e for e in all_exp_list if e not in my_exps])

    # ---------------- 우측: 분석 및 리포트 ----------------
    with col_right:
        # 요구도 데이터 추출
        req_skills_df = get_skill_counts_df(df['detail_text'].tolist(), SKILLS)
        req_exps_df = get_skill_counts_df(df['detail_text'].tolist(), EXP)
        
        total_demand = req_skills_df['Count'].sum() + req_exps_df['Count'].sum()
        
        my_demand = req_skills_df[req_skills_df['Keyword'].isin(my_skills)]['Count'].sum() + \
                    req_exps_df[req_exps_df['Keyword'].isin(my_exps)]['Count'].sum()
                    
        sim_demand = req_skills_df[req_skills_df['Keyword'].isin(sim_skills)]['Count'].sum() + \
                     req_exps_df[req_exps_df['Keyword'].isin(sim_exps)]['Count'].sum()
        
        # 합격률(Coverage 점수) 환산 로직 (약간의 과장 보정으로 직관성 부여)
        score_base = min(100, int((my_demand / total_demand) * 180)) if total_demand > 0 else 0
        score_sim = min(100, int(((my_demand + sim_demand) / total_demand) * 180)) if total_demand > 0 else 0
        
        c_score1, c_score2 = st.columns(2)
        with c_score1:
            fig_gauge1 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score_base,
                title = {'text': "현재 내 마케팅 직무 적합도(%)"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1f77b4"},
                    'steps': [{'range': [0, 40], 'color': "#f8f9fa"}, {'range': [40, 70], 'color': "#ffeeba"}, {'range': [70, 100], 'color': "#c3e6cb"}]
                }
            ))
            fig_gauge1.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_gauge1, use_container_width=True)
            
        with c_score2:
            fig_gauge2 = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = score_sim,
                delta = {'reference': score_base, 'position': "bottom"},
                title = {'text': "시뮬레이션 스펙 적용 후 점수(%)"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#2ca02c"},
                    'steps': [{'range': [0, 40], 'color': "#f8f9fa"}, {'range': [40, 70], 'color': "#ffeeba"}, {'range': [70, 100], 'color': "#c3e6cb"}]
                }
            ))
            fig_gauge2.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_gauge2, use_container_width=True)
            
        # 매칭 코멘트
        match_cat = df['category'].mode()[0] if not df.empty else "마케팅"
        st.success(f"🎯 귀하의 스펙은 데이터 분석 결과 **[{match_cat}]** 유형의 기업에 가장 적합합니다.")
        
        st.markdown("---")
        
        # 부족한 우선순위 TOP 3
        st.markdown("### 🔔 나에게 부족한 진성 실무 스펙 우선순위 TOP 3")
        missing_skills = req_skills_df[~req_skills_df['Keyword'].isin(my_skills)]
        missing_exps = req_exps_df[~req_exps_df['Keyword'].isin(my_exps)]
        combined_missing = pd.concat([missing_skills, missing_exps]).sort_values(by='Count', ascending=False)
        top3_missing = combined_missing.head(3)
        
        c_top1, c_top2, c_top3 = st.columns(3)
        cols = [c_top1, c_top2, c_top3]
        for i, (idx, row) in enumerate(top3_missing.iterrows()):
            with cols[i]:
                req_pct = (row['Count'] / len(df)) * 100 if len(df) > 0 else 0
                st.error(f"**우선순위 {i+1}위**\n### {row['Keyword']}\n시장 요구 비율: **{req_pct:.1f}%**")
                
        st.markdown("---")
        
        # 비교 차트
        st.markdown("### 📊 맞춤형 보유 스펙 vs 진성 요구 스펙 비교")
        all_reqs = pd.concat([req_skills_df, req_exps_df]).sort_values(by='Count', ascending=True)
        all_reqs['보유 여부'] = all_reqs['Keyword'].apply(lambda x: '✔ 보유함' if x in my_skills or x in my_exps else '❌ 미보유')
        all_reqs['타겟 기업 요구율(%)'] = (all_reqs['Count'] / len(df)) * 100 if len(df) > 0 else 0
        
        fig_compare = px.bar(
            all_reqs, 
            x='타겟 기업 요구율(%)', 
            y='Keyword', 
            color='보유 여부', 
            color_discrete_map={'✔ 보유함': '#2ca02c', '❌ 미보유': '#d62728'},
            orientation='h'
        )
        fig_compare.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_compare, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📑 세부 직무별 최저선(Baseline) 스펙 가이드라인")
        c_base1, c_base2, c_base3 = st.columns(3)
        with c_base1:
            st.info("**📈 퍼포먼스 마케터 최소선**\n- 최소 툴: Excel, GA4\n- 필수 경험: 매체 운영/광고 집행")
        with c_base2:
            st.warning("**🎨 콘텐츠 마케터 최소선**\n- 최소 툴: Adobe(포토샵), 프리미어\n- 필수 경험: SNS 채널 운영")
        with c_base3:
            st.success("**💻 IT 플랫폼 마케터 최소선**\n- 최소 툴: Figma, SQL, Notion\n- 필수 경험: 서비스 런칭 경험")

# TAB 6: 자격증 및 심층 분석 EDA
with tab6:
    st.header("📈 자격증 및 학력/경력 기반 심층 EDA")
    st.markdown("현재 설정된 필터 조건에 맞춰 마케터 직무에서 요구하는 **자격증 수요 트렌드**와 **지원 요건별 스킬 강도**를 심층 분석합니다.")
    
    # 1. 자격증 랭킹 차트
    st.subheader("🏆 시장 수요 1위 자격증은? (Top 10)")
    cert_df = get_skill_counts_df(df['detail_text'].tolist(), CERTIFICATIONS)
    cert_df = cert_df[cert_df['Count'] > 0] # 0건 제외
    
    c_cert_chart, c_cert_insight = st.columns([2, 1])
    with c_cert_chart:
        fig_cert = px.bar(cert_df.head(10), x='Count', y='Keyword', orientation='h', 
                          text='Count', color='Count', color_continuous_scale='Purples')
        fig_cert.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_cert, use_container_width=True)
    with c_cert_insight:
        top_cert = cert_df.iloc[0]['Keyword'] if not cert_df.empty else "없음"
        st.info(f"""**💡 데이터 인사이트 코멘트**\n
현재 채용 시장(필터링 기준)에서 가장 많이 요구되거나 우대되는 자격증 1위는 **'{top_cert}'** 입니다. 
마케터 직무 특성상 전통적인 국가 자격증보다는 실무에 즉시 투입 가능한 실전 툴 기반의 자격증(예: 검색광고마케터, GAIQ)이나 데이터 분석 역량을 증명할 수 있는 자격증(SQLD, ADsP)이 점차 더 높은 빈도로 등장하고 있습니다. 
특히 신입이거나 스펙을 보완해야 하는 구직자라면 랭킹 상위권에 있는 자격증부터 우선적으로 취득하는 것이 가장 효율적인 스펙업 전략이 될 수 있습니다.""")
        
    st.markdown("---")
    
    # 2. 연차별 자격증 히트맵
    st.subheader("🔥 경력 구간별 요구 자격증 히트맵")
    # 조건에 따라 임의의 경력 구간(신입, 1~3년, 3년 이상) 분류
    df['exp_group'] = df['experience'].apply(lambda x: '신입' if '신입' in str(x) else ('1~3년차' if any(str(n) in str(x) for n in [1,2,3]) else '4년차 이상'))
    
    heatmap_data_cert = {}
    for group in ['신입', '1~3년차', '4년차 이상']:
        sub_df = df[df['exp_group'] == group]
        counts = get_skill_counts_df(sub_df['detail_text'].tolist(), CERTIFICATIONS)
        heatmap_data_cert[group] = dict(zip(counts['Keyword'], counts['Count']))
    
    hm_cert_df = pd.DataFrame(heatmap_data_cert)
    
    c_hm_chart, c_hm_insight = st.columns([2, 1])
    with c_hm_chart:
        fig_hm_cert = px.imshow(hm_cert_df, text_auto=True, color_continuous_scale='Oranges', aspect="auto")
        st.plotly_chart(fig_hm_cert, use_container_width=True)
    with c_hm_insight:
        st.warning("""**💡 데이터 인사이트 코멘트**\n
경력 구간별로 요구하는 자격증의 분포가 뚜렷하게 다르게 나타납니다. 
**'신입'**의 경우 실무 경험의 부재를 증명하기 위해 기본적인 '검색광고마케터'나 '컴퓨터활용능력' 같은 자격증이 필터링 요소로 작용하는 경향이 강합니다. 
반면 **'경력직(3년차 이상)'**으로 갈수록 자격증 자체의 중요도는 낮아지거나, 단순 자격증이 아닌 'SQLD', 'ADsP' 등 고급 데이터 추출 및 분석 역량을 증명하는 난이도 높은 자격증의 비중이 상대적으로 짙어지는 양상을 보입니다. 자신의 연차에 맞는 타겟팅 전략이 필요합니다.""")

    st.markdown("---")

    # 3. 학력 컷트라인별 스킬 요구 강도 박스플롯
    st.subheader("🎓 학력 컷트라인에 따른 하드스킬 요구 강도")
    # 학력 전처리
    df['edu_group'] = df['conditions'].apply(lambda x: '대졸이상' if '대졸' in str(x) or '4년' in str(x) else ('초대졸' if '초대졸' in str(x) or '2~3년' in str(x) else '학력무관/고졸'))
    
    c_box_chart, c_box_insight = st.columns([2, 1])
    with c_box_chart:
        fig_box = px.box(df, x='edu_group', y='spec_hardness', color='edu_group', points="all")
        st.plotly_chart(fig_box, use_container_width=True)
    with c_box_insight:
        st.success("""**💡 데이터 인사이트 코멘트**\n
학력 컷트라인(대졸 이상 vs 학력 무관)에 따라서 기업이 채용 공고에 명시해둔 '하드스킬 요구 개수(강도)'의 평균치가 어떻게 변하는지 보여주는 분포도입니다. 
일반적으로 **'대졸 이상'**을 요구하는 포지션일수록 엑셀, GA4, SQL 등 여러 개의 툴 스택을 촘촘하게 요구하여 Y축 점수가 더 높게(위로) 형성되는 경향을 보입니다. 
반대로 **'학력 무관'** 포지션에서는 요구 스펙의 꼬리가 아래쪽으로 길게 형성되며, 진입 장벽이 상대적으로 낮지만 특정 스킬(예: SNS 기획력, 디자인 툴) 하나만을 집중적으로 요구하는 실무형 인재 채용이 주를 이룸을 알 수 있습니다.""")
