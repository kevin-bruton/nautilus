#%%

import sys
import pandas as pd
import matplotlib.pyplot as plt

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
# Calculate the mean Net Profit
mean_net_profit = df['Net Profit'].mean()

# Create bins for the Net Profit column, rounded to the nearest 10000
bin_size = 1000
bins = range(int(df['Net Profit'].min() // bin_size * bin_size), int(df['Net Profit'].max() // bin_size * bin_size) + bin_size, bin_size)
labels = [f'{i}-{i+bin_size}' for i in bins[:-1]]

# Create a new column in the dataframe for the binned Net Profit
df['Net Profit Range'] = pd.cut(df['Net Profit'], bins=bins, labels=labels, right=False)

print(f"The mean Net Profit is: {mean_net_profit}")
# Plot the bar chart
net_profit_counts = df['Net Profit Range'].value_counts().sort_index()
fig, ax = plt.subplots()

bars = ax.bar(net_profit_counts.index, net_profit_counts.values, color=['red' if len(label.split('-')) >= 3 else 'blue' for label in net_profit_counts.index])

# Set the title and labels
ax.set_title(f'{filename}; Percentage of Strategies with positive Net Profit: {percentage_positive_profits:.2f}%    Mean NP: ${mean_net_profit:.2f}')
ax.set_xlabel('Net Profit Range')
ax.set_ylabel('Number of Strategies')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Show the plot
plt.tight_layout()
# Keep the plot open after the script terminates
plt.show()
# %%

print(f"The percentage of strategies with Net Profit greater than 0 is: {percentage_positive_profits}%")
# %%
