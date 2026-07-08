"""
마케터 채용공고의 텍스트에서 스펙(하드스킬, 자격증, 경험), 기업 규모, 레드플래그 등을
휴리스틱하게 추출하여 정량 분석하는 심층 EDA 스크립트입니다.
"""

import os
import pandas as pd
import json
import re
from collections import Counter

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'marketing_project', 'marketing_jobs.csv')
JSON_OUTPUT = os.path.join(BASE_DIR, 'report', 'advanced_eda_summary.json')

# 정규식 패턴 (대소문자 무시)
SKILLS = {
    'GA / GA4': r'\b(?:ga4?|google analytics)\b',
    'SQL': r'\bsql\b',
    'Python': r'\bpython\b|파이썬',
    'Tableau': r'\btableau\b|태블로',
    'Excel / 엑셀': r'\bexcel\b|엑셀',
    'Adobe (포토샵/일러)': r'adobe|포토샵|일러스트레이터|photoshop|illustrator',
    'Figma': r'\bfigma\b|피그마',
    '프리미어/에펙 (영상)': r'프리미어|에프터이펙트|premiere|after\s*effect|영상편집',
    'Notion / Slack': r'notion|slack|노션|슬랙'
}

CERTS = {
    '검색광고마케터': r'검색광고마케터',
    '컴퓨터활용능력': r'컴퓨터활용능력|컴활',
    '토익 (TOEIC)': r'\btoeic\b|토익',
    '오픽/토스 (Speaking)': r'\bopic\b|오픽|토스|toeic\s*speaking',
    '어학 우수자 (영어)': r'영어 능통|어학 우수|비즈니스 영어|영어 가능|영어 회화',
    '제2외국어 (일/중)': r'jlpt|hsk|일본어|중국어'
}

EXP = {
    '인턴 경험': r'인턴',
    '브랜드/서비스 런칭': r'브랜드 런칭|서비스 런칭|신규 런칭',
    'SNS 채널 운영': r'sns 채널|sns 운영|인스타그램 운영|유튜브 운영',
    '퍼포먼스 캠페인 운영': r'퍼포먼스 캠페인|매체 운영|광고 집행',
    '에이전시/대행사 경험': r'에이전시|대행사',
    '데이터 분석 경험': r'데이터 추출|데이터 분석 경험|A/B 테스트|a/b test'
}

RED_FLAGS = {
    '멀티태스킹/올라운더': r'멀티\s*태스킹|올라운더|all\s*rounder|다양한 업무',
    'A부터 Z까지': r'a부터 z까지|a to z',
    '가족같은 분위기': r'가족\s*같은',
    '강한 체력/책임감': r'체력|강한 책임감|열정',
    '빠른 실행력 (야근 암시)': r'빠른 실행|빠른 호흡',
    '식대/간식 강조': r'식대|간식 무한|간식 제공'
}

def analyze_advanced():
    df = pd.read_csv(DATA_PATH)
    df = df.drop_duplicates(subset=['job_id'])
    
    total_docs = len(df)
    
    # NaN 처리
    df['detail_text'] = df['detail_text'].fillna('')
    df['title'] = df['title'].fillna('')
    df['company_name'] = df['company_name'].fillna('')

    # 기업 규모 분류
    def classify_company(row):
        text = str(row['detail_text']).lower()
        comp = str(row['company_name']).lower()
        
        # 스타트업 키워드
        if re.search(r'스타트업|시리즈\s*[a-z]|투자 유치|스톡옵션|초기 런칭|유니콘', text):
            return '스타트업'
        
        # 중견/대기업 키워드
        if re.search(r'대기업|중견기업|상장|코스피|코스닥', text) or re.search(r'그룹|홀딩스|네트웍스', comp):
            return '중견/대기업'
            
        return '중소/일반기업'

    df['company_size'] = df.apply(classify_company, axis=1)

    # 항목 추출 함수
    def extract_counts(pattern_dict, target_texts):
        counts = {k: 0 for k in pattern_dict.keys()}
        for text in target_texts:
            t = str(text).lower()
            for key, pattern in pattern_dict.items():
                if re.search(pattern, t):
                    counts[key] += 1
        return counts

    # 전체 통계
    all_texts = df['detail_text'].tolist()
    skills_count = extract_counts(SKILLS, all_texts)
    certs_count = extract_counts(CERTS, all_texts)
    exp_count = extract_counts(EXP, all_texts)
    rf_count = extract_counts(RED_FLAGS, all_texts)

    # 기업 규모별 통계
    startup_texts = df[df['company_size'] == '스타트업']['detail_text'].tolist()
    enterprise_texts = df[df['company_size'] == '중견/대기업']['detail_text'].tolist()
    
    size_stats = {
        '스타트업': {
            'count': len(startup_texts),
            'skills': extract_counts(SKILLS, startup_texts),
            'certs': extract_counts(CERTS, startup_texts),
            'exp': extract_counts(EXP, startup_texts)
        },
        '중견/대기업': {
            'count': len(enterprise_texts),
            'skills': extract_counts(SKILLS, enterprise_texts),
            'certs': extract_counts(CERTS, enterprise_texts),
            'exp': extract_counts(EXP, enterprise_texts)
        }
    }

    # 레드플래그가 2개 이상 매칭되는 공고 수
    def count_redflags(text):
        t = str(text).lower()
        matches = sum(1 for p in RED_FLAGS.values() if re.search(p, t))
        return matches

    df['rf_score'] = df['detail_text'].apply(count_redflags)
    high_rf_count = len(df[df['rf_score'] >= 2])
    
    results = {
        'total_analyzed': total_docs,
        'company_size_dist': df['company_size'].value_counts().to_dict(),
        'overall': {
            'skills': sorted(skills_count.items(), key=lambda x: x[1], reverse=True),
            'certs': sorted(certs_count.items(), key=lambda x: x[1], reverse=True),
            'exp': sorted(exp_count.items(), key=lambda x: x[1], reverse=True),
            'red_flags': sorted(rf_count.items(), key=lambda x: x[1], reverse=True),
            'high_rf_count': high_rf_count
        },
        'by_size': size_stats
    }

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("고급 분석 완료!")

if __name__ == "__main__":
    analyze_advanced()
