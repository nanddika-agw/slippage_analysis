
# Nanddika Agarwal

# This program is to plot buy side and sell side graphs based on 
# x-axis = order size and y-axis = slippage for the data from combined
# slippage csv file. 


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import os 

# Load the combined slippage data
file_path= os.path.join('data', 'CRWV', 'slippage', 'all_slippage_combined.csv')
# file_path = r'data\CRWV\slippage\all_slippage_combined.csv'
df = pd.read_csv(file_path)



df = df.dropna(subset=['slippage'])


# Group by size and side
grouped = df.groupby(['size', 'side']).agg({
    'slippage': ['mean', 'count']
}).reset_index()


# Flatten multi-level column headers
grouped.columns = ['size', 'side', 'avg_slippage', 'trade_count']



# Separate BUY and SELL data
buy_df = grouped[grouped['side'] == 'B'].sort_values('size')
sell_df = grouped[grouped['side'] == 'A'].sort_values('size')



# BUY SIDE PLOT

x = buy_df['size'].values
y = buy_df['avg_slippage'].values

mask = np.isfinite(x) & np.isfinite(y)
x = x[mask]
y = y[mask]

x_smooth = np.linspace(x.min(), x.max(), 500)
spline = make_interp_spline(x, y, k=3)
y_smooth = spline(x_smooth)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x_smooth, y_smooth, color='green', label='Buy Side')
plt.scatter(x, y, color='skyblue', s=20, label='Actual Points')
plt.xlabel('Order Size')
plt.ylabel('Average Slippage($)')
plt.title('Buy Side: Average Slippage vs Order Size')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# SELL SIDE PLOT

x = sell_df['size'].values
y = sell_df['avg_slippage'].values

mask = np.isfinite(x) & np.isfinite(y)
x = x[mask]
y = y[mask]

x_smooth = np.linspace(x.min(), x.max(), 500)
spline = make_interp_spline(x, y, k=3)
y_smooth = spline(x_smooth)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x_smooth, y_smooth, color='red', label='Sell Side')
plt.scatter(x, y, color='skyblue', s=20, label='Actual Points')
plt.xlabel('Order Size')
plt.ylabel('Average Slippage($)')
plt.title('Sell Side: Average Slippage vs Order Size')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

