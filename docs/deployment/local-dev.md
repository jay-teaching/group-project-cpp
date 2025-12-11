# Local Development Guide

This guide describes how to set up the project on your local machine for development and testing.

## Prerequisites

-   **Python 3.12+** installed.
-   **[uv](https://docs.astral.sh/uv/)** installed (recommended for fast dependency management).
-   **VS Code** (recommended editor).

## 1. Installation

Clone the repository and install dependencies using `uv`.

```bash
# Clone the repo
git clone https://github.com/jay-teaching/group-project-cpp.git
cd group-project-cpp

# Install dependencies and create a virtual environment
uv sync
```

!!! tip "Standard Pip"
    If you don't use `uv`, you can standard pip: `pip install -r requirements.txt`.

## 2. Running the API

The backbone of the project is the FastAPI application (`api.py`). You need to run this first so the dashboard has something to talk to.

```bash
uv run uvicorn api:app --reload
```
You should see output indicating the server is running at `http://127.0.0.1:8000`.

## 3. Running the Dashboard

Open a **new terminal** window (keep the API running in the first one) and launch Streamlit:

```bash
uv run streamlit run dashboard.py
```

This will automatically open your browser to `http://localhost:8501`.

## 4. Development Workflow

The project is set up for hot-reloading.

-   **API Changes**: If you modify `api.py` or `prediction.py`, the `uvicorn` server will automatically restart.
-   **Dashboard Changes**: If you modify `dashboard.py`, click "Rerun" in the top-right corner of the browser (or set it to "Always Rerun").

## 5. Running Tests

We use `pytest` for ensuring code quality.

```bash
# Run all tests
uv run pytest
```
