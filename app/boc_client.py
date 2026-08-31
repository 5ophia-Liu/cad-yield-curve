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

def fetch_benchmark_yields(start_date, end_date):
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

def extract_yield_dataframe(response):
    lines = response.text.splitlines()
    obs_index = lines.index('"OBSERVATIONS"')
    data_lines = lines[obs_index + 1:]
    df = pd.read_csv(io.StringIO("\n".join(data_lines)))
    return df

response = fetch_benchmark_yields("2023-01-01", "2023-12-31")
df = extract_yield_dataframe(response)
print(df.head())

