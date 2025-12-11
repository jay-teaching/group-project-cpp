"""API for making churn predictions using a FastAPI server.

Add fastapi and uvicorn to your environment with:
    uv add fastapi uvicorn

To serve the API, run:
    uv run uvicorn api:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from prediction import make_prediction


# Field names match those used in the model training
# Aliases are more user-friendly names for the API
class Customer(BaseModel):
    tenure: int = Field(..., description="Number of months the customer has stayed with the company")
    monthly_charges: float = Field(..., alias="MonthlyCharges", description="The amount charged to the customer monthly")
    has_tech_support: bool = Field(..., alias="TechSupport", description="Does the customer have tech support?")
    is_month_to_month: bool = Field(..., alias="ContractMonthToMonth", description="Is the contract month-to-month?")
    has_fiber_optic: bool = Field(..., alias="FiberOptic", description="Is the internet service fiber optic?")

app = FastAPI()


@app.post("/predict")
def predict(customer: Customer):
    """Make a churn prediction for a customer."""
    
    model_input = {
        "tenure": customer.tenure,
        "MonthlyCharges": customer.monthly_charges,
        "TechSupport": customer.has_tech_support,
        "ContractMonthToMonth": customer.is_month_to_month,
        "FiberOptic": customer.has_fiber_optic,
    }
    
    prediction = make_prediction(**model_input)
    
    return {"prediction": prediction}

@app.get("/schema")
def predict_schema():
    """Describe the expected fields for /predict."""
    return Customer.model_json_schema()
