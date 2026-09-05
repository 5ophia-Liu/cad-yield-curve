import requests
import pandas as pd
import io as io

SERIES_MAP = {
    2: "BD.CDN.2YR.DQ.YLD",
    3: "BD.CDN.3YR.DQ.YLD",
    5: "BD.CDN.5YR.DQ.YLD",
    7: "BD.CDN.7YR.DQ.YLD",
    10: "BD.CDN.10YR.DQ.YLD",
    30: "BD.CDN.LONG.DQ.YLD",
}

url = "https://www.bankofcanada.ca/valet/observations"
data_format = "csv"

# get BOC data from specified start_date to end_date as csv object
def fetch_benchmark_yields(start_date: pd.Timestamp, end_date: pd.Timestamp):
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    params = {
    "start_date": start_date,
    "end_date": end_date
    }
    series_string = ",".join(SERIES_MAP.values())
    response = requests.get(
        f"{url}/{series_string}/{data_format}",
        params=params,
    )
    return response

# extract yield data from BOC response and return as pandas dataframe
def extract_yield_dataframe(response):
    lines = response.text.splitlines()
    obs_index = None
    for i, line in enumerate(lines):
        if "OBSERVATIONS" in line:
            obs_index = i
            break
    data_lines = lines[obs_index + 1:]
    df = pd.read_csv(io.StringIO("\n".join(data_lines)))
    df["date"] = pd.to_datetime(df["date"])
    return df

