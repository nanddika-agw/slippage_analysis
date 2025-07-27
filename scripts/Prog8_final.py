
# Nanddika Agarwal

# This program is to design "combined slippage csv file from all slippage file
# for a stock in a given folder

# Then from "combined slippage file" to "average slippage file" based on 
# ORDER SIZE - This file will have only 3 columns - size, avg_slippage, 
# trade_count (which is number of total trades for a stock for a perticular 
# order size)


import pandas as pd
import os



# Path to slippage folder
slippage_dir = r'data\CRWV\slippage'



# Container to hold all rows
all_data = []



# Loop through all slippage CSV files
for file_name in os.listdir(slippage_dir):
    if file_name.endswith("_slippage.csv"):
        file_path = os.path.join(slippage_dir, file_name)
        df = pd.read_csv(file_path)
        df['source_file'] = file_name  # Optional: Track source
        all_data.append(df)



# Combine all into one DataFrame
combined_df = pd.concat(all_data, ignore_index=True)



# Group by order size
grouped_by_size = dict(tuple(combined_df.groupby('size')))



# Summary
print(f"Total unique order sizes: {len(grouped_by_size)}")
print(f"Combined rows: {len(combined_df)}")



# Access data for size = 100
if 100 in grouped_by_size:
    print(grouped_by_size[100].head())



# Save combined dataframe
combined_output_path = os.path.join(slippage_dir, "all_slippage_combined.csv")
combined_df.to_csv(combined_output_path, index=False)
print(f"Combined slippage saved to {combined_output_path}")



# Average slippage per order size ---
avg_slippage_df = (
    combined_df.groupby("size", as_index=False)
    .agg({
        "slippage": ["mean", "count"]
    })
)

      
      
# Flatten column names: ('slippage', 'mean') → 'slippage_mean'
avg_slippage_df.columns = ['size', 'avg_slippage', 'trade_count']



# Sort by order size
avg_slippage_df = avg_slippage_df.sort_values("size")



# Save average slippage file
avg_output_path = os.path.join(slippage_dir, "avg_slippage_by_size.csv")
avg_slippage_df.to_csv(avg_output_path, index=False)
print(f"Average slippage per order size saved to {avg_output_path}")
