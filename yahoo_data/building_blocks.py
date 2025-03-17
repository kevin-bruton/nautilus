import random
from numpy import average
import pandas as pd

#df = pd.read_csv('../data/AMZN.csv')



"""
Determina si se cumple una condición de compra basada en los datos OHLCV proporcionados y el número de condición de entrada.
Parámetros:
ohlcvDataFrame (pd.DataFrame): Un DataFrame que contiene las columnas 'Open', 'High', 'Low', 'Close' y 'Volume'.
entryNum (int): El número de condición de entrada a evaluar.
Retorna:
bool: True si se cumple la condición de compra, False en caso contrario.
"""
def get_buy_condition(ohlcvDataFrame: pd.DataFrame, entryNum: int) -> bool:
  open, high, low, close, volume = (ohlcvDataFrame[col] for col in ['Open', 'High', 'Low', 'Close', 'Vol'])
  return bool({
    # No aplica ninguna condición
    0: True,
    # Tendencial: Tres día subiendo
    1: close.iloc[-1] > open.iloc[-1] and close.iloc[-2] > open.iloc[-2] and close.iloc[-3] > open.iloc[-3],
    # Tendencial: Cierre mayor a la media de los últimos X cierres
    2: close.iloc[-1] >= max(close.iloc[-5:]),
    3: close.iloc[-1] >= max(close.iloc[-10:]),
    4: close.iloc[-1] >= max(close.iloc[-20:]),
    5: close.iloc[-1] >= max(close.iloc[-50:]),
    6: close.iloc[-1] >= max(close.iloc[-100:]),
    7: close.iloc[-1] >= max(close.iloc[-150:]),
    8: close.iloc[-1] >= max(close.iloc[-200:]),
    # Reversión: Cierre menor a la media de los últimos X cierres
    9: close.iloc[-1] <= min(close.iloc[-5:]),
    10: close.iloc[-1] <= min(close.iloc[-10:]),
    11: close.iloc[-1] <= min(close.iloc[-20:]),
    12: close.iloc[-1] <= min(close.iloc[-50:]),
    13: close.iloc[-1] <= min(close.iloc[-100:]),
    # Reversión: Bajo volúmen y cierre en mínimo de los últimos X cierres
    14: volume.iloc[-1] < average(volume.iloc[-10:]) and (close.iloc[-1] < min(close.iloc[-5:])),
    15: volume.iloc[-1] < average(volume.iloc[-10:]) and (close.iloc[-1] < min(close.iloc[-10:])),
    16: volume.iloc[-1] < average(volume.iloc[-10:]) and (close.iloc[-1] < min(close.iloc[-50:])),
    17: volume.iloc[-1] < average(volume.iloc[-10:]) and (close.iloc[-1] < min(close.iloc[-100:])),
    # Tendencial: Duel momentum. Cierre mayor que el cierre de hace X días y cierre de hace X días mayor que el cierre de hace 2.5X días
    18: close.iloc[-1] > close.iloc[-5] and close.iloc[-5] > close.iloc[-10],
    19: close.iloc[-1] > close.iloc[-5] and close.iloc[-5] > close.iloc[-20],
    20: close.iloc[-1] > close.iloc[-10] and close.iloc[-10] > close.iloc[-20],
    21: close.iloc[-1] > close.iloc[-15] and close.iloc[-15] > close.iloc[-30],
    22: close.iloc[-1] > close.iloc[-20] and close.iloc[-20] > close.iloc[-50],
    # Tendencial: Cruce de medias móviles
    23: average(close.iloc[-5:]) > average(close.iloc[-10:]),
    24: average(close.iloc[-10:]) > average(close.iloc[-20:]),
    25: average(close.iloc[-15:]) > average(close.iloc[-30:]),
    26: average(close.iloc[-20:]) > average(close.iloc[-50:]),
    27: average(close.iloc[-50:]) > average(close.iloc[-200:]),
    # Reversion: Cierre cruza la media móvil a la baja
    28: close.iloc[-1] < average(close.iloc[-5:]),
    29: close.iloc[-1] < average(close.iloc[-10:]),
    30: close.iloc[-1] < average(close.iloc[-20:]),
    31: close.iloc[-1] < average(close.iloc[-30:]),
    32: close.iloc[-1] < average(close.iloc[-50:]),
    33: close.iloc[-1] < average(close.iloc[-100:]),
    34: close.iloc[-1] < average(close.iloc[-150:]),
    35: close.iloc[-1] < average(close.iloc[-200:]),
    # Tendencial: Cierre cruza la media móvil a la alza
    36: close.iloc[-1] > average(close.iloc[-5:]),
    37: close.iloc[-1] > average(close.iloc[-10:]),
    38: close.iloc[-1] > average(close.iloc[-20:]),
    39: close.iloc[-1] > average(close.iloc[-30:]),
    40: close.iloc[-1] > average(close.iloc[-50:]),
    41: close.iloc[-1] > average(close.iloc[:-100]),
    42: close.iloc[-1] > average(close.iloc[:-150]),
    43: close.iloc[-1] > average(close.iloc[-200:]),
    # Tendencial: días consecutivos subiendo
    44: close.iloc[-1] > close.iloc[-2] and close.iloc[-2] > close.iloc[-3],
    45: close.iloc[-2] > close.iloc[-3] and close.iloc[-3] > close.iloc[-4],
    46: close.iloc[-1] > close.iloc[-2] and close.iloc[-2] > close.iloc[-3] and close.iloc[-3] > close.iloc[-4],
    47: close.iloc[-2] > close.iloc[-3] and close.iloc[-3] > close.iloc[-4] and close.iloc[-4] > close.iloc[-5],
    48: close.iloc[-1] > close.iloc[-2] and close.iloc[-2] > close.iloc[-3] and close.iloc[-3] > close.iloc[-4] and close.iloc[-4] > close.iloc[-4],
    49: close.iloc[-2] > close.iloc[-3] and close.iloc[-3] > close.iloc[-4] and close.iloc[-4] > close.iloc[-5] and close.iloc[-5] > close.iloc[-6],
    # Expansión del rango
    50: (high.iloc[-1] - open.iloc[-1]) > ((high.iloc[-2] - open.iloc[-2])*1),
    51: (high.iloc[-1] - open.iloc[-1]) > ((high.iloc[-2] - open.iloc[-2])*1.5),
    52: ((open.iloc[-1] - low.iloc[-1])) > ((open.iloc[-2] - low.iloc[-2])*1),
    53: ((open.iloc[-1] - low.iloc[-1])) > ((open.iloc[-2] - low.iloc[-2])*1.5),
    # Reversión bajo de hoy más bajo que el de ayer
    54: low.iloc[-1] < low.iloc[-2],
    # Tendencial: Alto de hoy más alto que el de ayer
    55: high.iloc[-1] > high.iloc[-2],
    # Cuerpo de vela menor que el rango
    56: abs(open.iloc[-2] - close.iloc[-2]) < (high.iloc[-2] - low.iloc[-2]),
    # Cuerpo de vela mayor que el rango
    57: abs(open.iloc[-2] - close.iloc[-2]) > (high.iloc[-2] - low.iloc[-2]),
  }[entryNum])

