from dotenv import load_dotenv
load_dotenv() 
from pathlib import Path

from nautilus_trader.backtest.node import BacktestDataConfig
from nautilus_trader.backtest.node import BacktestEngineConfig
from nautilus_trader.backtest.node import BacktestNode
from nautilus_trader.backtest.node import BacktestRunConfig
from nautilus_trader.backtest.node import BacktestVenueConfig
from nautilus_trader.config import ImportableStrategyConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model import Quantity
from nautilus_trader.model import QuoteTick
from nautilus_trader.persistence.catalog import ParquetDataCatalog

#catalog = ParquetDataCatalog.from_env()
catalog = ParquetDataCatalog(Path.cwd() / "catalog")
print('path:', Path.cwd() / "catalog")
print(catalog.instruments())

import os
print(os.getenv("NAUTILUS_DATA_DIR"))