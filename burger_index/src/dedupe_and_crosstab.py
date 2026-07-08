"""
burger.csv 파일에서 브랜드와 주소 기준 중복을 제거하고
브랜드명과 상권업종대분류명 기준의 교차표를 생성하는 스크립트.
"""
import os
import pandas as pd

def get_brand(name):
    n = str(name).lower()
    if '버거킹' in n or 'burger king' in n: return '버거킹'
    elif '맥도날드' in n or 'mcdonald' in n: return '맥도날드'
    elif 'kfc' in n or '케이에프씨' in n: return 'KFC'
    elif '롯데리아' in n or 'lotteria' in n: return '롯데리아'
    else: return '기타'

def main():
    data_path = os.path.join("burger_index", "data", "burger.csv")
    report_path = os.path.join("burger_index", "report", "final_crosstab.md")
    
    df = pd.read_csv(data_path, encoding='utf-8')
    initial_count = len(df)
    
    # 파생변수 생성
    df['브랜드명'] = df['상호명'].apply(get_brand)
    
    # 주소 정제 후 중복 제거 (첫 번째 값만 남김)
    df['도로명주소_정제'] = df['도로명주소'].astype(str).str.strip()
    df_deduped = df.drop_duplicates(subset=['브랜드명', '도로명주소_정제'], keep='first').copy()
    
    deduped_count = len(df_deduped)
    
    # 도로명주소_정제 컬럼은 더 이상 필요 없으므로 제거 후 저장
    df_deduped = df_deduped.drop(columns=['도로명주소_정제'])
    df_deduped.to_csv(data_path, index=False, encoding='utf-8')
    
    # 교차표 생성
    target_col = [c for c in df_deduped.columns if '상권업종대분류명' in c][0]
    crosstab_result = pd.crosstab(df_deduped['브랜드명'], df_deduped[target_col], margins=True, margins_name='총합')
    
    # 마크다운 저장
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"### 데이터 중복 제거 결과\\n")
        f.write(f"- 제거 전 데이터 수: {initial_count}건\\n")
        f.write(f"- 제거 후 데이터 수: {deduped_count}건 (중복 제거 {initial_count - deduped_count}건)\\n\\n")
        f.write(f"### 중복 제거 후 최종 브랜드별 교차표 빈도수\\n\\n")
        f.write(crosstab_result.to_markdown())

if __name__ == "__main__":
    main()
