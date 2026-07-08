"""
burger.csv 데이터에서 '음식', '소매' 업종이 아닌 데이터를 제외하고 중복 데이터를 검사하는 스크립트.
"""
import os
import pandas as pd

def main():
    data_path = os.path.join("burger_index", "data", "burger.csv")
    report_path = os.path.join("burger_index", "report", "duplicates_report.md")
    
    df = pd.read_csv(data_path, encoding='utf-8')
    
    # 1. 음식, 소매가 아닌 데이터 제외
    target_col = [c for c in df.columns if '상권업종대분류명' in c][0]
    initial_count = len(df)
    df_cleaned = df[df[target_col].isin(['음식', '소매'])]
    filtered_count = len(df_cleaned)
    removed_count = initial_count - filtered_count
    
    # 2. 중복 데이터 확인
    # 상가업소번호가 기본 키이지만, 주소와 상호명으로도 확인
    # 여기서는 '상가업소번호' 기준 중복과 완전 동일 행 중복을 검사
    id_col = [c for c in df.columns if '상가업소번호' in c][0]
    
    duplicates = df_cleaned[df_cleaned.duplicated(subset=[id_col], keep=False)]
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"### 데이터 정제 결과\n")
        f.write(f"- 초기 데이터 수: {initial_count}건\n")
        f.write(f"- '음식', '소매' 업종 필터링 후 데이터 수: {filtered_count}건 (제외된 데이터: {removed_count}건)\n\n")
        
        f.write(f"### 중복 데이터 내역\n")
        if len(duplicates) == 0:
            f.write("중복된 데이터가 없습니다.\n")
        else:
            f.write(f"총 {len(duplicates)}건의 중복 의심 데이터(상가업소번호 동일)가 발견되었습니다.\n\n")
            
            # Sort by ID to group duplicates together
            duplicates = duplicates.sort_values(by=id_col)
            cols_to_show = [id_col, '상호명', '도로명주소', target_col]
            
            f.write(duplicates[cols_to_show].to_markdown(index=False))
            
    # 정제된 데이터를 다시 저장
    df_cleaned.to_csv(data_path, index=False, encoding='utf-8')

if __name__ == "__main__":
    main()
