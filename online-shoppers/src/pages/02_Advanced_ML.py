"""
이 파일은 Online Shoppers Purchasing Intention 데이터셋을 바탕으로 
Random Forest 및 Gradient Boosting 앙상블 기법을 적용하여 구매 예측 성능을 비교 분석하는 페이지입니다.
"""
import streamlit as st
import pandas as pd
import zipfile
import os
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE

st.set_page_config(page_title="고급 앙상블 모델 예측", layout="wide")

@st.cache_data
def load_data():
    zip_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "online+shoppers+purchasing+intention+dataset.zip")
    with zipfile.ZipFile(zip_path, 'r') as z:
        file_list = z.namelist()
        with z.open(file_list[0]) as f:
            df = pd.read_csv(f)
    return df

st.header("🤖 고급 앙상블 머신러닝 (Random Forest & Boosting)")
st.markdown("의사결정 나무를 기반으로 하는 두 가지 대표적인 앙상블 알고리즘(랜덤 포레스트, 그래디언트 부스팅)을 사용하여 더 강력한 구매(Revenue) 예측 모델을 학습하고 성능을 비교합니다.")

with st.spinner("데이터 로드 및 모델 학습 중입니다... (데이터 크기와 트리의 개수에 따라 다소 시간이 소요될 수 있습니다)"):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        st.stop()
        
    # 데이터 준비
    df_ml = df.copy()
    df_ml['Revenue'] = df_ml['Revenue'].astype(int)
    df_ml['Weekend'] = df_ml['Weekend'].astype(int)

    cat_cols = ['Month', 'VisitorType', 'Browser', 'OperatingSystems', 'Region', 'TrafficType']
    for col in ['Browser', 'OperatingSystems', 'Region', 'TrafficType']:
        df_ml[col] = df_ml[col].astype(str)
        
    df_ml = pd.get_dummies(df_ml, columns=cat_cols, drop_first=True)

    X = df_ml.drop('Revenue', axis=1)
    y = df_ml['Revenue']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_resampled, y_train_resampled)

    gb_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    gb_model.fit(X_train_resampled, y_train_resampled)

def render_mermaid(code: str, height=500):
    components.html(
        f"""
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        <div class="mermaid" style="display: flex; justify-content: center; align-items: center; width: 100%;">
            {code}
        </div>
        """,
        height=height,
    )

st.divider()

st.subheader("🏗️ 앙상블 모델 파이프라인")
render_mermaid("""
flowchart LR
    subgraph Data Processing
        A[(트래픽 데이터)] --> B[전처리 및 원핫인코딩]
        B --> C[Train Test 분할]
        C -->|SMOTE| D[불균형 해소]
    end
    subgraph Model Training
        D --> E1((Random Forest))
        D --> E2((Gradient Boosting))
    end
    subgraph Evaluation
        E1 --> F[성능 비교]
        E2 --> F
    end
    
    classDef data fill:#f9f,stroke:#333,stroke-width:2px;
    classDef model fill:#bbf,stroke:#333,stroke-width:2px;
    class A,B,C,D data;
    class E1,E2 model;
""", height=300)

st.divider()

st.subheader("📈 비즈니스 예측 시나리오 (Sequence Diagram)")
render_mermaid("""
sequenceDiagram
    actor User as 온라인 쇼퍼
    participant Web as 쇼핑몰 사이트
    participant ML as AI 예측 서버
    participant CRM as 마케팅 시스템
    
    User->>Web: 사이트 방문 및 탐색
    Web->>ML: 실시간 세션 데이터 전송
    ML-->>ML: 전처리 및 모델 예측
    alt 구매 확률 높음 (True)
        ML->>CRM: 타겟 마케팅 요청
        CRM-->>User: 맞춤형 팝업 노출
    else 구매 확률 낮음 (False)
        ML->>CRM: 이탈 방지 마케팅 요청
        CRM-->>User: 리마인드 메시지 발송
    end
    User->>Web: 최종 구매 결정
""", height=550)

st.divider()

