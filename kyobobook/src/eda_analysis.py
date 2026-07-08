"""
교보문고 베스트셀러 데이터에 대한 탐색적 데이터 분석(EDA) 스크립트입니다.
데이터 전처리, 기술통계량 산출 및 최소 10가지 이상의 시각화 이미지를 생성합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer

def run_eda():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "bestseller.csv")
    image_dir = os.path.join(os.path.dirname(__file__), "..", "images")
    os.makedirs(image_dir, exist_ok=True)
    
    df = pd.read_csv(data_path)
    
    # 1. 초기 데이터 점검
    num_rows, num_cols = df.shape
    duplicates = df.duplicated().sum()
    
    # 주요 컬럼 추출 및 전처리
    target_cols = {
        'prstRnkn': 'rank',
        'product.productInfo.cmdtName': 'title',
        'product.productInfo.cmdtClstName': 'category',
        'product.productInfo.pbcmName': 'publisher',
        'product.productInfo.chrcName': 'author',
        'product.priceInfo.saleCmdtPrce': 'price',
        'product.priceInfo.saleCmdtSapr': 'discount_price',
        'product.reviewInfo.score': 'review_score',
        'product.reviewInfo.count': 'review_count',
        'product.productInfo.anntCntt': 'description'
    }
    
    df_clean = df[list(target_cols.keys())].rename(columns=target_cols).copy()
    
    # 결측치 처리
    df_clean['review_score'] = df_clean['review_score'].fillna(0)
    df_clean['review_count'] = df_clean['review_count'].fillna(0)
    df_clean['description'] = df_clean['description'].fillna('')
    df_clean['category'] = df_clean['category'].fillna('기타')
    df_clean['publisher'] = df_clean['publisher'].fillna('기타')
    
    # 기술통계
    num_stats = df_clean[['price', 'discount_price', 'review_score', 'review_count']].describe().to_dict()
    cat_stats = df_clean[['category', 'publisher', 'author']].describe(include=['O']).to_dict()
    
    stats_output = {
        "rows": num_rows,
        "cols": num_cols,
        "duplicates": int(duplicates),
        "num_stats": num_stats,
        "cat_stats": cat_stats,
        "top_categories": df_clean['category'].value_counts().head(30).to_dict(),
        "top_publishers": df_clean['publisher'].value_counts().head(30).to_dict()
    }
    
    # 통계량 저장
    scratch_dir = os.path.join(os.path.dirname(__file__), "..", "..", ".gemini", "antigravity-ide", "brain", "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    # Just save in project root for simplicity since I need to read it
    stats_path = os.path.join(os.path.dirname(__file__), "..", "data", "eda_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats_output, f, ensure_ascii=False, indent=2)

    # ===============================
    # 시각화 생성 (10종)
    # ===============================
    
    # 1. 단변량: 가격 분포 (Histogram)
    plt.figure(figsize=(10, 6))
    plt.hist(df_clean['price'], bins=30, color='skyblue', edgecolor='black')
    plt.title('도서 정가(Price) 분포')
    plt.xlabel('가격 (원)')
    plt.ylabel('빈도수')
    plt.savefig(os.path.join(image_dir, '01_price_hist.png'))
    plt.close()

    # 2. 단변량: 리뷰 평점 분포 (Histogram)
    plt.figure(figsize=(10, 6))
    plt.hist(df_clean[df_clean['review_score'] > 0]['review_score'], bins=20, color='lightgreen', edgecolor='black')
    plt.title('리뷰 평점 분포 (0점 제외)')
    plt.xlabel('평점 (10점 만점)')
    plt.ylabel('빈도수')
    plt.savefig(os.path.join(image_dir, '02_review_score_hist.png'))
    plt.close()

    # 3. 단변량: 분야별 도서 수 (Bar Chart)
    plt.figure(figsize=(12, 8))
    cat_counts = df_clean['category'].value_counts().head(20)
    cat_counts.sort_values().plot(kind='barh', color='coral')
    plt.title('상위 20개 분야 빈도수')
    plt.xlabel('도서 수')
    plt.ylabel('분야')
    plt.tight_layout()
    plt.savefig(os.path.join(image_dir, '03_category_bar.png'))
    plt.close()

    # 4. 단변량: 출판사별 베스트셀러 수 (Bar Chart)
    plt.figure(figsize=(12, 8))
    pub_counts = df_clean['publisher'].value_counts().head(20)
    pub_counts.sort_values().plot(kind='barh', color='purple')
    plt.title('상위 20개 출판사 빈도수')
    plt.xlabel('도서 수')
    plt.ylabel('출판사')
    plt.tight_layout()
    plt.savefig(os.path.join(image_dir, '04_publisher_bar.png'))
    plt.close()

    # 5. 이변량: 가격 vs 리뷰 평점 (Scatter Plot)
    plt.figure(figsize=(10, 6))
    subset = df_clean[df_clean['review_score'] > 0]
    plt.scatter(subset['price'], subset['review_score'], alpha=0.5, color='orange')
    plt.title('가격과 리뷰 평점의 관계')
    plt.xlabel('가격 (원)')
    plt.ylabel('리뷰 평점')
    plt.savefig(os.path.join(image_dir, '05_price_vs_score_scatter.png'))
    plt.close()

    # 6. 이변량: 리뷰 수 vs 리뷰 평점 (Scatter Plot)
    plt.figure(figsize=(10, 6))
    plt.scatter(subset['review_count'], subset['review_score'], alpha=0.5, color='teal')
    plt.title('리뷰 수와 리뷰 평점의 관계')
    plt.xlabel('리뷰 수')
    plt.ylabel('리뷰 평점')
    # 리뷰 수가 극단적으로 많은 경우가 있으므로 log scale 고려
    plt.xscale('log')
    plt.savefig(os.path.join(image_dir, '06_count_vs_score_scatter.png'))
    plt.close()

    # 7. 그룹분석: 상위 10개 분야별 평균 가격 (Bar Chart)
    plt.figure(figsize=(12, 6))
    top10_cats = df_clean['category'].value_counts().head(10).index
    avg_price_by_cat = df_clean[df_clean['category'].isin(top10_cats)].groupby('category')['price'].mean().sort_values(ascending=False)
    avg_price_by_cat.plot(kind='bar', color='steelblue')
    plt.title('상위 10개 분야별 평균 가격')
    plt.xlabel('분야')
    plt.ylabel('평균 가격 (원)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(image_dir, '07_avg_price_by_category.png'))
    plt.close()

    # 8. 그룹분석: 상위 10개 분야별 평균 리뷰 수 (Bar Chart)
    plt.figure(figsize=(12, 6))
    avg_review_by_cat = df_clean[df_clean['category'].isin(top10_cats)].groupby('category')['review_count'].mean().sort_values(ascending=False)
    avg_review_by_cat.plot(kind='bar', color='indianred')
    plt.title('상위 10개 분야별 평균 리뷰 수')
    plt.xlabel('분야')
    plt.ylabel('평균 리뷰 수')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(image_dir, '08_avg_review_by_category.png'))
    plt.close()

    # 9. 다변량: 수치형 변수 상관관계 히트맵 (Heatmap 대신 scatter matrix나 단순 플롯)
    import matplotlib.cm as cm
    numeric_df = df_clean[['price', 'discount_price', 'review_score', 'review_count']]
    corr = numeric_df.corr()
    plt.figure(figsize=(8, 6))
    cax = plt.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1, fignum=1)
    plt.colorbar(cax)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45)
    plt.yticks(range(len(corr.columns)), corr.columns)
    for (i, j), z in np.ndenumerate(corr):
        plt.text(j, i, '{:0.2f}'.format(z), ha='center', va='center', bbox=dict(boxstyle='round', facecolor='white', edgecolor='0.3'))
    plt.title('수치형 변수 간 상관관계', pad=20)
    plt.savefig(os.path.join(image_dir, '09_correlation_matrix.png'))
    plt.close()

    # 10. 단변량: 리뷰 수 상자수염그림 (Boxplot)
    plt.figure(figsize=(10, 4))
    plt.boxplot(df_clean['review_count'], vert=False)
    plt.title('리뷰 수 분포 상자수염그림 (Outlier 확인)')
    plt.xlabel('리뷰 수')
    plt.savefig(os.path.join(image_dir, '10_review_count_boxplot.png'))
    plt.close()

    # 11. 텍스트 데이터: TF-IDF 상위 30개 키워드 시각화
    # 간단한 명사 추출을 위한 정규표현식 기반 (KoNLPy 사용 안함)
    import re
    def simple_tokenize(text):
        words = re.findall(r'[가-힣a-zA-Z]{2,}', str(text))
        return words

    tfidf = TfidfVectorizer(tokenizer=simple_tokenize, max_features=1000, stop_words=['입니다', '있는', '대한', '위한', '통해', '수', '것', '이', '그', '등', '를', '은', '는'])
    text_data = df_clean['description'].tolist()
    if text_data:
        tfidf_matrix = tfidf.fit_transform(text_data)
        feature_names = tfidf.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        keywords_df = pd.DataFrame({'keyword': feature_names, 'score': scores})
        keywords_df = keywords_df.sort_values('score', ascending=False).head(30)
        
        plt.figure(figsize=(12, 8))
        plt.barh(keywords_df['keyword'][::-1], keywords_df['score'][::-1], color='mediumaquamarine')
        plt.title('도서 소개글 TF-IDF 상위 30개 키워드')
        plt.xlabel('TF-IDF 점수 합산')
        plt.ylabel('키워드')
        plt.tight_layout()
        plt.savefig(os.path.join(image_dir, '11_tfidf_keywords.png'))
        plt.close()
        
        # 키워드 저장
        stats_output['top_keywords'] = keywords_df.to_dict(orient='records')
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats_output, f, ensure_ascii=False, indent=2)

    print(f"분석 완료: 통계 파일({stats_path}) 및 시각화 이미지 11종({image_dir}) 생성됨")

if __name__ == "__main__":
    run_eda()
