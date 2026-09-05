import QuantLib as ql
import pandas as pd
from app.boc_client import SERIES_MAP

SERIES_MAP_INV = {k: v for v, k in SERIES_MAP.items()}

#construct single ql object curve given yields, start_date, calendar, daycount_convention
def build_curve(yields: dict, start_date: pd.Timestamp, calendar, daycount_convention):
    # starting day, month, year ql conversion
    ql_start_date = ql.Date(start_date.day, start_date.month, start_date.year)
    ql.Settings.instance().evaluationDate = ql_start_date # set as evaluate from date   

    bond_helpers = []
    for maturity, yield_percent in yields.items():
        year_key = SERIES_MAP_INV.get(maturity);
        # business day adjustment
        end_date = calendar.advance(ql_start_date, ql.Period(year_key, ql.Years))
        # coupon schedule
        schedule = ql.Schedule(
            ql_start_date,
            end_date,
            ql.Period(ql.Semiannual),
            calendar,
            ql.Unadjusted,
            ql.Unadjusted,
            ql.DateGeneration.Backward,
            False,
        )

        #dummy variables
        settlement_days = 1
        coupon_rate = yield_percent / 100 # make observed yield rate coupon rate
        clean_price = ql.QuoteHandle(ql.SimpleQuote(100.0))
        face_value = 100.0 # set face = clean price to 100 so yield will equal coupon rate
        # data on bond for given end_date and yield
        helper = ql.FixedRateBondHelper(
            clean_price,
            settlement_days,
            face_value,
            schedule,
            [coupon_rate],
             daycount_convention,
        )
        bond_helpers.append(helper) #add to bond helpers list

    # use helpers to produce a discount curve
    curve = ql.PiecewiseLogCubicDiscount(ql_start_date, bond_helpers, daycount_convention)
    curve.enableExtrapolation() # return curve object with spot rates for any date
    return curve

# generate list of maturities from 0 to year_range
def make_maturities_list(year_range: int = 30) -> list:
    maturities = list(range(0, year_range + 1))
    return maturities

# helper to convert curve object to list for each year in range 0 to year_range
def curve_to_list(curve, calendar, start_date: pd.Timestamp, daycount_convention, year_range: int = 30) -> list:
    ql_start_date = ql.Date(start_date.day, start_date.month, start_date.year)
    maturities = make_maturities_list(year_range)
    curve_data = []
    for year in maturities:
        date = calendar.advance(ql_start_date, ql.Period(year, ql.Years))
        spot_rate = curve.zeroRate(date, daycount_convention, ql.Compounded, ql.Semiannual).rate()
        curve_data.append(round(spot_rate * 100, 4))
    return curve_data