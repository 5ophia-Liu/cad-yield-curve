# CAD Yield Curve Surface

This project generates a 3D visualisation of the Canadian government bond yield curve (ex. Jan-Dec 2025). Based on historical benchmark yields from the BOC.

## Demo

https://github.com/user-attachments/assets/8e7afe83-0007-490b-b575-5cabdb8f13b2

## Details

- **Backend** (FastAPI + QuantLib): fetches Government of Canada benchmark bond yields (2Y, 3Y, 5Y, 7Y, 10Y, 30Y) from the Bank of Canada's Valet API, then bootstraps a curve using PiecewiseLogCubicDiscount to derive zero rates across the full 0–30Y range.
- **Frontend** (React + React Three Fibre + Three.js) fetches curve data and render it as a 3D mesh (date x yield x maturity). Yield level is shown by colour (blue < red).


## Run Instructions

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend** (separate terminal)
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Then open `http://localhost:5173`.

## Tech stack

Python, FastAPI, QuantLib, pandas · React, TypeScript, Three.js, React Three Fibre, Vite

## Additional Updates in Progress
- To add date input fields instead of editing in the frontend.
- Reduction of noise in short-end maturity extrapolation.
