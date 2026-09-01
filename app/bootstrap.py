import QuantLib as ql
import pandas as pd

# test input data
calendar = ql.Canada() # Canadian calendar for business day adjustments
daycount_convention = ql.Actual365Fixed() # daycount convention for accrual
start_date = ql.Date(3, 1, 2023) # sample
yields = {2: 4.28, 3: 4.31, 5: 4.30, 7: 4.20, 10: 3.35, 30: 3.14}  # sample
year_range = 30
SERIES_MAP = {
        "BD.CDN.2YR.DQ.YLD": 2,
        "BD.CDN.3YR.DQ.YLD": 3,
        "BD.CDN.5YR.DQ.YLD": 5,
        "BD.CDN.7YR.DQ.YLD": 7,
        "BD.CDN.10YR.DQ.YLD": 10,
        "BD.CDN.LONG.DQ.YLD": 30,
        }

#construct ql object curve given yields, start_date, calendar, daycount_convention
def build_curve(yields: dict, start_date: pd.Timestamp, calendar, daycount_convention):
    # print(f'Building yield curve from in "{calendar}" using discount convention \
    # "{daycount_convention}" from "{start_date}" with yields: "{yields}')
    
    # starting day, month, year ql conversion
    ql_start_date = ql.Date(start_date.day, start_date.month, start_date.year)
    ql.Settings.instance().evaluationDate = ql_start_date # set as evaluate from date   

    bond_helpers = []

    for maturity, yield_percent in yields.items():
        year_key = SERIES_MAP.get(maturity);
        # business day adjustment
        end_date = calendar.advance(ql_start_date, ql.Period(year_key, ql.Years))
        print
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
    curve.enableExtrapolation()
    # return a dictionary of the curve data for each year
    return curve

# helper to convert df to dict by year
def curve_to_dict(curve: dict, calendar, start_date: pd.Timestamp, daycount_convention, year_range: int = 30):
    ql_start_date = ql.Date(start_date.day, start_date.month, start_date.year)
    curve_data = {}
    for year in list(range(1, year_range + 1)):
        date = calendar.advance(ql_start_date, ql.Period(year, ql.Years))
        spot_rate = curve.zeroRate(date, daycount_convention, ql.Compounded, ql.Semiannual).rate()
        curve_data[year] = round(spot_rate * 100, 4)
    return curve_data