# Azure Deployment Guide

This guide walks you through deploying the Churn Prediction model to **Azure Functions** using the "Flex Consumption" plan.

## Prerequisites

-   An active **Azure Subscription**.
-   **VS Code** with the **Azure Functions** extension installed.
-   The **Azure CLI** (or usage of Cloud Shell).

## Deployment Steps

### 1. Create the Function App (Azure Portal)

1.  Log in to the [Azure Portal](https://portal.azure.com).
2.  Search for **Function App** and click **Create**.
3.  **Basics Tab**:
    *   **Plan**: Select **Flex Consumption**.
    *   **Resource Group**: Select your group.
    *   **Function App Name**: Enter a globally unique name (e.g., `telco-churn-api`).
    *   **Runtime Stack**: Python.
    *   **Version**: 3.11 or 3.12 (Recommended).
    *   **Region**: Select your region (e.g., `Switzerland North`).
4.  **Storage**: Use default or existing account.
5.  **Review + Create**: Click create and wait for deployment.

### 2. Configure Local Project

In your local VS Code environment:

1.  Open the Command Palette (`Ctrl+Shift+P`).
2.  Type: `Azure Functions: Create Function`.
3.  Select **HTTP Trigger**.
4.  Name it `predict`.
5.  Auth Level: **Function**.

!!! important "Dependencies"
    Ensure your `requirements.txt` includes all necessary libraries:
    ```text
    azure-functions
    scikit-learn
    pandas
    joblib
    ```

### 3. Deploy from VS Code

1.  Click the **Azure** icon in the VS Code sidebar.
2.  Under **Resources**, find your Function App.
3.  Right-click the Function App and select **Deploy to Function App...**.
4.  Select your project folder.
5.  Wait for the deployment to finish.

## Verifying the Deployment

Once deployed, you can test the API directly.

1.  In the **Azure** sidebar in VS Code, expand your Function App -> **Functions**.
2.  Right-click `predict` and select **Execute Function Now...**.
3.  Enter the sample JSON body:
    ```json
    {
        "tenure": 24,
        "MonthlyCharges": 70.0,
        "TechSupport": 0,
        "ContractMonthToMonth": 1,
        "FiberOptic": 0
    }
    ```
4.  You should receive a response like: `{"prediction": 0.35}`.

## connecting the Dashboard

Finally, update your Streamlit dashboard to point to the live API.

1.  Open `dashboard.py`.
2.  Find the `PROD_API` variable.
3.  Update it with your function URL (get this from the Azure Portal or VS Code context menu).

```python
PROD_API = "https://<your-app-name>.azurewebsites.net/api/predict?code=<your-function-key>"
```
