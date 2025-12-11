import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")

with app.setup:
    from pathlib import Path

    import joblib
    import marimo as mo
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.metrics import (accuracy_score, classification_report,
                                 confusion_matrix, f1_score, roc_auc_score)
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler


@app.cell(hide_code=True)
def _():
    mo.md("""
    # Telco Churn – Feature Engineering Analysis

    ## Workflow
    1. Load and explore data
    2. Analyze categorical features to find high-impact predictors
    3. Engineer features based on findings
    4. Compare baseline vs. engineered model performance
    """)
    return


@app.cell
def _():
    DATA_PATH = Path("input/WA_Fn-UseC_-Telco-Customer-Churn.csv")
    MODEL_SAVE_PATH = Path("models/telco_logistic_regression.joblib")

    SAVE_MODEL = True
    TEST_SIZE = 0.20
    C_VALUE = 1.0
    MAX_ITER = 1000
    SOLVER = "liblinear"
    RANDOM_STATE = 42
    return (
        C_VALUE,
        DATA_PATH,
        MAX_ITER,
        MODEL_SAVE_PATH,
        SAVE_MODEL,
        SOLVER,
        TEST_SIZE,
        RANDOM_STATE,
    )


@app.cell
def _(DATA_PATH):
    telco_df = pd.read_csv(DATA_PATH)
    mo.md(f"## Step 1: Load Data\n\nDataset shape: **{telco_df.shape[0]} rows × {telco_df.shape[1]} columns**")
    return (telco_df,)


@app.cell
def _(telco_df):
    # Data cleaning
    cleaned = telco_df.copy()
    if "customerID" in cleaned.columns:
        cleaned = cleaned.drop(columns=["customerID"])
    cleaned["TotalCharges"] = pd.to_numeric(cleaned["TotalCharges"], errors="coerce")
    cleaned = cleaned.dropna()
    
    for column in cleaned.select_dtypes(include="object"):
        cleaned[column] = cleaned[column].str.lower().str.strip()
    
    churn_counts = cleaned["Churn"].value_counts()
    churn_rate = (cleaned["Churn"] == "yes").mean()
    
    mo.md(f"""
    ## Step 2: Data Cleaning & Churn Overview
    
    - Records after cleaning: **{len(cleaned):,}**
    - Churn distribution:
      - No churn: {churn_counts.get('no', 0):,} ({1-churn_rate:.1%})
      - Churn: {churn_counts.get('yes', 0):,} ({churn_rate:.1%})
    """)
    return (cleaned,)


@app.cell
def _(cleaned):
    mo.md("""
    ## Step 3: Exploratory Data Analysis – Finding High-Impact Features
    
    Analyzing categorical features to identify which ones have the strongest relationship with churn.
    """)
    return


@app.cell
def _(cleaned):
    # Analyze Contract type
    contract_churn = cleaned.groupby("Contract")["Churn"].apply(
        lambda x: (x == "yes").sum() / len(x)
    ).sort_values(ascending=False)
    
    mo.md(f"""
    ### Finding #1: Contract Type is a Strong Predictor
    
    | Contract | Churn Rate | Count |
    |----------|-----------|-------|
    | month-to-month | {contract_churn.iloc[0]:.1%} | {(cleaned['Contract'] == 'month-to-month').sum():,} |
    | one year | {contract_churn.iloc[1]:.1%} | {(cleaned['Contract'].str.contains('1 year|one year', na=False)).sum():,} |
    | two year | {contract_churn.iloc[2]:.1%} | {(cleaned['Contract'].str.contains('2 year|two year', na=False)).sum():,} |
    
    **Insight**: Month-to-month customers have **{(contract_churn.iloc[0] / contract_churn.iloc[2]):.1f}x higher churn** than two-year contracts!
    
    **Action**: Add `Contract_month-to-month` as a feature.
    """)
    return


@app.cell
def _(cleaned):
    # Analyze Internet Service type
    internet_churn = cleaned.groupby("InternetService")["Churn"].apply(
        lambda x: (x == "yes").sum() / len(x)
    ).sort_values(ascending=False)
    
    mo.md(f"""
    ### Finding #2: Internet Service Type is a Strong Predictor
    
    | Service | Churn Rate | Count |
    |---------|-----------|-------|
    | fiber optic | {internet_churn.iloc[0]:.1%} | {(cleaned['InternetService'] == 'fiber optic').sum():,} |
    | dsl | {internet_churn.iloc[1]:.1%} | {(cleaned['InternetService'] == 'dsl').sum():,} |
    | no | {internet_churn.iloc[2]:.1%} | {(cleaned['InternetService'] == 'no').sum():,} |
    
    **Insight**: Fiber optic customers have **{(internet_churn.iloc[0] / internet_churn.iloc[2]):.1f}x higher churn** than non-users!
    
    **Action**: Add `InternetService_fiber optic` as a feature.
    """)
    return


