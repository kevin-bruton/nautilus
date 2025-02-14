#%%

import yfinance as yf

#%%
# Download
df = yf.download(tickers=['MSFT','AMZN','GOOG'], period='max', interval='1d')

# %%
# Save to parquet
df.to_parquet('data/yahoo_data.parquet', engine="pyarrow", compression="snappy")

# %%
# Save to CSV
df.to_csv('data/yahoo_data.csv')

# %%
