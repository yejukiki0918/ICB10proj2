"""
이 파일은 Online Shoppers Purchasing Intention 데이터셋을 바탕으로 
사용자의 구매(Revenue) 여부를 예측하는 Decision Tree 모델 파이프라인 페이지입니다.
Streamlit의 멀티페이지 앱 구조를 위해 pages 폴더에 위치합니다.
"""
import streamlit as st
import pandas as pd
import zipfile
import os
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE

st.set_page_config(page_title="머신러닝 예측", layout="wide")

@st.cache_data
def load_data():
    # 현재 파일 기준 부모 디렉토리의 data 폴더 경로 탐색 (src/pages/01_ML_Prediction.py -> ../../data)
    zip_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "online+shoppers+purchasing+intention+dataset.zip")
    with zipfile.ZipFile(zip_path, 'r') as z:
        file_list = z.namelist()
        with z.open(file_list[0]) as f:
            df = pd.read_csv(f)
    return df

st.header("🤖 머신러닝 예측: 사용자 구매(Revenue) 여부 예측")
st.markdown("Decision Tree 모델을 활용하여 사용자의 세션 데이터를 바탕으로 구매 여부를 예측하고 분석합니다.")

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
    st.stop()

# 1. Mermaid 시각화
st.subheader("1. 모델 파이프라인 (Mermaid)")
st.markdown("""
```mermaid
graph TD;
    A[데이터 로드] --> B[데이터 전처리<br/>범주형 변수 더미화];
    B --> C[학습/테스트 분할<br/>80% / 20%];
    C --> S[SMOTE 오버샘플링<br/>Train 불균형 해소];
    S --> D[Decision Tree 모델 학습<br/>max_depth=5];
    D --> E[Train/Test 예측수행<br/>및 평가지표 계산];
    E --> F[결과 시각화<br/>트리, 중요도, 과적합진단, 오차행렬];
```
""")

# 데이터 준비
df_ml = df.copy()

# 불리언/범주형 처리
df_ml['Revenue'] = df_ml['Revenue'].astype(int)
df_ml['Weekend'] = df_ml['Weekend'].astype(int)

# 범주형 원핫인코딩
cat_cols = ['Month', 'VisitorType', 'Browser', 'OperatingSystems', 'Region', 'TrafficType']
for col in ['Browser', 'OperatingSystems', 'Region', 'TrafficType']:
    df_ml[col] = df_ml[col].astype(str)
    
df_ml = pd.get_dummies(df_ml, columns=cat_cols, drop_first=True)

X = df_ml.drop('Revenue', axis=1)
y = df_ml['Revenue']

# 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# SMOTE 오버샘플링 (Train 데이터에만 적용)
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# 모델 학습 (오버샘플링된 데이터로 학습하여 Recall 개선)
dt_model = DecisionTreeClassifier(max_depth=5, random_state=42)
dt_model.fit(X_train_resampled, y_train_resampled)

# 2. Decision Tree 시각화
st.subheader("2. 의사결정 나무 (Decision Tree) 시각화")
st.markdown("상위 3개의 Depth까지만 시각화하여 주요 분기점(Split)을 확인합니다.")
fig_tree, ax_tree = plt.subplots(figsize=(20, 10))
plot_tree(dt_model, feature_names=X.columns, class_names=['구매 안 함', '구매'], filled=True, ax=ax_tree, max_depth=3, fontsize=10)
st.pyplot(fig_tree)

# 3. 피처 중요도 시각화
st.subheader("3. 주요 피처 중요도 (Feature Importances)")
importances = dt_model.feature_importances_
feat_imp = pd.DataFrame({'Feature': X.columns, 'Importance': importances}).sort_values(by='Importance', ascending=False)

fig_imp = px.bar(feat_imp.head(10), x='Importance', y='Feature', orientation='h', title='상위 10개 피처 중요도', color='Importance', color_continuous_scale='Viridis')
fig_imp.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_imp, use_container_width=True)

# 4. Train vs Test 성능 비교 및 과적합 진단
st.subheader("4. Train vs Test 성능 지표 비교 및 과적합 진단")
st.markdown("SMOTE 오버샘플링을 적용하여 소수 클래스(구매자)에 대한 예측력(재현율)을 개선했습니다. 학습 데이터와 평가 데이터의 성능을 비교하여 과적합 여부를 진단합니다.")

