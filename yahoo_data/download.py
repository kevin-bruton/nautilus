
#%%
import yfinance as yf

#%%
# Download
ticker = 'AMZN'
start='2000-01-01'
end='2005-01-01'
df = yf.download(tickers=[ticker], period='1y', interval='1d', start=start, end=end)

# %%
# Save to parquet
df.to_parquet('data/yahoo_data.parquet', engine="pyarrow", compression="snappy")

# %%
# Save to CSV
df.to_csv(f'../data/{ticker}_{start}-{end}.csv')

# %%