@app.cell
def _():
    mo.md("""
    ## Step 4: Feature Engineering
    
    Based on EDA findings, we engineer features from Contract type and InternetService.
    """)
    return


@app.cell
def _():
    BASELINE_FEATURES = ["tenure", "MonthlyCharges", "TechSupport_yes"]
    
    ENGINEERED_FEATURES = BASELINE_FEATURES + ["Contract_month-to-month", "InternetService_fiber optic"]
    
    return (BASELINE_FEATURES, ENGINEERED_FEATURES)


@app.cell
def _(ENGINEERED_FEATURES):
    def preprocess_telco(df: pd.DataFrame):
        cleaned = df.copy()
        if "customerID" in cleaned.columns:
            cleaned = cleaned.drop(columns=["customerID"])
        cleaned["TotalCharges"] = pd.to_numeric(
            cleaned["TotalCharges"], errors="coerce"
        )
        cleaned = cleaned.dropna()

        for column in cleaned.select_dtypes(include="object"):
            cleaned[column] = cleaned[column].str.lower().str.strip()

        # One-hot encode without dropping first to preserve all contract types
        X = pd.get_dummies(cleaned.drop(columns=["Churn"]), drop_first=False, dtype=int)

        # Choose engineered features
        available_features = [f for f in ENGINEERED_FEATURES if f in X.columns]
        missing = set(ENGINEERED_FEATURES) - set(available_features)
        
        if missing:
            print(f"⚠️ Missing: {missing}")
            print(f"Available columns: {X.columns.tolist()}")
        
        X = X[available_features]
        y = cleaned["Churn"].map({"yes": 1, "no": 0}).to_numpy()

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        return cleaned, X_scaled, y, scaler, available_features

    return (preprocess_telco,)


@app.cell
def _(preprocess_telco, telco_df):
    cleaned_df, X_scaled, y, scaler, feature_names = preprocess_telco(telco_df)
    mo.md(f"**Features used**: {', '.join(feature_names)}")
    return X_scaled, scaler, y


@app.cell
def _():
    mo.md("## Step 5: Model Training & Evaluation")
    return


@app.cell
def _(C_VALUE, MAX_ITER, SOLVER, TEST_SIZE, X_scaled, y, RANDOM_STATE):
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    # Model 1: Logistic Regression
    model_lr = LogisticRegression(
        solver=SOLVER, C=C_VALUE, max_iter=MAX_ITER, random_state=RANDOM_STATE
    )
    model_lr.fit(X_train, y_train)

    y_pred_lr = model_lr.predict(X_test)
    y_proba_lr = model_lr.predict_proba(X_test)[:, 1]

    metrics_lr = {
        "accuracy": accuracy_score(y_test, y_pred_lr),
        "f1": f1_score(y_test, y_pred_lr),
        "roc_auc": roc_auc_score(y_test, y_proba_lr),
        "confusion": confusion_matrix(y_test, y_pred_lr),
        "report": classification_report(y_test, y_pred_lr),
    }
    
    # Model 2: Random Forest
    model_rf = RandomForestClassifier(
        n_estimators=100, max_depth=10, min_samples_split=10,
        random_state=RANDOM_STATE, n_jobs=-1
    )
    model_rf.fit(X_train, y_train)

    y_pred_rf = model_rf.predict(X_test)
    y_proba_rf = model_rf.predict_proba(X_test)[:, 1]

    metrics_rf = {
        "accuracy": accuracy_score(y_test, y_pred_rf),
        "f1": f1_score(y_test, y_pred_rf),
        "roc_auc": roc_auc_score(y_test, y_proba_rf),
        "confusion": confusion_matrix(y_test, y_pred_rf),
        "report": classification_report(y_test, y_pred_rf),
    }
    
    # Model 3: Gradient Boosting
    model_gb = GradientBoostingClassifier(
        n_estimators=100, max_depth=5, learning_rate=0.1,
        random_state=RANDOM_STATE
    )
    model_gb.fit(X_train, y_train)

    y_pred_gb = model_gb.predict(X_test)
    y_proba_gb = model_gb.predict_proba(X_test)[:, 1]

    metrics_gb = {
        "accuracy": accuracy_score(y_test, y_pred_gb),
        "f1": f1_score(y_test, y_pred_gb),
        "roc_auc": roc_auc_score(y_test, y_proba_gb),
        "confusion": confusion_matrix(y_test, y_pred_gb),
        "report": classification_report(y_test, y_pred_gb),
    }
    
    return metrics_lr, metrics_rf, metrics_gb, model_lr, model_rf, model_gb