def get_metrics(y_true, y_pred, y_prob):
    return {
        '정확도(Accuracy)': accuracy_score(y_true, y_pred),
        '정밀도(Precision)': precision_score(y_true, y_pred),
        '재현율(Recall)': recall_score(y_true, y_pred),
        'F1 스코어': f1_score(y_true, y_pred),
        'ROC-AUC': roc_auc_score(y_true, y_prob)
    }

# 원본 Train 데이터에 대한 예측 (과적합 확인용)
y_train_pred = dt_model.predict(X_train)
y_train_prob = dt_model.predict_proba(X_train)[:, 1]
train_metrics = get_metrics(y_train, y_train_pred, y_train_prob)

# Test 데이터에 대한 예측
y_test_pred = dt_model.predict(X_test)
y_test_prob = dt_model.predict_proba(X_test)[:, 1]
test_metrics = get_metrics(y_test, y_test_pred, y_test_prob)

metrics_df = pd.DataFrame([
    {'데이터셋': '학습(Train)', '평가지표': k, '점수': v} for k, v in train_metrics.items()
] + [
    {'데이터셋': '평가(Test)', '평가지표': k, '점수': v} for k, v in test_metrics.items()
])

fig_comp = px.bar(metrics_df, x='평가지표', y='점수', color='데이터셋', barmode='group',
                  title="학습(Train) vs 평가(Test) 성능 비교",
                  text_auto='.3f', color_discrete_map={'학습(Train)': '#3366CC', '평가(Test)': '#DC3912'})
fig_comp.update_layout(yaxis_range=[0, 1.1])
st.plotly_chart(fig_comp, use_container_width=True)

# 과적합 진단 로직
recall_diff = train_metrics['재현율(Recall)'] - test_metrics['재현율(Recall)']
acc_diff = train_metrics['정확도(Accuracy)'] - test_metrics['정확도(Accuracy)']

if test_metrics['재현율(Recall)'] < 0.6 and test_metrics['정확도(Accuracy)'] < 0.6:
    diagnosis = "과소적합(Underfitting) 의심"
    color = "error"
    msg = "모델이 학습 데이터의 패턴조차 제대로 파악하지 못하고 있습니다. 모델 복잡도(max_depth)를 늘리거나 추가 변수를 탐색해야 합니다."
elif acc_diff > 0.1 or recall_diff > 0.15:
    diagnosis = "과적합(Overfitting) 의심"
    color = "warning"
    msg = f"학습 점수가 평가 점수보다 비정상적으로 높습니다. (재현율 차이: {recall_diff:.3f}, 정확도 차이: {acc_diff:.3f}). 모델이 학습 데이터에 과하게 맞춰져 있어 일반화 능력이 떨어집니다."
else:
    diagnosis = "적절한 학습 (Good Fit)"
    color = "success"
    msg = "학습과 평가 점수의 차이가 크지 않으며, 오버샘플링을 통해 재현율(Recall)도 안정적으로 확보된 일반화된 모델로 판단됩니다."
    
if color == "error":
    st.error(f"**진단 결과: {diagnosis}**\n\n{msg}")
elif color == "warning":
    st.warning(f"**진단 결과: {diagnosis}**\n\n{msg}")
else:
    st.success(f"**진단 결과: {diagnosis}**\n\n{msg}")

st.subheader("5. 오차 행렬 (Confusion Matrix)")
cm = confusion_matrix(y_test, y_test_pred)
fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale='Blues', 
                   labels=dict(x="예측 클래스", y="실제 클래스", color="빈도"),
                   x=['구매 안 함', '구매 완료'], y=['구매 안 함', '구매 완료'], title="평가(Test) 데이터 기준 오차 행렬")
st.plotly_chart(fig_cm, use_container_width=True)

st.divider()

