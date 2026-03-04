<<<<<<< HEAD
# Vehicle Safety Prediction

This is a full-stack project with a FastAPI backend and a React frontend.
It predicts vehicle safety level from sensor inputs and stores prediction history in SQLite.

Current status labels used in the app are:
- `SAFE`
- `RISK`
- `HIGH RISK`

## Project structure

```text
vehicle_safety/
├── backend/
│   ├── main.py
│   ├── ml.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── model.pkl
│   ├── requirements.txt
│   └── predictions.db
├── frontend/
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── index.js
│       ├── components/App.js
│       └── styles/App.css
├── data/
│   └── vehicle_dataset.csv
└── README.md
```

## Backend quick start

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend URLs:
- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## Frontend quick start

```bash
cd frontend
npm install
npm start
```

Frontend URL:
- App: `http://localhost:3000`

## How prediction works

- Backend loads `backend/model.pkl`.
- Model artifact is expected as a dict with keys:
  - `model`
  - `features` (exact feature order)
- Prediction output classes are mapped as:
  - `0 -> HIGH RISK`
  - `1 -> RISK`
  - `2 -> SAFE`

## API endpoints

- `GET /` health check
- `POST /predict` send sensor input and get prediction label + message
- `GET /history?limit=50` fetch latest predictions

## Notes

- Frontend reads backend at `http://localhost:8000` (configured in `frontend/src/components/App.js`).
- Prediction history is stored in `backend/predictions.db`.
- `backend/scaler.pkl` and `backend/train_model.py` are not required for current runtime inference.
=======
# Vehicle_Collision_Prediction
>>>>>>> 4545506fee0d71136ae73654ba9f1168b69029fb
