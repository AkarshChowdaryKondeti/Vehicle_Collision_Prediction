# Vehicle Safety Prediction

## Overview

The **Vehicle Safety Prediction System** is a full-stack application that uses machine learning to predict vehicle safety from obstacle distance and relative velocity. The system returns one of four statuses: `SAFE`, `RISK`, `HIGH RISK`, or `COLLIDED`. The backend is powered by **FastAPI**, the frontend is built with **React**, and prediction history is stored in an **SQLite** database for traceability and basic analytics.

---

## Features

- **Real-time Safety Prediction**: Classifies vehicle safety based on live input values and computed TTC.
- **Prediction History**: Stores each prediction with sensor values for traceability.
- **Statistics Dashboard**: Shows status distribution using pie and bar charts derived from stored history.
- **User Dashboard**: A React-based UI with separate `Predict`, `History`, and `Statistics` views.

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
│       ├── components/App.js          # App shell and tab switching
│       ├── components/PredictView.js  # Prediction input/output view
│       ├── components/HistoryView.js  # Prediction history table
│       ├── components/StatisticsView.js # Statistics charts
│       ├── components/statusConfig.js # Shared status colors and normalization
│       └── styles/App.css # Styling for the frontend
├── data/
│   └── vehicle_dataset.csv  # Dataset reference (for review/demo)
├── view_predictions.py      # Helper script to inspect stored DB rows
└── README.md              # Project overview and setup guide
```

---

## How it Works

### Backend

* The backend runs on **FastAPI**, where sensor data is sent via the `POST /predict` endpoint for processing.
* It loads a pre-trained model from `backend/model.pkl` (or `MODEL_PATH` env var).
* The prediction is returned to the frontend with a safety status, TTC when applicable, and a short recommendation-style message.
* Each prediction is saved in the **SQLite database** (`predictions.db`), which stores all sensor data, predictions, and timestamps.

### Frontend

* The frontend is built with **React** and interacts with the backend to:

  * Display real-time safety predictions.
  * Show a history of past predictions.
  * Visualize status distribution in the `Statistics` tab.
* The app displays safety statuses with corresponding colors, TTC values, and descriptive messages.

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
      "distance": 30,
      "relative_velocity": 5
    }
    ```
  * Example response:

    ```json
    {
      "predicted_status": "SAFE",
      "ttc": 6.0,
      "message": "SAFE: TTC is 6.00 seconds. No immediate collision risk detected. Keep a safe buffer and continue monitoring traffic."
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
4. **Edge-Case Handling**:

   * `distance = 0` is treated as `COLLIDED`
   * very small distance with positive closing speed is treated as `HIGH RISK`
   * TTC is omitted when relative velocity is zero or negative

5. **Response Messaging**:

   * `SAFE`: `SAFE: TTC is 6.00 seconds. No immediate collision risk detected. Keep a safe buffer and continue monitoring traffic.`
   * `RISK`: `RISK: Caution advised. Reduce speed slightly and prepare to brake if the gap closes.`
   * `HIGH RISK`: `HIGH RISK: TTC is 1.20 seconds. High collision risk detected. Brake firmly and increase following distance now.`
   * `COLLIDED`: `Distance is 0 m. The vehicle is already in collision with the obstacle.`

6. **Frontend Views**:

   * `Predict`: accepts `distance` and `relative_velocity`, then shows status, TTC, and message
   * `History`: displays recent prediction rows from the database
   * `Statistics`: displays a pie chart for status distribution and a bar chart for class counts

---

## Notes

* **Frontend** makes requests to the backend at `http://localhost:8000`.
* **Prediction history** is stored in the **SQLite database** (`predictions.db`).
* The frontend statistics view uses the same stored history data and normalizes valid status labels for charting.
* Runtime inference uses a fixed `backend/model.pkl`; model training is not part of this repository workflow.
* CI is defined in `.github/workflows/ci.yml` and runs backend syntax/import checks plus frontend build/test checks.
* **Scalable Deployment**: This project can be deployed to cloud platforms like AWS, Heroku, or DigitalOcean for production use.

---

## Future Enhancements

* Add automated tests for the API and prediction flow.
* Improve error handling for API inputs.
* Implement deployment to cloud for public access.
* Enhance frontend UI for better user experience.
