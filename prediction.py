"""
Minimal Azure Functions predictor for the Telco churn model.
"""

import joblib
import pandas as pd
from typing import List


MODEL_COLUMNS: List[str] = [
    "tenure", 
    "MonthlyCharges", 
    "TechSupport_yes",              
    "Contract_month-to-month",      
    "InternetService_fiber optic"   
]

# Load model
BUNDLE = joblib.load("models/telco_logistic_regression.joblib")
MODEL, SCALER = BUNDLE["model"], BUNDLE["scaler"]

def make_prediction(**kwargs: float) -> float:
    """Make a churn prediction given the input features."""
    
 
    try:
        data_row = [
            kwargs["tenure"],
            kwargs["MonthlyCharges"],
            kwargs["TechSupport"],           # API key: TechSupport
            kwargs["ContractMonthToMonth"],  # API key: ContractMonthToMonth
            kwargs["FiberOptic"]             # API key: FiberOptic
        ]
    except KeyError as e:
    
        raise ValueError(f"API parameter missing: {e.args[0]}") from e

   
    features = pd.DataFrame([data_row], columns=pd.Index(MODEL_COLUMNS))

   
    scaled = SCALER.transform(features)
    prob = float(MODEL.predict_proba(scaled)[0, 1])

    print(f"Churn probability: {prob:.4f}")
    return prob