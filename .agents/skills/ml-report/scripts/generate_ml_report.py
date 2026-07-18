"""
이 스크립트는 범용 머신러닝 리포트 생성을 위해 데이터를 로드하고,
EDA (탐색적 데이터 분석) 시각화 및 머신러닝 모델 학습(3종 이상)과 
평가(5종 지표)를 수행한 뒤 그 결과를 이미지와 텍스트 형태로 출력 디렉토리에 저장합니다.
"""
import os
import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
import zipfile
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from imblearn.over_sampling import SMOTE

def load_dataset(path):
    if path.endswith('.zip'):
        with zipfile.ZipFile(path, 'r') as z:
            file_list = z.namelist()
            with z.open(file_list[0]) as f:
                return pd.read_csv(f)
    elif path.endswith('.csv'):
        return pd.read_csv(path)
    else:
        raise ValueError("지원하지 않는 파일 형식입니다.")

def main():
    parser = argparse.ArgumentParser(description="Generate ML Report Assets")
    parser.add_argument("dataset_path", help="Path to dataset (.csv or .zip)")
    parser.add_argument("target_column", help="Target column name")
    parser.add_argument("problem_type", help="Problem type: classification or regression")
    parser.add_argument("output_dir", help="Directory to save outputs")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Loading data from {args.dataset_path}...")
    df = load_dataset(args.dataset_path)
    
    # 기초 전처리
    df = df.dropna()
    
    # 1. EDA 시각화 및 표 생성
    print("Performing EDA...")
    tables_output = []
    
    # 타겟 컬럼 타입 처리
    if df[args.target_column].dtype == object or df[args.target_column].dtype == bool:
        df[args.target_column] = df[args.target_column].astype(int)
        
    num_cols = df.select_dtypes(include=[np.number]).columns.drop(args.target_column).tolist()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    # 범주형 변수가 있으면 첫 번째 변수로 교차표 및 막대그래프
    if cat_cols:
        cat_col = cat_cols[0]
        crosstab = pd.crosstab(df[cat_col], df[args.target_column])
        tables_output.append(f"### 교차표 ({cat_col} vs {args.target_column})\n\n{crosstab.to_markdown()}")
        
        crosstab.plot(kind='bar', figsize=(8, 5))
        plt.title(f"{cat_col} 에 따른 {args.target_column} 분포")
        plt.tight_layout()
        plt.savefig(os.path.join(args.output_dir, "eda_bar.png"))
        plt.close()
        
    # 수치형 변수가 있으면 첫 번째 변수로 기술통계 및 박스플롯
    if num_cols:
        num_col = num_cols[0]
        desc = df.groupby(args.target_column)[num_col].describe()
        tables_output.append(f"### 기술통계 ({num_col} by {args.target_column})\n\n{desc.to_markdown()}")
        
        df.boxplot(column=num_col, by=args.target_column, figsize=(8, 5))
        plt.title(f"{args.target_column} 별 {num_col} 박스플롯")
        plt.suptitle("")
        plt.tight_layout()
        plt.savefig(os.path.join(args.output_dir, "eda_box.png"))
        plt.close()

    with open(os.path.join(args.output_dir, "tables.md"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(tables_output))
        
    # 2. ML 모델링 및 평가
    print("Training models...")
    df_ml = pd.get_dummies(df, drop_first=True)
    X = df_ml.drop(args.target_column, axis=1)
    y = df_ml[args.target_column]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if args.problem_type == 'classification' else None)
    
    if args.problem_type == 'classification':
        try:
            smote = SMOTE(random_state=42)
            X_train, y_train = smote.fit_resample(X_train, y_train)
        except Exception as e:
            print(f"SMOTE failed, skipping... {e}")
            
        models = {
            'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        }
        
        metrics_list = []
        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred
            
            metrics = {
                '모델': name,
                'Accuracy': accuracy_score(y_test, y_pred),
                'Precision': precision_score(y_test, y_pred, zero_division=0),
                'Recall': recall_score(y_test, y_pred, zero_division=0),
                'F1-Score': f1_score(y_test, y_pred, zero_division=0),
                'ROC-AUC': roc_auc_score(y_test, y_prob)
            }
            metrics_list.append(metrics)
            
        metrics_df = pd.DataFrame(metrics_list)
        metrics_df.to_csv(os.path.join(args.output_dir, "metrics.csv"), index=False)
        
        # 성능 시각화
        metrics_df.set_index('모델').plot(kind='bar', figsize=(10, 6))
        plt.title("모델별 5대 평가지표 비교")
        plt.legend(loc='lower right')
        plt.tight_layout()
        plt.savefig(os.path.join(args.output_dir, "model_comparison.png"))
        plt.close()
        
    print(f"All assets generated successfully in {args.output_dir}")

if __name__ == "__main__":
    main()
