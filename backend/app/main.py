from datetime import datetime
import QuantLib as ql
import pandas as pd
from app.bootstrap import build_curve, curve_to_list, make_maturities_list
from app.boc_client import extract_yield_dataframe, fetch_benchmark_yields, SERIES_MAP
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import traceback

# global variables
calendar = ql.Canada() # Canadian calendar for business day adjustments
daycount_convention = ql.Actual365Fixed() # daycount convention for accrual
year_range = 30

app = FastAPI(title="CAD Yield Curve API")

# middleware change ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "CAD Yield Curve API is running"}

def get_data(start_date: str, end_date: str):
    try: 
        # convert start_date and end_date to pd.Timestamp
        start_date = pd.to_datetime(start_date, format="%Y-%m-%d")
        end_date = pd.to_datetime(end_date, format="%Y-%m-%d")
        yields = fetch_benchmark_yields(start_date, end_date)
        yields_df = extract_yield_dataframe(yields)
        #* this extracts from date +2 to end date for some reason
        return yields_df
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/yields")
def run(get_data, start_date: str, end_date: str):
    try:
        get_data(start_date, end_date)
        return {"status": "ok", "message": f"yields from start date+2: {start_date}, to end date: {end_date} extracted."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/curve")
def run(start_date: str, end_date: str):
    yield_df = get_data(start_date, end_date)
    try: 

        # make curve 
        def make_curve(row):
            # get the yields list for each row.
            yield_columns = list(SERIES_MAP.values())
            yield_dict = row[yield_columns].to_dict()
            date_string = row["date"]
            curve_object = build_curve(yield_dict, date_string, calendar, daycount_convention)
            curve_dict = curve_to_list(curve_object, calendar, date_string, daycount_convention, year_range)
            return curve_dict

        # add column with curve list for each row
        yield_df['curve'] = yield_df.apply(make_curve, axis=1)
        maturities = make_maturities_list(year_range)
        dates = yield_df['date'].dt.strftime('%Y-%m-%d').tolist()
        curves = yield_df['curve'].tolist()
        return {"maturities": maturities, "dates": dates, "curves": curves}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
