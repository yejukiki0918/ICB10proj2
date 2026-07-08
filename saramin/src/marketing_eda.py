"""
마케터 채용공고 1,000건을 대상으로 탐색적 데이터 분석(EDA)을 수행하는 스크립트입니다.
주요 기능:
- 데이터를 로드하여 결측치, 중복값을 확인합니다.
- 조건(경력, 학력, 지역) 및 직무군을 파싱합니다.
- Matplotlib을 이용해 10종의 시각화 차트를 `images/` 경로에 저장합니다.
- 데이터 통계 및 시각화 요약 결과를 JSON 파일로 저장합니다.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'marketing_project', 'marketing_jobs.csv')
IMG_DIR = os.path.join(BASE_DIR, 'images')
os.makedirs(IMG_DIR, exist_ok=True)
JSON_OUTPUT = os.path.join(BASE_DIR, 'report', 'eda_summary.json')
os.makedirs(os.path.dirname(JSON_OUTPUT), exist_ok=True)

STOP_WORDS = set([
    '마케터', '마케팅', '지원', '근무', '업무', '우대', '채용', '관련', '진행', '이상', '경험', '가능한', 
    '있는', '대한', '우대사항', '자격요건', '제출', '서류', '필수', '해당', '보유자', '경력', '신입', '담당업무', 
    '지원자격', '전형절차', '근무조건', '접수기간', '방법', '복리후생', '회사', '기업', '우리', '함께', '성장', 
    '이해도', '경력자', '기타', '사항', '이력서', '포트폴리오', '면접', '합격', '경우', '마케터로서', '위한'
])

def load_and_clean_data():
    df = pd.read_csv(DATA_PATH)
    # 중복 제거 (job_id 기준)
    duplicates = df.duplicated(subset=['job_id']).sum()
    df = df.drop_duplicates(subset=['job_id'])
    
    # conditions 파싱
    def parse_cond(c):
        if not isinstance(c, str): return pd.Series(['무관', '학력무관', '지역무관'])
        parts = [p.strip() for p in c.split('/')]
        exp = parts[0] if len(parts) > 0 else '무관'
        edu = parts[1] if len(parts) > 1 else '학력무관'
        loc = parts[3].split(' ')[0] if len(parts) > 3 else '지역무관'
        return pd.Series([exp, edu, loc])
        
    df[['experience', 'education', 'location']] = df['conditions'].apply(parse_cond)
    
    # 2. 직무 카테고리
    def categorize(title):
        t = str(title).lower()
        if any(w in t for w in ['it', '개발', '앱', '웹', '플랫폼', '소프트웨어']): return 'IT/플랫폼'
        if any(w in t for w in ['퍼포먼스', '그로스', '데이터', 'ga', '분석']): return '퍼포먼스/데이터'
        if any(w in t for w in ['콘텐츠', '브랜드', 'sns', '디자인', '유튜브']): return '콘텐츠/브랜드'
        if any(w in t for w in ['b2b', '영업', '제휴', '세일즈']): return 'B2B/영업'
        return '일반/종합'
        
    df['job_category'] = df['title'].apply(categorize)
    
    # 3. 필수요건 / 우대사항 텍스트 추출 (정규식 기반)
    def extract_section(text, start_kws, end_kws):
        if not isinstance(text, str): return ""
        for sk in start_kws:
            start_idx = text.find(sk)
            if start_idx != -1:
                end_idx = len(text)
                for ek in end_kws:
                    idx = text.find(ek, start_idx + len(sk))
                    if idx != -1 and idx < end_idx:
                        end_idx = idx
                content = text[start_idx + len(sk) : end_idx].strip()
                return re.sub(r'[^\w\s]', ' ', content)
        return ""
        
    df['req_text'] = df['detail_text'].apply(lambda x: extract_section(x, ['자격요건', '지원자격', '자격 요건', '필수사항'], ['우대사항', '근무조건', '전형절차', '복리후생', '접수기간', '담당업무']))
    df['pref_text'] = df['detail_text'].apply(lambda x: extract_section(x, ['우대사항', '우대조건', '우대 사항'], ['근무조건', '전형절차', '복리후생', '접수기간']))
    
    return df, duplicates

def extract_keywords(texts, top_n=30):
    valid_texts = [str(t) for t in texts if pd.notna(t) and len(str(t)) > 10]
    if not valid_texts: return []
    
    cleaned = []
    for t in valid_texts:
        words = re.findall(r'\w+', t)
        filtered = [w for w in words if w not in STOP_WORDS and len(w) > 1 and not w.isdigit()]
        cleaned.append(" ".join(filtered))
        
    try:
        vec = TfidfVectorizer(max_features=top_n)
        tfidf = vec.fit_transform(cleaned)
        scores = np.array(tfidf.sum(axis=0)).flatten()
        vocab = vec.get_feature_names_out()
        sorted_kw = sorted(zip(vocab, scores), key=lambda x: x[1], reverse=True)
        return sorted_kw
    except Exception as e:
        print("TF-IDF Error:", e)
        return []

def plot_and_save(fig, filename):
    plt.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, filename), dpi=150)
    plt.close(fig)

def run_eda():
    print("데이터 로딩 중...")
    df, dups = load_and_clean_data()
    print(f"데이터 로드 완료: {len(df)}건 (중복: {dups}건)")
    
    summary = {
        "basic_info": {
            "total_rows": len(df),
            "duplicates_removed": int(dups)
        },
        "stats": {}
    }
    
    # 1. 요구 경력 분포
    exp_counts = df['experience'].value_counts()
    summary["stats"]["experience"] = exp_counts.to_dict()
    fig, ax = plt.subplots(figsize=(10, 6))
    exp_counts.head(15).plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title('요구 경력별 공고 수 분포')
    plot_and_save(fig, 'plot1_experience.png')
    
    # 2. 학력 제한 분포
    edu_counts = df['education'].value_counts()
    summary["stats"]["education"] = edu_counts.to_dict()
    fig, ax = plt.subplots(figsize=(8, 8))
    edu_counts.head(7).plot(kind='pie', autopct='%1.1f%%', startangle=90, cmap='Pastel1', ax=ax)
    ax.set_title('요구 학력 제한 분포')
    ax.set_ylabel('')
    plot_and_save(fig, 'plot2_education.png')
    
    # 3. 근무 지역 Top 10
    loc_counts = df['location'].value_counts().head(10)
    summary["stats"]["location"] = loc_counts.to_dict()
    fig, ax = plt.subplots(figsize=(10, 6))
    loc_counts.plot(kind='bar', color='lightcoral', ax=ax)
    ax.set_title('근무 지역 Top 10')
    plot_and_save(fig, 'plot3_location.png')
    
    # 4. 직무 카테고리 분포 (Donut)
    cat_counts = df['job_category'].value_counts()
    summary["stats"]["job_category"] = cat_counts.to_dict()
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(cat_counts, labels=cat_counts.index, autopct='%1.1f%%', pctdistance=0.85, colors=plt.cm.Set3.colors)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    ax.set_title('세부 직무군별 채용 비중')
    plot_and_save(fig, 'plot4_category.png')
    
    # 5. 카테고리별 요구 경력 (Grouped)
    cat_exp = pd.crosstab(df['job_category'], df['experience'].apply(lambda x: x if x in ['경력무관', '신입'] else '경력'))
    summary["stats"]["category_vs_experience"] = cat_exp.to_dict()
    fig, ax = plt.subplots(figsize=(12, 6))
    cat_exp.plot(kind='bar', stacked=False, ax=ax, cmap='viridis')
    ax.set_title('직무군별 요구 경력 비교')
    plt.xticks(rotation=45)
    plot_and_save(fig, 'plot5_cat_exp.png')
    
    # 6. 주요 지역 vs 직무 카테고리 (Heatmap)
    top_locs = df['location'].value_counts().head(5).index
    loc_cat = pd.crosstab(df[df['location'].isin(top_locs)]['location'], df['job_category'])
    summary["stats"]["location_vs_category"] = loc_cat.to_dict()
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(loc_cat.values, cmap='YlOrRd')
    ax.set_xticks(np.arange(len(loc_cat.columns)))
    ax.set_yticks(np.arange(len(loc_cat.index)))
    ax.set_xticklabels(loc_cat.columns, rotation=45, ha='right')
    ax.set_yticklabels(loc_cat.index)
    plt.colorbar(im, ax=ax)
    ax.set_title('주요 지역과 직무군 교차 분석 히트맵')
    plot_and_save(fig, 'plot6_loc_cat.png')
    
    # 7. 학력 vs 경력 (Stacked)
    edu_exp = pd.crosstab(df['education'], df['experience'].apply(lambda x: '무관' if '무관' in x else '제한있음'))
    summary["stats"]["education_vs_experience"] = edu_exp.to_dict()
    fig, ax = plt.subplots(figsize=(10, 6))
    edu_exp.head(5).plot(kind='bar', stacked=True, ax=ax, cmap='Set2')
    ax.set_title('학력 제한 vs 경력 제한 스택드 차트')
    plt.xticks(rotation=45)
    plot_and_save(fig, 'plot7_edu_exp.png')
    
    # 8. 전체 TF-IDF 핵심 키워드 Top 30
    overall_kw = extract_keywords(df['detail_text'], 30)
    summary["stats"]["keywords_overall"] = [{"word": w, "score": s} for w, s in overall_kw]
    if overall_kw:
        words = [x[0] for x in overall_kw]
        scores = [x[1] for x in overall_kw]
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(words[::-1], scores[::-1], color='teal')
        ax.set_title('전체 공고 핵심 역량 키워드 Top 30 (TF-IDF)')
        plot_and_save(fig, 'plot8_kw_overall.png')
        
    # 9. 필수 자격요건 핵심 키워드
    req_kw = extract_keywords(df['req_text'], 20)
    summary["stats"]["keywords_required"] = [{"word": w, "score": s} for w, s in req_kw]
    if req_kw:
        words = [x[0] for x in req_kw]
        scores = [x[1] for x in req_kw]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(words, scores, color='darkorange')
        ax.set_title('마케터 필수 자격요건 핵심 키워드')
        plt.xticks(rotation=45)
        plot_and_save(fig, 'plot9_kw_req.png')
        
    # 10. 우대사항 핵심 키워드
    pref_kw = extract_keywords(df['pref_text'], 20)
    summary["stats"]["keywords_preferred"] = [{"word": w, "score": s} for w, s in pref_kw]
    if pref_kw:
        words = [x[0] for x in pref_kw]
        scores = [x[1] for x in pref_kw]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(words, scores, color='indigo')
        ax.set_title('마케터 우대사항 핵심 키워드')
        plt.xticks(rotation=45)
        plot_and_save(fig, 'plot10_kw_pref.png')

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("EDA 분석 완료!")

if __name__ == "__main__":
    run_eda()
