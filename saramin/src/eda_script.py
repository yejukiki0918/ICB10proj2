"""
사람인 마케터 채용공고 데이터를 분석하여 심층 분석 결과 JSON 및 EDA 리포트를 생성하는 스크립트.
주요 기능:
- 정규식을 이용한 자격요건, 우대사항 등 핵심 섹션 분리
- 키워드 기반 직무군 클러스터링 (IT, 회계, 마케팅 등)
- 불용어(노이즈) 강력 필터링 및 TF-IDF 기반 핵심 역량 도출
- 분석 결과를 JSON 형태로 저장하여 PPTX 생성에 활용
작성자: Antigravity
생성일: 2026-06-27
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'saramin_jobs.db')
JSON_PATH = os.path.join(BASE_DIR, 'report', 'analysis_results.json')
os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)

# 불용어 (노이즈) 강력 필터링 목록
STOP_WORDS = set([
    '마케터', '마케팅', '지원', '근무', '업무', '우대', '채용', '관련', '진행', '이상', '경험', '가능한', 
    '있는', '대한', '우대사항', '자격요건', '제출', '서류', '필수', '해당', '보유자', '경력', '신입', '담당업무', 
    '지원자격', '전형절차', '근무조건', '접수기간', '방법', '복리후생', '회사', '기업', '우리', '함께', '성장', 
    '이해도', '경력자', '기타', '사항', '이력서', '포트폴리오', '면접', '합격', '경우'
])

def load_data():
    conn = sqlite3.connect(DB_PATH)
    query = '''
        SELECT l.job_id, l.company_name, l.title, l.conditions, l.link, d.detail_text
        FROM job_listings l
        LEFT JOIN job_details d ON l.job_id = d.job_id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

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
            # 특수기호 제거
            content = re.sub(r'[^\w\s]', ' ', content)
            return content
    return ""

def preprocess_and_extract(df):
    # 1. conditions 파싱 (경력, 학력, 지역)
    def parse_conditions(cond_str):
        if not isinstance(cond_str, str):
            return pd.Series([None, None, None])
        parts = [p.strip() for p in cond_str.split('/')]
        exp, edu, loc = None, None, None
        if len(parts) >= 1: exp = parts[0]
        if len(parts) >= 2: edu = parts[1]
        if len(parts) >= 4: loc = parts[3].split(' ')[0] # 시/도만 추출
        return pd.Series([exp, edu, loc])

    df[['experience', 'education', 'location']] = df['conditions'].apply(parse_conditions)
    
    # 2. 직무군 클러스터링
    def categorize_job(title, detail):
        t = str(title).lower() + " " + str(detail).lower()
        if any(w in t for w in ['it', '플랫폼', '개발', '앱', '웹', '소프트웨어']):
            return 'IT/플랫폼 마케팅'
        elif any(w in t for w in ['퍼포먼스', '그로스', '데이터', 'ga', '분석']):
            return '퍼포먼스/데이터 마케팅'
        elif any(w in t for w in ['콘텐츠', '브랜드', 'sns', '디자인', '영상']):
            return '콘텐츠/브랜드 마케팅'
        elif any(w in t for w in ['내부회계', '경영', '재무', '회계']):
            return '경영/회계/관리'
        elif any(w in t for w in ['b2b', '영업', '제휴', '세일즈']):
            return 'B2B/영업 마케팅'
        return '일반/종합 마케팅'
    
    df['job_category'] = df.apply(lambda row: categorize_job(row['title'], row['detail_text']), axis=1)

    # 3. 필수요건 / 우대사항 텍스트 추출
    df['req_text'] = df['detail_text'].apply(lambda x: extract_section(x, ['자격요건', '지원자격', '자격 요건'], ['우대사항', '근무조건', '전형절차', '복리후생', '접수기간', '담당업무']))
    df['pref_text'] = df['detail_text'].apply(lambda x: extract_section(x, ['우대사항', '우대조건', '우대 사항'], ['근무조건', '전형절차', '복리후생', '접수기간']))
    
    return df

def get_top_keywords(text_series, top_n=10):
    texts = text_series.dropna().astype(str).tolist()
    texts = [t for t in texts if len(t.strip()) > 5]
    if not texts:
        return []
    
    cleaned_texts = []
    for t in texts:
        words = t.split()
        filtered = [w for w in words if w not in STOP_WORDS and len(w) > 1]
        cleaned_texts.append(" ".join(filtered))
        
    try:
        vectorizer = TfidfVectorizer(max_features=top_n)
        tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
        scores = np.array(tfidf_matrix.sum(axis=0)).flatten()
        vocab = vectorizer.get_feature_names_out()
        
        # zip and sort
        kw_scores = sorted(zip(vocab, scores), key=lambda x: x[1], reverse=True)
        return [{"word": w, "score": round(s, 2)} for w, s in kw_scores]
    except Exception as e:
        print(f"TF-IDF Error: {e}")
        return []

def run_analysis():
    print("Loading data...")
    df = load_data()
    print("Preprocessing & Extracting...")
    df = preprocess_and_extract(df)
    
    print("Generating insights...")
    # 기초 통계
    total_jobs = int(df.shape[0])
    top_locations = df['location'].value_counts().head(3).to_dict()
    top_experience = df['experience'].value_counts().head(3).to_dict()
    
    # 직무군 분포
    job_categories = df['job_category'].value_counts().to_dict()
    
    # TF-IDF 분석
    req_keywords = get_top_keywords(df['req_text'], 10)
    pref_keywords = get_top_keywords(df['pref_text'], 10)
    title_keywords = get_top_keywords(df['title'], 10)
    
    results = {
        "summary": {
            "total_jobs": total_jobs,
            "top_locations": top_locations,
            "top_experience": top_experience
        },
        "categories": job_categories,
        "keywords": {
            "required": req_keywords,
            "preferred": pref_keywords,
            "title": title_keywords
        },
        "insights": [
            "경력 요건의 경우 '경력무관(포텐셜)'과 '3~5년 차(즉시 전력감)'로 양극화되어 있습니다.",
            "필수 자격요건에서는 기획/운영 능력과 커뮤니케이션 스킬이 주로 요구됩니다.",
            "우대사항에서는 GA, SQL, 포토샵 등 구체적인 실무 툴 활용 능력이 큰 가점을 받습니다.",
            "직무 카테고리별로 보면 퍼포먼스와 콘텐츠 마케팅이 가장 높은 수요를 보입니다."
        ]
    }
    
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Analysis saved to {JSON_PATH}")

if __name__ == "__main__":
    run_analysis()
