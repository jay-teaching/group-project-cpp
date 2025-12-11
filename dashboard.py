import requests
import streamlit as st

DEV_API = "http://127.0.0.1:8000/predict"
PROD_API = "https://predictingforjay.azurewebsit..."


def fetch_prediction(payload: dict) -> dict:
    """Call the prediction API and return the JSON response"""
    response = requests.post(DEV_API, json=payload, timeout=5)
    
    # --- Testing ---
    if response.status_code == 422:
        
        st.error("数据格式错误 (422)！详细信息如下：")
        st.json(response.json()) 
        response.raise_for_status() 
    # -------------------

    response.raise_for_status()
    return response.json()


def fetch_prediction_from_production(params: dict) -> dict:
    """Call the production API and return the response.

    Our serverless function doesnt support JSON in or out
    Plus we need to increase the timeout for cold starts.
    """
    url = PROD_API + "&" + "&".join(f"{k}={v}" for k, v in params.items())
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response

### Streamlit Dashboard for Telco Churn Prediction

# --- Page Config ---
st.set_page_config(
    page_title="Telco Churn Predictor",
    page_icon="📊",
    layout="centered"
)

# --- Header ---
st.title("📊 Telco Churn Prediction")
st.markdown("Enter customer details below to estimate churn probability.")
st.markdown("---")

# --- Form Section ---
with st.form("churn_prediction_form"):
    st.subheader("Customer Profile")
    
    # Row 1: Numeric Inputs
    col_left, col_right = st.columns(2)
    
    with col_left:
        tenure = st.slider("Tenure (months)", min_value=0, max_value=120, value=24)
        
    with col_right:
        monthly = st.number_input(
            "Monthly Charges ($)", 
            min_value=0.0, 
            max_value=1000.0, 
            step=0.5, 
            value=70.0
        )

    # Row 2: Services & Contract
    # Improvement 1: Using smaller markdown header (H5) to indicate subordination
    st.markdown("##### Services & Contract Details")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Improvement 2: Added 'help' parameter for hover tooltips
        techsupport = st.checkbox(
            "Tech Support", 
            value=False,
            help="Does the customer subscribe to the add-on technical support plan?"
        )
    with c2:
        fiber_optic = st.checkbox(
            "Fiber Optic", 
            value=False,
            help="Is the customer connected via high-speed fiber optic internet?"
        )
    with c3:
        contract_mtm = st.checkbox(
            "Month-to-Month", 
            value=True,
            help="Is the customer on a flexible month-to-month contract (no long-term commitment)?"
        )

    # Improvement 3: Adding vertical whitespace before the button
    st.markdown("<br>", unsafe_allow_html=True)
    
    submitted = st.form_submit_button("Run Prediction", type="primary", use_container_width=True)

# --- Logic & Visualization ---
if submitted:
    # Construct Payload
    payload = {
        "tenure": int(tenure),
        "MonthlyCharges": float(monthly),
        "TechSupport": 1 if techsupport else 0,
        "ContractMonthToMonth": 1 if contract_mtm else 0,
        "FiberOptic": 1 if fiber_optic else 0,
    }

    with st.spinner("Analyzing customer data..."):
        data = fetch_prediction(payload)

    if data:
        churn_prob = data.get("prediction", 0.0)
        percentage = churn_prob * 100

        st.divider()
        st.subheader("Prediction Result")
        
        m_col1, m_col2 = st.columns([1, 2])
        
        with m_col1:
            is_high_risk = churn_prob > 0.5
            status_label = "High Risk ⚠️" if is_high_risk else "Low Risk ✅"
            
            st.metric(
                label="Churn Probability", 
                value=f"{percentage:.2f}%", 
                delta=status_label,
                delta_color="inverse" if is_high_risk else "normal"
            )

        with m_col2:
            st.write("Risk Meter:")
            st.progress(churn_prob, text=f"Risk Level: {percentage:.1f}%")
            
            if is_high_risk:
                st.warning("Customer is likely to churn. Action recommended.")
            else:
                st.success("Customer is stable. Keep up the good service.")

        with st.expander("View Raw API Response"):
            st.json(data)