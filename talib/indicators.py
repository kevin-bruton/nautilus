#%%
# Imports
import pandas as pd
import talib

#%%
# dict of functions by group
for group, names in talib.get_function_groups().items():
    print(group)
    for name in names:
        print(f"  {name}")

#%%
# Load data from parquet
df = pd.read_parquet('data/yahoo_data.parquet')
#df.set_index('Date', inplace=True)

# %%
# Create a new column for each ticker in the dataframe
tickers = df['Close'].columns
for ticker in tickers:
  close = df['Close'][ticker]
  sma_25 = talib.SMA(close, timeperiod=25)
  df[('SMA_25',ticker)] = sma_25
  df[('Above_SMA_25',ticker)] = close > sma_25
  df[('3_days_rising', ticker)] = close.iloc[-1] > close.iloc[-2] > close.iloc[-3]
  df[('3_days_falling', ticker)] = close.iloc[-1] < close.iloc[-2] < close.iloc[-3]

# %%
