# Vehicle Safety Prediction

## Overview

The **Vehicle Safety Prediction System** is a full-stack application that uses machine learning to predict vehicle safety based on sensor inputs. The system classifies the safety of the vehicle into three categories: `SAFE`, `RISK`, and `HIGH RISK`. The backend is powered by **FastAPI** and the frontend is built with **React**. Prediction history is stored in an **SQLite** database for tracking and analysis.

---

## Features

- **Real-time Safety Prediction**: Classifies vehicle safety based on sensor data.
- **Prediction History**: Stores each prediction with sensor values for traceability.
- **User Dashboard**: A React-based UI for interaction with real-time safety predictions and history.

---

## Project Structure

```text
vehicle_safety/
├── backend/
│   ├── main.py            # FastAPI app and API routes
│   ├── ml.py              # Model loading and prediction logic
│   ├── database.py        # Database setup and session management
│   ├── models.py          # Database schema for predictions
│   ├── schemas.py         # Pydantic models for validation
│   ├── model.pkl          # Pre-trained model artifact
│   ├── predictions.db     # SQLite database storing prediction history
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── package.json       # Frontend dependencies and scripts
│   ├── public/            # Static assets
│   └── src/
│       ├── index.js       # React entry point
│       ├── components/App.js # Main app component
│       └── styles/App.css # Styling for the frontend
├── data/
│   └── vehicle_dataset.csv  # Dataset reference (for review/demo)
└── README.md              # Project overview and setup guide
```

---

## How it Works

### Backend

* The backend runs on **FastAPI**, where sensor data is sent via the `POST /predict` endpoint for processing.
* It loads a pre-trained model from `backend/model.pkl` (or `MODEL_PATH` env var).
* The prediction is returned to the frontend with a safety status of `SAFE`, `RISK`, or `HIGH RISK`.
* Each prediction is saved in the **SQLite database** (`predictions.db`), which stores all sensor data, predictions, and timestamps.

### Frontend

* The frontend is built with **React** and interacts with the backend to:

  * Display real-time safety predictions.
  * Show a history of past predictions.
* The app is user-friendly, displaying safety statuses with corresponding colors and messages.

---

## Backend Setup

1. **Navigate to the `backend` directory**:

   ```bash
   cd backend
   ```

2. **Create a Python virtual environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server**:

   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

**Backend URLs:**

* API: `http://localhost:8000`
* Swagger docs (for API testing): `http://localhost:8000/docs`

---

## Frontend Setup

1. **Navigate to the `frontend` directory**:

   ```bash
   cd frontend
   ```

2. **Install the required dependencies**:

   ```bash
   npm install
   ```

3. **Start the React application**:

   ```bash
   npm start
   ```

**Frontend URL:**

* App: `http://localhost:3000`

---

## API Endpoints

* **GET /**: Health check endpoint.
* **POST /predict**: Send sensor data to get a safety prediction:

  * Example request body:

    ```json
    {
      "distance": 100,
      "ttc": 2.5,
      "axis": 0.1,
      "speed": 50,
      "steering_angle": 10,
      "relative_velocity": 5
    }
    ```
  * Example response:

    ```json
    {
      "predicted_status": "SAFE",
      "message": "✅ Vehicle is operating safely."
    }
    ```
* **GET /history**: Fetch the latest prediction history (supports `limit` parameter).

  * Example request: `GET /history?limit=50`

---

## How Prediction Works

1. **Backend**: Loads the model artifact (`model.pkl`) and runs predictions on sensor input.
2. **Feature Set**:

   * **Distance**
   * **Time-to-Collision (TTC)**
   * **Axis**
   * **Speed**
   * **Steering angle**
   * **Relative velocity**
3. **Class Mapping**:

   * `0 -> HIGH RISK`
   * `1 -> RISK`
   * `2 -> SAFE`

---

## Notes

* **Frontend** makes requests to the backend at `http://localhost:8000`.
* **Prediction history** is stored in the **SQLite database** (`predictions.db`).
* Runtime inference uses a fixed `backend/model.pkl`; model training is not part of this repository workflow.
* **Scalable Deployment**: This project can be deployed to cloud platforms like AWS, Heroku, or DigitalOcean for production use.

---

## Future Enhancements

* Add automated tests for the API and prediction flow.
* Improve error handling for API inputs.
* Implement deployment to cloud for public access.
* Enhance frontend UI for better user experience.
