import pandas as pd
import os

data_dir = 'c:/Users/다의/Desktop/icb10proj2/illumiel/data'

# 1. 전월비 / 전년비 비교 (상품성과보고서)
try:
    df_mom = pd.read_excel(os.path.join(data_dir, '상품성과보고서_비교기간26년5월_대비 26년6월.xlsx'))
    df_yoy = pd.read_excel(os.path.join(data_dir, '상품성과보고서_비교기간25년6월_대비 26년6월(전년도대비).xlsx'))
    
    overall_mom = df_mom[df_mom['채널상품명'] == '전체'].copy()
    overall_yoy = df_yoy[df_yoy['채널상품명'] == '전체'].copy()
    
    print("--- 6월 총괄 성과 ---")
    print(overall_mom.head(2))
    print(overall_yoy.head(2))
except Exception as e:
    print("Error reading 상품성과보고서:", e)

# 2. CRM / 알림받기
try:
    df_crm = pd.read_csv(os.path.join(data_dir, '알림받기통계_고객현황_202507_202606(12개월이전 조회불가).csv'), encoding='utf-8')
    df_rep = pd.read_csv(os.path.join(data_dir, '재구매통계_202507_202606.csv'), encoding='utf-8')
    print("--- CRM 및 재구매 통계 ---")
    print(df_crm.tail(2))
    print(df_rep.tail(2))
except Exception as e:
    print("Error reading CRM data:", e)

# 3. 6월 판매정보
try:
    df_sales = pd.read_excel(os.path.join(data_dir, '6월 판매정보_상세내역_일루미엘_2026-06월.xlsx'))
    df_sales['상품 주문 구매확정일'] = pd.to_datetime(df_sales['상품 주문 구매확정일'], errors='coerce')
    
    suncare_sales = df_sales[(df_sales['상품 주문 구매확정일'] >= '2026-06-08') & (df_sales['상품 주문 구매확정일'] <= '2026-06-14')]
    triple_sales = df_sales[(df_sales['상품 주문 구매확정일'] >= '2026-06-22') & (df_sales['상품 주문 구매확정일'] <= '2026-07-05')]
    
    print("--- 프로모션별 실적 ---")
    print(f"Suncare (6/8~14) Revenue: {suncare_sales['상품 결제 금액'].sum():,}")
    print(f"Triple (6/22~7/5) Revenue: {triple_sales['상품 결제 금액'].sum():,}")
    
    # 피부 레스큐(감태) vs 클리어런스
    rescue_revenue = triple_sales[triple_sales['상품명'].str.contains('감태|레스큐', na=False)]['상품 결제 금액'].sum()
    clearance_revenue = triple_sales[triple_sales['상품명'].str.contains('클리어런스|임박', na=False)]['상품 결제 금액'].sum()
    print(f"Triple - Rescue Revenue: {rescue_revenue:,}")
    print(f"Triple - Clearance Revenue: {clearance_revenue:,}")
except Exception as e:
    print("Error reading 6월 판매정보:", e)