"""
Sólo abrir posiciones en días de la semana específicos
"""
def day_of_week_range(ohlcvDataFrame: pd.DataFrame, day_start: int, day_end: int) -> bool:
  if day_start < day_end:
    return day_start <= ohlcvDataFrame.index[-1].dayofweek <= day_end
  else:
    return day_start <= ohlcvDataFrame.index[-1].dayofweek or ohlcvDataFrame.index[-1].dayofweek <= day_end

"""
Sólo abrir posiciones en días del mes específicos
"""
def month_date_range_filter(ohlcvDataFrame: pd.DataFrame, start: int, end: int) -> bool:
  if start < end:
    return start <= ohlcvDataFrame.index[-1].day <= end
  else:
    return start <= ohlcvDataFrame.index[-1].day or ohlcvDataFrame.index[-1].day <= end
  

"""
Dado un DataFrame OHLCV y dos números de condición de entrada, evalúa si se cumple la condición de compra.
"""
def entry_evaluator(ohlcvDataFrame: pd.DataFrame, cond1: int, cond2) -> bool:
  buy_condition_1 = get_buy_condition(ohlcvDataFrame, cond1)
  buy_condition_2 = get_buy_condition(ohlcvDataFrame, cond2)
  # se podría añadir aquí filtros para días de la semana o días del mes
  return buy_condition_1 and buy_condition_2

"""
Genera las condiciones de entrada y devuelve si la condiciones de compra se cumplen.
"""
def entry_generator(ohlcvDataFrame: pd.DataFrame) -> str:
  num_entries = 56
  get_rand_entry_num = lambda x: random.randint(0, x - 1)
  condition1_num = get_rand_entry_num(num_entries)
  condition2_num = get_rand_entry_num(num_entries)
  return entry_evaluator(ohlcvDataFrame, condition1_num, condition2_num)

def calc_commissions_per_order(num_stocks: int) -> float:
  min_commission = 1
  commission_rate = 0.005
  return max(min_commission, commission_rate * num_stocks)

def slippage_per_order(num_stocks: int, price: float) -> float:
  slippage_estimate = 0.0005 # = 0.05% - Esto es tirando por lo alto para acciones líquidas como las del S&P 500
  return slippage_estimate * price * num_stocks

def costs_per_order(num_stocks: int, price: float) -> float:
  return calc_commissions_per_order(num_stocks) + slippage_per_order(num_stocks, price)

def gross_profit(num_stocks: int, price: float, entry_price: float) -> float:
  return num_stocks * (price - entry_price)

def net_profit_per_trade(num_stocks: int, entry_price: float, exit_price: float, ) -> float:
  costs_entry = costs_per_order(num_stocks, entry_price)
  costs_exit = costs_per_order(num_stocks, exit_price)
  gross_profit = gross_profit(num_stocks, exit_price, entry_price)
  return gross_profit - costs_entry - costs_exit
