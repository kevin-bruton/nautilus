# %%
import pandas as pd
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithm
from nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAP
from nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAPConfig
from nautilus_trader.model import BarType
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

# %%

df = pd.read_parquet("aggregated_60min.parquet", engine="pyarrow")

# %%
# Process quotes using a wrangler


#trades_df = provider.read_csv_ticks("./data/ES_2025.01.15.txt")
#EURUSD = TestInstrumentProvider.default_fx_ccy("EUR/USD")
#wrangler = QuoteTickDataWrangler(EURUSD)
#
#ticks = wrangler.process(df)
#trades_df = provider.read_csv_ticks("./data/ES_2025.01.15.txt")

# Initialize the instrument which matches the data
ES_FUTURE = TestInstrumentProvider.es_future(2025,6)
print('es instru:', ES_FUTURE)
# ETHUSDT_BINANCE = TestInstrumentProvider.ethusdt_binance()

# Process into Nautilus objects
# wrangler = TradeTickDataWrangler(instrument=ES_FUTURES)
# ticks = wrangler.process(trades_df)
print('Data wrangling...')
wrangler = BarDataWrangler(instrument=ES_FUTURE, bar_type=BarType.from_str("ESM5.GLBX-60-MINUTE-LAST-EXTERNAL"))

bars = wrangler.process(df)

# %%
# Configure backtest engine
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
engine.add_instrument(ES_FUTURE)

# Add data
engine.add_data(bars)
# %%
# Configure your strategy
strategy_config = EMACrossTWAPConfig(
    instrument_id=ES_FUTURE.id,
    bar_type=BarType.from_str("ESM5.GLBX-60-MINUTE-LAST-EXTERNAL"),
    trade_size=Decimal("1"),
    fast_ema_period=10,
    slow_ema_period=20,
    twap_horizon_secs=10.0,
    twap_interval_secs=2.5,
)

# Instantiate and add your strategy
strategy = EMACrossTWAP(config=strategy_config)
engine.add_strategy(strategy=strategy)


# %%
# Instantiate and add your execution algorithm
exec_algorithm = TWAPExecAlgorithm()  # Using defaults
engine.add_exec_algorithm(exec_algorithm)

# %%
# Run the engine (from start to end of data)
print('Running backtest...')
engine.run()

# %%
account_report = engine.trader.generate_account_report(GLOBEX)
print('\nAccount report:')
print(account_report)

# %%
print('\nOrder fills report:')
print(engine.trader.generate_order_fills_report())

# %%
print('\nPositions report:')
print(engine.trader.generate_positions_report())


# %%
# For repeated backtest runs make sure to reset the engine. Avoids having to reload the data
engine.reset()

# %%
# Once done, good practice to dispose of the object if the script continues
engine.dispose()


# %%
