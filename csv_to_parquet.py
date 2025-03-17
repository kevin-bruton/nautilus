# %%
from pathlib import Path
from nautilus_trader.test_kit.providers import CSVBarDataLoader

instr_filename_contains = "ES_2025"
timeframe = "60min"

# %%
# Check for data files
DATA_DIR = "./data/"
path = Path(DATA_DIR).expanduser()
raw_files = list(path.iterdir())
assert raw_files, f"Unable to find any histdata files in directory {path}"
raw_files

#%%
# get file for the instrument we want to backtest
file_paths = [rf for rf in raw_files if instr_filename_contains in str(rf)]
if len(file_paths) == 0:
    raise ValueError(f"Unable to find any files for instrument {instr_filename_contains}")
else:
    file_path = file_paths[0]
# %%
# Here we just take the first data file found and load into a pandas DataFrame
# "Date","Time","Open","High","Low","Close","Up","Down"
# 01/03/2010,17:01,1366.50,1367.50,1366.00,1367.00,2566,854

# Load from TradeStation CSV file
print('Loading data...')
df = CSVBarDataLoader.load(
    file_path=file_path,                                   # Input 1st CSV file
    index_col='Date_Time',                                              # Use 1st column in data as index for dataframe
    parse_dates=[["Date", "Time"]],                                # Specify columns containing date/time
)
df['Volume'] = df['Up'] + df['Down']

# Let's make sure data are sorted by DateTime
df = df.sort_index()

#%%
df = df.resample(timeframe).agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
    "Volume": "sum"
}).dropna()
df.to_parquet(Path(f"{DATA_DIR}/{instr_filename_contains}_{timeframe}.parquet"), engine="pyarrow", compression="snappy")


# %%
