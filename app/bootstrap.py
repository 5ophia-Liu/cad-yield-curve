import QuantLib as ql


# input data
calendar = ql.Canada() # Canadian calendar for business day adjustments
daycount_convention = ql.Actual365Fixed() # daycount convention for accrual
start_date = ql.Date(3, 1, 2023) # sample
yields = {2: 4.28, 3: 4.31, 5: 4.30, 7: 4.20, 10: 3.35, 30: 3.14}  # sample

def build_curve(yields, start_date, calendar, daycount_convention):
    print(f'Building yield curve from in "{calendar}" using discount convention \
      "{daycount_convention}" from "{start_date}" with yields: "{yields}')
    
    # starting day, month, year
    ql.Settings.instance().evaluationDate = start_date # set as evaluate from date   

    bond_helpers = []

    for maturity, yield_percent in yields.items():
        # business day adjustment
        end_date = calendar.advance(start_date, ql.Period(maturity, ql.Years))
        # coupon schedule
        schedule = ql.Schedule(
            start_date,
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
    curve = ql.PiecewiseLogCubicDiscount(start_date, bond_helpers, daycount_convention)
    curve.enableExtrapolation()

    # print out discount factors for each maturity
    for year in list(range(1, 31)):
        date = calendar.advance(start_date, ql.Period(year, ql.Years))
        spot_rate = curve.zeroRate(date, daycount_convention, ql.Compounded, ql.Semiannual).rate()
        print(f'"{date}" df: {curve.discount(date)*100:.3f}%" spot: {spot_rate * 100:.3f}%')
    
    return curve

curve = build_curve(yields, start_date, calendar, daycount_convention)