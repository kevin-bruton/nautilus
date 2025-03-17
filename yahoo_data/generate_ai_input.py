#%%
import pandas as pd
from datetime import datetime, date
from building_blocks import get_buy_condition

df = pd.read_csv('../data/AMZN_2000-2025.csv', index_col='Date', converters={'Date': lambda x: datetime.strptime(x, '%m/%d/%Y').date()})
min_bars = 200
max_input_num = 57

#%%
def generate_buy_conditions(df, min_bars, max_input_num):
  result = pd.DataFrame(index=df.index)
  for i in range(max_input_num + 1):
    print(i)
    result[f'buy_condition_{i}'] = df.apply(lambda row: get_buy_condition(df.loc[:row.name], i) if df.index.get_loc(row.name) >= min_bars else None, axis=1)
  return result


#%%

df2 = generate_buy_conditions(df, min_bars, max_input_num)
df2.dropna(inplace=True)
# %%

df2.loc[date(2000,1,1):date(2005,1,1)].to_csv('../data/AMZN_2000-2005_features.csv')
df2.loc[date(2005,1,1):date(2010,1,1)].to_csv('../data/AMZN_2005-2010_features.csv')
df2.loc[date(2010,1,1):date(2015,1,1)].to_csv('../data/AMZN_2010-2015_features.csv')
df2.loc[date(2015,1,1):date(2020,1,1)].to_csv('../data/AMZN_2015-2020_features.csv')
df2.loc[date(2020,1,1):date(2025,1,1)].to_csv('../data/AMZN_2020-2025_features.csv')

# %%
df['prediction'] = df['Close'].shift(-1)
prediction = df['prediction'].loc[date(2000,10,17):]
df2['prediction'] = prediction