from decimal import Decimal

import pandas as pd

from nautilus_trader.common.enums import LogColor
from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.core.data import Data
from nautilus_trader.core.message import Event
from nautilus_trader.indicators.average.ema import ExponentialMovingAverage
from nautilus_trader.model.book import OrderBook
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.data import OrderBookDeltas
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.data import TradeTick
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy

class EMACrossConfig(StrategyConfig, frozen=True):
    bar_type: BarType
    trade_size: Decimal
    fast_ema_period: PositiveInt = 10
    slow_ema_period: PositiveInt = 20
    subscribe_trade_ticks: bool = True
    subscribe_quote_ticks: bool = False
    close_positions_on_stop: bool = True

class EMACross(Strategy):
    def __init__(self, config: EMACrossConfig) -> None:
        super().__init__(config)
        self.fast_ema = ExponentialMovingAverage(config.fast_ema_period)
        self.slow_ema = ExponentialMovingAverage(config.slow_ema_period)

        self.close_positions_on_stop = config.close_positions_on_stop
        self.instrument: Instrument = None

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.bar_type.instrument_id)

        # Register the indicators for updating
        self.register_indicator_for_bars(self.config.bar_type, self.fast_ema)
        self.register_indicator_for_bars(self.config.bar_type, self.slow_ema)

        # Get historical data
        self.request_bars(self.config.bar_type, start=self._clock.utc_now() - pd.Timedelta(days=1))
        #self.request_bars()
        # self.request_quote_ticks(self.config.bar_type.instrument_id)
        # self.request_trade_ticks(self.config.bar_type.instrument_id)

        # Subscribe to live data
        self.subscribe_bars(self.config.bar_type)

        if self.config.subscribe_quote_ticks:
            self.subscribe_quote_ticks(self.config.bar_type.instrument_id)
        if self.config.subscribe_trade_ticks:
            self.subscribe_trade_ticks(self.config.bar_type.instrument_id)

        # self.subscribe_order_book_deltas(self.config.bar_type.instrument_id, depth=20)  # For debugging
        # self.subscribe_order_book_at_interval(self.config.bar_type.instrument_id, depth=20)  # For debugging

    def on_instrument(self, instrument: Instrument) -> None:
        """
        Actions to be performed when the strategy is running and receives an instrument.

        Parameters
        ----------
        instrument : Instrument
            The instrument received.

        """
        # For debugging (must add a subscription)
        # self.log.info(repr(instrument), LogColor.CYAN)

    def on_order_book_deltas(self, deltas: OrderBookDeltas) -> None:
        """
        Actions to be performed when the strategy is running and receives order book
        deltas.

        Parameters
        ----------
        deltas : OrderBookDeltas
            The order book deltas received.

        """
        # For debugging (must add a subscription)
        # self.log.info(repr(deltas), LogColor.CYAN)

    def on_order_book(self, order_book: OrderBook) -> None:
        """
        Actions to be performed when the strategy is running and receives an order book.

        Parameters
        ----------
        order_book : OrderBook
            The order book received.

        """
        # For debugging (must add a subscription)
        # self.log.info(repr(order_book), LogColor.CYAN)

    def on_quote_tick(self, tick: QuoteTick) -> None:
        """
        Actions to be performed when the strategy is running and receives a quote tick.

        Parameters
        ----------
        tick : QuoteTick
            The tick received.

        """
        # For debugging (must add a subscription)
        self.log.info(repr(tick), LogColor.CYAN)

    def on_trade_tick(self, tick: TradeTick) -> None:
        """
        Actions to be performed when the strategy is running and receives a trade tick.

        Parameters
        ----------
        tick : TradeTick
            The tick received.

        """
        # For debugging (must add a subscription)
        self.log.info(repr(tick), LogColor.CYAN)

    def on_bar(self, bar: Bar) -> None:
        """
        Actions to be performed when the strategy is running and receives a bar.

        Parameters
        ----------
        bar : Bar
            The bar received.

        """
        self.log.info(repr(bar), LogColor.CYAN)

        # Check if indicators ready
        if not self.indicators_initialized():
            self.log.info(
                f"Waiting for indicators to warm up [{self.cache.bar_count(self.config.bar_type)}]",
                color=LogColor.BLUE,
            )
            return  # Wait for indicators to warm up...

        if bar.is_single_price():
            # Implies no market information for this bar
            return

        # BUY LOGIC
        if self.fast_ema.value >= self.slow_ema.value:
            if self.portfolio.is_flat(self.config.bar_type.instrument_id):
                self.buy()
            elif self.portfolio.is_net_short(self.config.bar_type.instrument_id):
                self.close_all_positions(self.config.bar_type.instrument_id)
                self.buy()
        # SELL LOGIC
        elif self.fast_ema.value < self.slow_ema.value:
            if self.portfolio.is_flat(self.config.bar_type.instrument_id):
                self.sell()
            elif self.portfolio.is_net_long(self.config.bar_type.instrument_id):
                self.close_all_positions(self.config.bar_type.instrument_id)
                self.sell()

    def buy(self) -> None:
        """
        Users simple buy method (example).
        """
        order: MarketOrder = self.order_factory.market(
            instrument_id=self.config.bar_type.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.config.trade_size),
            # time_in_force=TimeInForce.FOK,
        )

        self.submit_order(order)

    def sell(self) -> None:
        """
        Users simple sell method (example).
        """
        order: MarketOrder = self.order_factory.market(
            instrument_id=self.config.bar_type.instrument_id,
            order_side=OrderSide.SELL,
            quantity=self.instrument.make_qty(self.config.trade_size),
            # time_in_force=TimeInForce.FOK,
        )

        self.submit_order(order)

    def on_data(self, data: Data) -> None:
        """
        Actions to be performed when the strategy is running and receives data.

        Parameters
        ----------
        data : Data
            The data received.

        """

    def on_event(self, event: Event) -> None:
        """
        Actions to be performed when the strategy is running and receives an event.

        Parameters
        ----------
        event : Event
            The event received.

        """

    def on_stop(self) -> None:
        """
        Actions to be performed when the strategy is stopped.
        """
        self.cancel_all_orders(self.config.bar_type.instrument_id)
        if self.close_positions_on_stop:
            self.close_all_positions(self.config.bar_type.instrument_id)

        # Unsubscribe from data
        self.unsubscribe_bars(self.config.bar_type)
        # self.unsubscribe_quote_ticks(self.config.bar_type.instrument_id)
        self.unsubscribe_trade_ticks(self.config.bar_type.instrument_id)
        # self.unsubscribe_order_book_deltas(self.config.bar_type.instrument_id)
        # self.unsubscribe_order_book_at_interval(self.config.bar_type.instrument_id)

    def on_reset(self) -> None:
        """
        Actions to be performed when the strategy is reset.
        """
        # Reset indicators here
        self.fast_ema.reset()
        self.slow_ema.reset()

    def on_save(self) -> dict[str, bytes]:
        """
        Actions to be performed when the strategy is saved.

        Create and return a state dictionary of values to be saved.

        Returns
        -------
        dict[str, bytes]
            The strategy state dictionary.

        """
        return {}

    def on_load(self, state: dict[str, bytes]) -> None:
        """
        Actions to be performed when the strategy is loaded.

        Saved state values will be contained in the give state dictionary.

        Parameters
        ----------
        state : dict[str, bytes]
            The strategy state dictionary.

        """

    def on_dispose(self) -> None:
        """
        Actions to be performed when the strategy is disposed.

        Cleanup any resources used by the strategy here.

        """
