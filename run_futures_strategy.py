# %%
import pandas as pd
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from enum import Enum
import plotly.express as px

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.data import BarSpecification, BarAggregation
#from nautilus_trader.core import BarSpecification, BarAggregation, PriceType
#from nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithm
#from nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAP
#from nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAPConfig
from strategies.k_ema_cross import EMACross, EMACrossConfig
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model import BarType, InstrumentId, Money, TraderId
from nautilus_trader.model import Venue
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType, PriceType, OmsType, AggregationSource
from nautilus_trader.model.instruments import FuturesContract
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.test_kit.providers import TestDataProvider
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.test_kit.providers import CSVBarDataLoader

from futures_contracts import get_instrument, get_bar_type

class RunType(Enum):
    BACKTEST = 1
    LIVETRADING = 2

def backtest(strat: Strategy, strategy_config: StrategyConfig, parquet_filepath: str, instrument_str: str, timeframe: int, trade_size: float, **strategy_params):
    instrument = get_instrument(instrument_str)
    bar_type = get_bar_type(instrument.id, timeframe, BarAggregation.MINUTE)
    strategy = strat(config=strategy_config(bar_type=bar_type, trade_size=Decimal(trade_size), **strategy_params))
    engine, strategy = run_strategy(
            parquet_filepath=parquet_filepath,
            instrument=instrument,
            bar_type=bar_type,
            strategy=strategy,
            run_type=RunType.BACKTEST
        )
    
    # account_report = engine.trader.generate_account_report(instrument.venue)
    # orders_report = engine.trader.generate_order_fills_report()
    positions_report =engine.trader.generate_positions_report()
    returns = strategy.portfolio.analyzer.get_performance_stats_returns()
    general_stats = strategy.portfolio.analyzer.get_performance_stats_pnls()
    # print('\nGeneral stats:')
    # general_stats_df = pd.DataFrame(list(general_stats.items()), columns=['Statistic', 'Value'])
    # print(general_stats_df.to_string(index=False))


    # For repeated backtest runs make sure to reset the engine. Avoids having to reload the data
    engine.reset()

    # Once done, good practice to dispose of the object if the script continues
    engine.dispose()

    performance = {
        'avg_trade': returns['Average (Return)'],
        'sharpe_ratio': returns['Sharpe Ratio (252 days)'],
        'sortino_ratio': returns['Sortino Ratio (252 days)'],
        'profit_factor': returns['Profit Factor'],
        'risk_return_ratio': returns['Risk Return Ratio'],
        'profit': general_stats['PnL (total)'],
        'profit_pct': general_stats['PnL% (total)'],
        'expectancy': general_stats['Expectancy'],
        'win_rate': general_stats['Win Rate'],
    }
    return positions_report, performance

def plot_equity_curve(positions_report: pd.DataFrame):
    if not positions_report.empty:
        positions_report['cum_profits'] = positions_report['realized_pnl'].str.replace(' USD', '', regex=False).astype(float)
        equity = positions_report[['ts_closed', 'cum_profits']]

        fig = px.line(equity, x='ts_closed', y='cum_profits', title='Strategy Equity Curve',
                    labels={'ts_closed': 'ts_closed', 'Equity': 'Cumulative Profit'})
        fig.update_layout(xaxis_title='ts_closed', yaxis_title='Cumulative Profit')
        fig.show()
    else:
        print('\nNo positions to plot')

def get_bar_type(instrument_id: InstrumentId, resolution: int, aggregation: BarAggregation):
    return BarType(
        instrument_id=instrument_id,
        bar_spec=BarSpecification(resolution, aggregation, PriceType.LAST),
        aggregation_source=AggregationSource.EXTERNAL
    )

def run_strategy(
        parquet_filepath: str,
        instrument: FuturesContract,
        bar_type: BarType,
        strategy: Strategy,
        run_type: RunType = RunType.BACKTEST
    ):
    print('Loading data...')
    df = pd.read_parquet(parquet_filepath, engine="pyarrow")
    wrangler = BarDataWrangler(instrument=instrument, bar_type=bar_type)
    bars = wrangler.process(df)

    print('Configuring run engine...')
    if run_type == RunType.BACKTEST:
        config = BacktestEngineConfig(
            trader_id=TraderId("BACKTESTER-001"),
            logging=LoggingConfig(
                log_level="ERROR",       # Only ERROR-level (and above) messages go to the console
                log_level_file="ERROR",  # (Optional) You can still record detailed logs in files
                log_colors=True,         # Optionally disable ANSI colors if needed
                log_directory='./logs'
            )       
        )
        engine = BacktestEngine(config=config)
        engine.add_venue(
            venue=instrument.venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.MARGIN,
            base_currency=USD,
            starting_balances=[Money(1_000_000.0, USD)],
        )
    else:
        raise NotImplementedError("Live trading not yet implemented")
    
    engine.add_instrument(instrument)
    engine.add_data(bars)
    engine.add_strategy(strategy=strategy)

    print('Running...')
    engine.run()
    print('Done!')

    return engine, strategy
# %%
