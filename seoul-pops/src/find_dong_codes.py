"""
이 스크립트는 엑셀 파일에서 동 코드를 찾아 파일에 기록합니다.
"""
import pandas as pd

def main():
    file_path = "seoul-pops/data/행정동코드_매핑정보_20241218.xlsx"
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error: {e}")
        return

    # Assuming columns are like: 0:?, 1:행자부코드, 2:시도, 3:시군구, 4:행정동명
    # Let's just find columns by checking their content or just search all text columns
    
    code_col = df.columns[1] # 행자부코드
    dong_col = df.columns[4] # 행정동명
    
    mask = df[dong_col].astype(str).str.contains('연남|성수', na=False)
    filtered = df[mask][[code_col, dong_col]]
    
    with open("seoul-pops/report/dong_codes.txt", "w", encoding="utf-8") as f:
        f.write(filtered.to_string())
        
    print("Saved to dong_codes.txt")

if __name__ == "__main__":
    main()
