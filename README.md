# Fraud Detection API

A REST API for detecting potentially fraudulent transactions using a machine learning model deployed with **FastAPI**.

The application validates transaction data with **Pydantic**, loads the trained ML model once during application startup, provides single and batch prediction endpoints, and logs high-risk transactions in the background.

## Features

- REST API built with FastAPI
- Pydantic-based request validation
- Machine learning model for fraud prediction
- Model loading with FastAPI lifespan
- Single transaction prediction
- Batch transaction prediction
- Fraud probability and risk level calculation
- Background logging of high-risk transactions
- Automated tests with pytest
- Continuous Integration with GitHub Actions
- Interactive API documentation with Swagger UI

## Tech Stack

- **Python 3.12**
- **FastAPI** — REST API framework
- **Uvicorn** — ASGI server
- **Pydantic** — data validation
- **scikit-learn** — machine learning
- **pandas** — data processing
- **NumPy** — numerical computing
- **joblib** — model serialization
- **pytest** — automated testing
- **GitHub Actions** — CI

## Project Structure

```text
fraud-detection-fastapi/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
│
├── tests/
│   └── test_main.py
│
├── models/
│   └── model.joblib
│
├── logs/
│   └── suspicious_transactions.log
│
├── .gitignore
├── README.md
├── requirements.txt
└── train_model.py
```

> `model.joblib` and log files are generated locally and are excluded from version control.

## Getting Started

### Prerequisites

Make sure you have installed:

- Python 3.12 or newer
- Git

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/fraud-detection-fastapi.git
cd fraud-detection-fastapi
```

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Model Preparation

Before starting the API, generate the machine learning model:

```bash
python train_model.py
```

The trained model is saved to:

```text
models/model.joblib
```

## Running the API

Start the development server with:

```bash
python -m uvicorn src.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### API Documentation

FastAPI automatically provides interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

## API Endpoints

### `GET /health`

Checks whether the API is running and the machine learning model has been loaded successfully.

### `POST /v1/predict`

Predicts the fraud probability for a single transaction.

### Risk Levels

The API assigns a risk level based on the predicted fraud probability:

| Probability | Risk Level |
|---:|---|
| `< 0.30` | `LOW` |
| `0.30 – < 0.70` | `MEDIUM` |
| `>= 0.70` | `HIGH` |

A transaction is classified as fraudulent when:

```text
fraud_probability >= 0.50
```

Transactions with `HIGH` risk are additionally written to the background log.

### `POST /v1/predict/batch`

Predicts fraud probability for multiple transactions in a single request.

The maximum batch size is **50 transactions**.

## Input Validation

Transaction data is validated using Pydantic.

The following constraints are enforced:

| Field | Validation |
|---|---|
| `user_id` | Integer greater than 0 |
| `amount` | Greater than 0 and at most 100,000 |
| `merchant_category` | One of the supported categories |
| `location_lat` | Between -90 and 90 |
| `location_lon` | Between -180 and 180 |
| `is_international` | Boolean |

Supported merchant categories:

```text
grocery
electronics
travel
entertainment
other
```

Invalid request data results in:

```text
422 Unprocessable Entity
```

Batch requests containing more than 50 transactions result in:

```text
400 Bad Request
```

## Testing

The project includes automated tests for:

- API health check
- Valid transaction prediction
- Input validation
- Invalid transaction data
- Batch prediction
- Batch size limitation
- Prediction response structure

Run the test suite with:

```bash
python -m pytest tests/
```

Current test result:

```text
10 passed
```

## Continuous Integration

The project uses **GitHub Actions** to automatically test the application.

The workflow is located at:

```text
.github/workflows/tests.yml
```

On every push to `main` and on pull requests targeting `main`, the workflow:

1. Checks out the repository
2. Sets up Python 3.12
3. Installs project dependencies
4. Generates the machine learning model
5. Runs the automated test suite

A successful workflow confirms that the project passes all automated tests.

## Error Handling

The API returns appropriate HTTP status codes for common errors:

| Status Code | Description |
|---:|---|
| `200` | Successful request |
| `400` | Invalid batch size |
| `422` | Validation error |
| `503` | ML model is not loaded |

## License

This project was created for educational purposes as part of the **Advanced Python for Data Science & Big Data** practical assignment.