st.header("💡 비즈니스 인사이트 및 액션 플랜")
st.markdown("""
위의 머신러닝(Decision Tree) 시각화 및 피처 중요도(Feature Importances) 분석 결과를 종합하여, 
성공적인 온라인 쇼핑몰 운영과 구매 전환율(Revenue) 극대화를 위한 **핵심 비즈니스 인사이트 및 액션 플랜**을 다음과 같이 제안합니다.

### 📌 1. 핵심 인사이트 (Key Insights)
* **`PageValues`의 압도적인 지배력**: 디시전 트리 구조와 피처 중요도 모두에서 `PageValues`(방문한 페이지의 이전 거래 기여 가치평균)가 구매 예측을 결정짓는 가장 핵심적인 요인으로 나타났습니다. 즉, 고객이 '가치 있는 페이지(장바구니, 결제 프로세스, 고관여 상품 페이지)'에 도달했는지 여부가 구매로 직결됩니다.
* **이탈률(`ExitRates` / `BounceRates`)의 부정적 영향**: 트리 구조에서 `PageValues`가 0이더라도 이탈률이 낮고 사이트 내 체류/탐색이 준수한 경우 구매 가능성이 일부 존재하지만, 이탈률이 높으면 구매 확률은 0%에 수렴합니다.
* **상품 탐색 시간(`ProductRelated_Duration`)**: 상품 관련 페이지를 얼마나 오래 탐색했는지가 구매 결정의 보조적인 중요 지표로 작용합니다. 충분한 정보를 탐색한 고객일수록 구매 확신을 가지기 쉽습니다.
* **시기적 요인(`Month_Nov` 등)**: 11월과 같은 대형 프로모션(블랙 프라이데이 등) 시즌의 트래픽은 강력한 구매 의도로 이어지는 경향이 짙습니다.

### 🚀 2. 데이터 기반 액션 플랜 (Action Plan)
**① 핵심 가치 페이지(High PageValues)로의 유입 경로 단축**
* **분석 결과 연계**: 방문자가 `PageValues`가 높은 페이지에 조기 도달할수록 결제 확률이 급증합니다.
* **구체적 액션**: 메인 페이지 및 검색 결과창에 **'개인화된 맞춤형 상품 추천'**과 **'원클릭 장바구니 담기'** 기능을 전면 배치합니다. 구매 전환율이 높았던 특정 상품(킬러 아이템)을 랜딩 최상단에 노출시켜 핵심 페이지 도달률을 즉각적으로 끌어올리는 UI/UX 개편이 필요합니다.

**② 체류 시간 증대 및 조기 이탈 방지 (Bounce/Exit Rate 개선)**
* **분석 결과 연계**: 이탈률 지표가 높을 경우, 트리 말단에서 모두 `False(미구매)`로 분류되었습니다.
* **구체적 액션**: 랜딩 페이지 로딩 속도를 최적화하고, 페이지 스크롤 시 이탈이 잦은 구간에 **'타임 세일 쿠폰'**이나 **'실시간 구매 후기 팝업'**을 노출해 체류 시간을 연장합니다. 특히, 장바구니에 물건을 담아두고 결제하지 않는(이탈 위험) 고객을 타겟으로 웹 푸시 알림 및 이메일 리마인드(CRM 캠페인)를 자동화해야 합니다.

**③ 시즌 및 트래픽 맞춤형 다이나믹 마케팅**
* **분석 결과 연계**: 특정 트래픽 유형 및 11월과 같은 연말 프로모션 월의 전환율이 통계적으로 유의미한 차이를 만듭니다.
* **구체적 액션**: 11월 트래픽 폭주에 대비해 서버 유연성을 확보하고, 성수기 1주일 전부터 **'사전 예약 알림'**을 통해 재방문(Returning_Visitor)을 유도합니다. 비수기에는 상품 탐색(`ProductRelated`)은 많으나 결제하지 않는 유저를 추출하여 **'첫 구매 혜택'** 리타겟팅 광고(Retargeting Ads)를 집중 편성, 마케팅 ROI를 높입니다.

> **🎯 총평**: 결국 온라인 쇼핑몰의 구매 전환(Revenue)은 **'유의미한 상품 탐색 유도 → 고가치 페이지(장바구니 등) 도달 → 이탈 전 즉각 결제'**라는 짧고 명확한 동선 확보에 달려 있습니다. 데이터가 지목한 가장 확실한 선행 지표(`PageValues`)를 높이는 데 모든 마케팅 리소스와 사이트 최적화 역량을 집중해야 합니다.
""")
