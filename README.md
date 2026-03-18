# Vehicle Safety Prediction

This project is a simple full-stack app that predicts vehicle safety using `distance` and `relative_velocity`.

It includes:
- a FastAPI backend
- a React frontend
- an SQLite database for prediction history

The app can return these statuses:
- `SAFE`
- `RISK`
- `HIGH RISK`
- `COLLIDED`

## Project Structure

```text
vehicle_safety/
├── backend/
│   ├── main.py
│   ├── ml.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── model.pkl
│   ├── predictions.db
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── index.js
│       ├── components/App.js
│       ├── components/PredictView.js
│       ├── components/HistoryView.js
│       ├── components/StatisticsView.js
│       ├── components/StatusBadge.js
│       ├── components/statusConfig.js
│       └── styles/App.css
├── data/
│   └── vehicle_dataset.csv
├── view_predictions.py
├── start.sh
└── README.md
```

## What It Does

### Backend

- Accepts input with `distance` and `relative_velocity`
- Loads the trained model from `backend/model.pkl`
- Predicts a safety status
- Applies simple safety rules for edge cases
- Saves each prediction to `backend/predictions.db`

### Frontend

The frontend has 3 views:
- `Predict` for sending inputs and seeing the result
- `History` for viewing saved predictions with filter, sort, and pagination
- `Statistics` for viewing status counts and exporting CSV

## How It Works

1. The user enters `distance` and `relative_velocity` in the frontend.
2. The frontend sends the data to `POST /predict`.
3. The backend calculates TTC and prepares model input.
4. The model predicts a safety status.
5. The backend applies simple rule checks for edge cases like very small distance or collision.
6. The final result is returned to the frontend.
7. The prediction is saved in the SQLite database.

## Workflow

```text
User Input
   |
   v
React Frontend
   |
   v
POST /predict
   |
   v
FastAPI Backend
   |
   +--> calculate TTC
   |
   +--> run model from model.pkl
   |
   +--> apply edge-case safety rules
   |
   +--> save result to predictions.db
   |
   v
Prediction Response
   |
   v
Frontend Result / History / Statistics
```

## Project Details

- Backend framework: FastAPI
- Frontend framework: React
- Database: SQLite
- ML model file: `backend/model.pkl`
- Stored history file: `backend/predictions.db`
- Main inputs: `distance`, `relative_velocity`
- Main output: `predicted_status`, `ttc`, `message`

## Uses

This project can be used for:
- basic vehicle safety prediction demos
- learning a simple full-stack ML app
- viewing saved prediction history
- checking status distribution from past records

## API Endpoints

- `GET /` - health check
- `POST /predict` - get a prediction
- `GET /history` - get saved prediction history

Example request for `POST /predict`:

```json
{
  "distance": 30,
  "relative_velocity": 5
}
```

Example response:

```json
{
  "predicted_status": "SAFE",
  "ttc": 6.0,
  "message": "SAFE: TTC is 6.00 seconds. No immediate collision risk detected. Keep a safe buffer and continue monitoring traffic."
}
```

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

## Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend:
- App: `http://localhost:3000`

## Notes

- The frontend calls the backend at `http://localhost:8000`
- Prediction history is stored in SQLite
- `view_predictions.py` can be used to inspect saved rows
- `start.sh` starts both backend and frontend together
