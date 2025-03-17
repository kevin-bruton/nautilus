#%%
from run_futures_strategy import backtest
from strategies.k_ema_cross import EMACross, EMACrossConfig

#%%
positions_report, performance = backtest(
  strat=EMACross,
  strategy_config=EMACrossConfig,
  parquet_filepath='./data/ES_2025_60min.parquet',
  instrument_str='ES',
  timeframe=60,
  trade_size=1,
  fast_ema_period=10,
  slow_ema_period=20
  )

# %%
print(performance)