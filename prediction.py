"""
Minimal Azure Functions predictor for the Telco churn model.

Expect only the features defined in the model built by `telco_marimo.py`.


"""

import joblib
import pandas as pd

# Edit this list to match the features used in your model
FEATURE_ORDER = ["tenure", "MonthlyCharges", "TechSupport_yes", "Contract_month-to-month", "InternetService_fiber optic"]


BUNDLE = joblib.load("models/telco_logistic_regression.joblib")
MODEL, SCALER = BUNDLE["model"], BUNDLE["scaler"]


def make_prediction(**kwargs: float) -> float:
    "Make a churn prediction given the input features."

    try:
        data_row = [
            kwargs["tenure"],
            kwargs["MonthlyCharges"],
            kwargs["TechSupport"],         
            kwargs["ContractMonthToMonth"], 
            kwargs["FiberOptic"]           
        ]
    except KeyError as e:
        raise ValueError(f"Missing Feature: {e.args[0]}") from e

    
    features = pd.DataFrame([data_row], columns=MODEL_COLUMNS)

    # Scale features with saved scaler
    scaled = SCALER.transform(features)

    # Predict with saved model
    prob = float(MODEL.predict_proba(scaled)[0, 1])

    print(f"Churn probability: {prob:.4f}")
    return prob