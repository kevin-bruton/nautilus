#%%
from run_futures_strategy import run_strategy, get_bar_type
from futures_contracts import ES
from decimal import Decimal
from nautilus_trader.model.data import BarAggregation
from strategies.k_ema_cross import EMACross, EMACrossConfig
import pandas as pd
import plotly.express as px

instrument = ES()
data_resolution = 60
data_dimension = BarAggregation.MINUTE

bar_type = get_bar_type(instrument.id, data_resolution, data_dimension)
strategy_config = EMACrossConfig(
    bar_type=bar_type,
    trade_size=Decimal("1"),
    fast_ema_period=10,
    slow_ema_period=20
)
strategy = EMACross(config=strategy_config)
engine, strategy = run_strategy(
    parquet_filepath="./data/ES_2025_60min.parquet",
    instrument=instrument,
    bar_type=bar_type,
    strategy=strategy
)

#%%
account_report = engine.trader.generate_account_report(instrument.venue)
orders_report = engine.trader.generate_order_fills_report()
positions_report =engine.trader.generate_positions_report()
returns = strategy.portfolio.analyzer.get_performance_stats_returns()
general_stats = strategy.portfolio.analyzer.get_performance_stats_pnls()
print('\nGeneral stats:')
general_stats_df = pd.DataFrame(list(general_stats.items()), columns=['Statistic', 'Value'])
print(general_stats_df.to_string(index=False))

#%%
""" if not positions_report.empty:
  positions_report['cum_profits'] = positions_report['realized_pnl'].str.replace(' USD', '', regex=False).astype(float)
  equity = positions_report[['ts_closed', 'cum_profits']]

  fig = px.line(equity, x='ts_closed', y='cum_profits', title='Strategy Equity Curve',
              labels={'ts_closed': 'ts_closed', 'Equity': 'Cumulative Profit'})
  fig.update_layout(xaxis_title='ts_closed', yaxis_title='Cumulative Profit')
  fig.show()
else:
  print('\nNo positions to plot')
 """
# For repeated backtest runs make sure to reset the engine. Avoids having to reload the data
engine.reset()

# Once done, good practice to dispose of the object if the script continues
engine.dispose()
# %%
 