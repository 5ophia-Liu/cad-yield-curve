from datetime import datetime
import QuantLib as ql
import pandas as pd
from app.bootstrap import build_curve, curve_to_dict
from app.boc_client import extract_yield_dataframe, fetch_benchmark_yields
from fastapi import FastAPI, HTTPException
import traceback

# global variables
calendar = ql.Canada() # Canadian calendar for business day adjustments
daycount_convention = ql.Actual365Fixed() # daycount convention for accrual
year_range = 30
SERIES_MAP = {
    2: "BD.CDN.2YR.DQ.YLD",
    3: "BD.CDN.3YR.DQ.YLD",
    5: "BD.CDN.5YR.DQ.YLD",
    7: "BD.CDN.7YR.DQ.YLD",
    10: "BD.CDN.10YR.DQ.YLD",
    30: "BD.CDN.LONG.DQ.YLD",
    }

app = FastAPI(title="CAD Yield Curve API")

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
            # get the yields dictionary for each row.
            yield_columns = list(SERIES_MAP.values())
            yield_dict = row[yield_columns].to_dict()
            date_string = row["date"]
            curve_object = build_curve(yield_dict, date_string, calendar, daycount_convention)
            curve_dict = curve_to_dict(curve_object, calendar, date_string, daycount_convention, year_range)
            return curve_dict

        # add column with curve dict for each row
        yield_df['curve'] = yield_df.apply(make_curve, axis=1)
        print(yield_df[['date', 'curve']].head())
        return {"status": "ok", "message": f"curve from start date+2: {start_date}, to end date: {end_date} extracted."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