def get_metrics(y_true, y_pred, y_prob):
    return {
        '정확도(Accuracy)': accuracy_score(y_true, y_pred),
        '정밀도(Precision)': precision_score(y_true, y_pred),
        '재현율(Recall)': recall_score(y_true, y_pred),
        'F1 스코어': f1_score(y_true, y_pred),
        'ROC-AUC': roc_auc_score(y_true, y_prob)
    }

y_test_pred_rf = rf_model.predict(X_test)
y_test_prob_rf = rf_model.predict_proba(X_test)[:, 1]
rf_metrics = get_metrics(y_test, y_test_pred_rf, y_test_prob_rf)

y_test_pred_gb = gb_model.predict(X_test)
y_test_prob_gb = gb_model.predict_proba(X_test)[:, 1]
gb_metrics = get_metrics(y_test, y_test_pred_gb, y_test_prob_gb)

st.subheader("📊 앙상블 모델 성능 지표 비교 (Test 데이터 기준)")
metrics_df = pd.DataFrame([
    {'모델': '랜덤 포레스트 (Random Forest)', '평가지표': k, '점수': v} for k, v in rf_metrics.items()
] + [
    {'모델': '그래디언트 부스팅 (Gradient Boosting)', '평가지표': k, '점수': v} for k, v in gb_metrics.items()
])

fig_comp = px.bar(metrics_df, x='평가지표', y='점수', color='모델', barmode='group',
                  title="Random Forest vs Gradient Boosting 성능 비교",
                  text_auto='.3f', color_discrete_map={'랜덤 포레스트 (Random Forest)': '#1f77b4', '그래디언트 부스팅 (Gradient Boosting)': '#ff7f0e'})
fig_comp.update_layout(yaxis_range=[0, 1.1])
st.plotly_chart(fig_comp, use_container_width=True)

st.divider()

st.subheader("🧩 모델별 오차 행렬 (Confusion Matrix)")
col1, col2 = st.columns(2)

with col1:
    cm_rf = confusion_matrix(y_test, y_test_pred_rf)
    fig_cm_rf = px.imshow(cm_rf, text_auto=True, color_continuous_scale='Blues', 
                          labels=dict(x="예측 클래스", y="실제 클래스", color="빈도"),
                          x=['구매 안 함', '구매 완료'], y=['구매 안 함', '구매 완료'], title="랜덤 포레스트 오차 행렬")
    st.plotly_chart(fig_cm_rf, use_container_width=True)

with col2:
    cm_gb = confusion_matrix(y_test, y_test_pred_gb)
    fig_cm_gb = px.imshow(cm_gb, text_auto=True, color_continuous_scale='Oranges', 
                          labels=dict(x="예측 클래스", y="실제 클래스", color="빈도"),
                          x=['구매 안 함', '구매 완료'], y=['구매 안 함', '구매 완료'], title="부스팅 모델 오차 행렬")
    st.plotly_chart(fig_cm_gb, use_container_width=True)

st.divider()

st.subheader("💡 피처 중요도 (Feature Importances) 비교")
st.markdown("두 모델이 각 특성(Feature)들을 얼마나 중요하게 반영했는지 비교합니다. 앙상블 기법을 거치면서 PageValues 외에도 다른 변수들의 영향력이 어떻게 분산되는지 살펴볼 수 있습니다.")

rf_importances = pd.DataFrame({'Feature': X.columns, 'Importance': rf_model.feature_importances_, 'Model': '랜덤 포레스트'})
gb_importances = pd.DataFrame({'Feature': X.columns, 'Importance': gb_model.feature_importances_, 'Model': '그래디언트 부스팅'})

rf_top10 = rf_importances.sort_values(by='Importance', ascending=False).head(10)
gb_top10 = gb_importances.sort_values(by='Importance', ascending=False).head(10)

col3, col4 = st.columns(2)

with col3:
    fig_rf_imp = px.bar(rf_top10, x='Importance', y='Feature', orientation='h', title='랜덤 포레스트 상위 10개 피처', color_discrete_sequence=['#1f77b4'])
    fig_rf_imp.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_rf_imp, use_container_width=True)

with col4:
    fig_gb_imp = px.bar(gb_top10, x='Importance', y='Feature', orientation='h', title='부스팅 상위 10개 피처', color_discrete_sequence=['#ff7f0e'])
    fig_gb_imp.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_gb_imp, use_container_width=True)
