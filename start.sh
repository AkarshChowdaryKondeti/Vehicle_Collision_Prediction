#!/bin/bash

echo "Starting FastAPI backend..."
(cd backend && uvicorn main:app --reload --port 8000) &
BACKEND_PID=$!

echo "Starting frontend..."
(cd frontend && npm start) &
FRONTEND_PID=$!

cleanup() {
  echo ""
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}


trap cleanup SIGINT

wait $BACKEND_PID $FRONTEND_PID
