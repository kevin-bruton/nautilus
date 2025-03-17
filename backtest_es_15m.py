# %%
import pandas as pd
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import plotly.express as px

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.data import BarSpecification, BarAggregation
from nautilus_trader.model.enums import PriceType
#from nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithm
#from nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAP
#from nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAPConfig
from strategies.ema_cross import EMACross, EMACrossConfig
from nautilus_trader.model import BarType
from nautilus_trader.model.enums import AggregationSource
from nautilus_trader.model import Money
from nautilus_trader.model import TraderId
from nautilus_trader.model import Venue
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.test_kit.providers import TestDataProvider
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.test_kit.providers import CSVBarDataLoader
from futures_contracts import ES

# %%
print('Loading data...')
parquet_filename = './data/ES_2025_60min.parquet'
df = pd.read_parquet(parquet_filename, engine="pyarrow")
contract_year = 2025
contract_month = 6
#ES_FUTURE = TestInstrumentProvider.es_future(contract_year, contract_month)
instrument = ES()
bar_spec = BarSpecification(60, BarAggregation.MINUTE, PriceType.LAST)
#bar_type = BarType.from_str("ESM5.GLBX-60-MINUTE-LAST-EXTERNAL")
bar_type = BarType(instrument_id=instrument.id, bar_spec=bar_spec, aggregation_source=AggregationSource.EXTERNAL)
#wrangler = BarDataWrangler(instrument=ES_FUTURE, bar_type=))
wrangler = BarDataWrangler(instrument=instrument, bar_type=bar_type)
bars = wrangler.process(df)
print('Data loaded successfully')

# %%
# Configure backtest engine
print('Configuring backtest engine...')
config = BacktestEngineConfig(
    trader_id=TraderId("BACKTESTER-001"),
    logging=LoggingConfig(
        log_level="ERROR",       # Only ERROR-level (and above) messages go to the console
        log_level_file="ERROR",  # (Optional) You can still record detailed logs in files
        log_colors=True         # Optionally disable ANSI colors if needed
    )       
)

# Build the backtest engine
engine = BacktestEngine(config=config)

# %%
# Add a trading venue (multiple venues possible)
GLOBEX = Venue("GLBX")
engine.add_venue(
    venue=GLOBEX,
    oms_type=OmsType.NETTING,
    account_type=AccountType.MARGIN,  # Spot CASH account (not for perpetuals or futures)
    base_currency=USD,  # Multi-currency account
    starting_balances=[Money(1_000_000.0, USD)],
)

#%%
# Add instrument(s)
engine.add_instrument(instrument)

# Add data
engine.add_data(bars)
# %%
# Configure your strategy

strategy_config = EMACrossConfig(
    instrument_id=instrument.id,
    #bar_type=BarType.from_str("ESM5.GLBX-60-MINUTE-LAST-EXTERNAL"),
    bar_type=BarType(instrument_id=instrument.id, bar_spec=bar_spec, aggregation_source=AggregationSource.EXTERNAL),
    trade_size=Decimal("1"),
    fast_ema_period=10,
    slow_ema_period=20
)

# Instantiate and add your strategy
strategy = EMACross(config=strategy_config)
engine.add_strategy(strategy=strategy)


# %%
# Instantiate and add your execution algorithm
#exec_algorithm = TWAPExecAlgorithm()  # Using defaults
#engine.add_exec_algorithm(exec_algorithm)

# %%
# Run the engine (from start to end of data)
print('Running backtest...')
engine.run()

# %%
account_report = engine.trader.generate_account_report(GLOBEX)
account_report

# %%
#print('\nOrder fills report:')
orders_report = engine.trader.generate_order_fills_report()

# %%
#print('\nPositions report:')
positions_report =engine.trader.generate_positions_report()
positions_report

#%%
returns = strategy.portfolio.analyzer.get_performance_stats_returns()
#print('\nPerformance stats returns:')
returns

general_stats = strategy.portfolio.analyzer.get_performance_stats_pnls()
print('\nGeneral stats:')
print(general_stats)

#%%
positions_report['cum_profits'] = positions_report['realized_pnl'].str.replace(' USD', '', regex=False).astype(float)
equity = positions_report[['ts_closed', 'cum_profits']]

#%%
fig = px.line(equity, x='ts_closed', y='cum_profits', title='Strategy Equity Curve',
              labels={'ts_closed': 'ts_closed', 'Equity': 'Cumulative Profit'})
fig.update_layout(xaxis_title='ts_closed', yaxis_title='Cumulative Profit')
fig.show()

# %%
# For repeated backtest runs make sure to reset the engine. Avoids having to reload the data
engine.reset()

# %%
# Once done, good practice to dispose of the object if the script continues
engine.dispose()


# %%
