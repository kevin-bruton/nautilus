
import pandas as pd
import datetime as dt
import pytz
from nautilus_trader.model import BarType
from nautilus_trader.model.instruments import FuturesContract
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.enums import AssetClass
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.enums import PriceType, AggregationSource
from nautilus_trader.model.data import BarSpecification, BarAggregation

def get_bar_type(instr: str, timeframe: int):
    instrument = {
        'ES': ES
    }[instr]()
    return BarType(
        instrument_id=instrument.id,
        bar_spec=BarSpecification(timeframe, BarAggregation.MINUTE, PriceType.LAST),
        aggregation_source=AggregationSource.EXTERNAL
    )

def get_instrument(instr: str):
    return {
        'ES': ES
    }[instr]()

def ES(expiry_year=2025, expiry_month=6):
  activation_date = first_friday_two_years_six_months_ago(expiry_year, expiry_month)
  expiration_date = third_friday_of_month(expiry_year, expiry_month)

  activation_time = pd.Timedelta(hours=21, minutes=30)
  expiration_time = pd.Timedelta(hours=14, minutes=30)
  activation_utc = pd.Timestamp(activation_date, tz=pytz.utc) + activation_time
  expiration_utc = pd.Timestamp(expiration_date, tz=pytz.utc) + expiration_time

  raw_symbol = f"ES{get_contract_month_code(expiry_month)}{expiry_year % 10}"

  return FuturesContract(
      instrument_id=InstrumentId(symbol=Symbol(raw_symbol), venue=Venue("GLBX")),
      raw_symbol=Symbol(raw_symbol),
      asset_class=AssetClass.INDEX,
      exchange="XCME",
      currency=USD,
      price_precision=2,
      price_increment=Price.from_str("0.25"),
      multiplier=Quantity.from_int(1),
      lot_size=Quantity.from_int(1),
      underlying="ES",
      activation_ns=activation_utc.value,
      expiration_ns=expiration_utc.value,
      ts_event=activation_utc.value,
      ts_init=activation_utc.value,
  )



def first_friday_two_years_six_months_ago(year: int, month: int) -> dt.date:
    target_year = year - 2
    target_month = month - 6

    # Adjust the year and month if necessary
    if target_month <= 0:
        target_year -= 1
        target_month += 12

    first_day = dt.date(target_year, target_month, 1)
    first_day_weekday = first_day.weekday()

    days_to_add = (4 - first_day_weekday + 7) % 7
    first_friday = first_day + dt.timedelta(days=days_to_add)

    return first_friday


def third_friday_of_month(year: int, month: int) -> dt.date:
    first_day = dt.date(year, month, 1)
    first_day_weekday = first_day.weekday()

    days_to_add = (4 - first_day_weekday + 7) % 7 + 14
    third_friday = first_day + dt.timedelta(days=days_to_add)

    return third_friday


def get_contract_month_code(expiry_month: int) -> str:  # noqa: C901 (too complex)
    match expiry_month:
        case 1:
            return "F"
        case 2:
            return "G"
        case 3:
            return "H"
        case 4:
            return "J"
        case 5:
            return "K"
        case 6:
            return "M"
        case 7:
            return "N"
        case 8:
            return "Q"
        case 9:
            return "U"
        case 10:
            return "V"
        case 11:
            return "X"
        case 12:
            return "Z"
        case _:
            raise ValueError(f"invalid `expiry_month`, was {expiry_month}. Use [1, 12].")