@app.cell
def _(metrics_lr, metrics_rf, metrics_gb):
    mo.md(f"""
    ### Performance Metrics – Model Comparison
    
    | Model | Accuracy | F1-Score | ROC-AUC |
    |-------|----------|----------|---------|
    | Logistic Regression | {metrics_lr['accuracy']:.4f} | {metrics_lr['f1']:.4f} | {metrics_lr['roc_auc']:.4f} |
    | Random Forest | {metrics_rf['accuracy']:.4f} | {metrics_rf['f1']:.4f} | {metrics_rf['roc_auc']:.4f} |
    | Gradient Boosting | {metrics_gb['accuracy']:.4f} | {metrics_gb['f1']:.4f} | {metrics_gb['roc_auc']:.4f} |
    """)
    return


@app.cell
def _(metrics_lr):
    mo.md(f"""
    ### Logistic Regression – Confusion Matrix
    ```
    {metrics_lr['confusion']}
    ```
    """)
    return


@app.cell
def _(metrics_lr):
    mo.md(f"""
    ### Logistic Regression – Classification Report
    ```
    {metrics_lr['report']}
    ```
    """)
    return


@app.cell
def _(metrics_rf):
    mo.md(f"""
    ### Random Forest – Confusion Matrix
    ```
    {metrics_rf['confusion']}
    ```
    """)
    return


@app.cell
def _(metrics_rf):
    mo.md(f"""
    ### Random Forest – Classification Report
    ```
    {metrics_rf['report']}
    ```
    """)
    return


@app.cell
def _(metrics_gb):
    mo.md(f"""
    ### Gradient Boosting – Confusion Matrix
    ```
    {metrics_gb['confusion']}
    ```
    """)
    return


@app.cell
def _(metrics_gb):
    mo.md(f"""
    ### Gradient Boosting – Classification Report
    ```
    {metrics_gb['report']}
    ```
    """)
    return


@app.cell
def _():
    mo.md("""
    ## Step 6: Model Selection Rationale
    
    ### Analysis & Decision
    
    While Random Forest and Gradient Boosting show marginal improvements over Logistic Regression,
    we have chosen to move forward with **Logistic Regression** for the following reasons:
    
    **Performance:**
    - Logistic Regression achieves almost similar performance (within 1-2% of ensemble methods)
    - The marginal performance gains from more complex models do not justify added complexity
    
    **Interpretability:**
    - Logistic Regression provides clear, interpretable coefficients
    - Easy to explain feature importance and churn drivers to stakeholders
    
    **Computational Efficiency:**
    - Significantly faster training and inference
    - Lower memory footprint for deployment
    - Easier to maintain and update in production
    
    **Simplicity & Reliability:**
    - Less prone to overfitting on this dataset
    - Easier to debug and troubleshoot
    - Industry-standard approach for churn prediction
    
    ### Conclusion
    
    For this use case, we argue that Logistic Regression strikes the optimal balance between predictive power,
    interpretability, and practical deployment considerations.
    """)
    return


@app.cell
def _():
    mo.md("## Step 7: Final Model – Logistic Regression")
    return


@app.cell
def _(model_lr, scaler, feature_names, metrics_lr):
    mo.md(f"""
    ### Final Model Specifications
    
    **Algorithm**: Logistic Regression (liblinear solver)
    
    **Features** ({len(feature_names)}):
    ```
    {', '.join(feature_names)}
    ```
    
    **Hyperparameters**:
    - C (inverse regularization): 1.0
    - Max iterations: 1000
    - Solver: liblinear
    - Random state: 42
    
    **Final Performance Metrics**:
    
    | Metric | Score |
    |--------|-------|
    | Accuracy | {metrics_lr['accuracy']:.4f} |
    | F1-Score | {metrics_lr['f1']:.4f} |
    | ROC-AUC | {metrics_lr['roc_auc']:.4f} |
    """)
    return


@app.cell
def _(MODEL_SAVE_PATH, SAVE_MODEL, model_lr, scaler):
    if SAVE_MODEL:
        joblib.dump({"model": model_lr, "scaler": scaler}, MODEL_SAVE_PATH)
    return

if __name__ == "__main__":
    app.run()


