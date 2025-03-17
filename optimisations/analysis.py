#%%

import sys
import pandas as pd
import plotly.express as px
print("args:", sys.argv)
if len(sys.argv) > 1:
  filename = f'./reports/{sys.argv[1]}.csv'
else:
  filename = './reports/rand_long_es_60.csv'

print("Reading file:", filename)
try:
  df = pd.read_csv(filename)
except FileNotFoundError:
  print("File not found. Exiting...")
  sys.exit()

# %%
# Calculate the percentage of Net Profits greater than 0
percentage_positive_profits = (df['Net Profit'] > 0).mean() * 100

# Create bins for the Net Profit column, rounded to the nearest 10000
bin_size = 1000
bins = range(int(df['Net Profit'].min() // bin_size * bin_size), int(df['Net Profit'].max() // bin_size * bin_size) + bin_size, bin_size)
labels = [f'{i}-{i+bin_size}' for i in bins[:-1]]

# Create a new column in the dataframe for the binned Net Profit
df['Net Profit Range'] = pd.cut(df['Net Profit'], bins=bins, labels=labels, right=False)

# Plot the bar chart
fig = px.bar(
    df['Net Profit Range'].value_counts().sort_index(), 
    title=f'Net Profit Distribution of Strategies in {filename}; Percentage of Strategies with positive Net Profit: {percentage_positive_profits:.2f}%', 
    labels={'index': 'Net Profit Range', 'value': 'Number of Strategies'}
  )
fig.update_traces(showlegend=False)
# Update the bar colors to paint negative bars in red
fig.update_traces(marker_color=['red' if len(label.split('-')) >= 3 else 'blue' for label in labels])

fig.show()

# %%

print(f"The percentage of strategies with Net Profit greater than 0 is: {percentage_positive_profits}%")
# %%
