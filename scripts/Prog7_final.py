
# Nanddika Agarwal

# This program is to calculate Slippage for all rows in a excel file and 
# for all source excel files in a folder (for a stock)
# looping over all the files in a stock folder and making slippage files for all
# of them

import pandas as pd
import os

# Directory containing all CSV files
# source_dir = r'C:\Projects\Blockhouse\CRWV'
# source_dir = os.path.join(r'data\CRWV', 'CRWV_2025-04-03 00_00_00+00_00.csv')
#slippage_dir = os.path.join(source_dir, "slippage")
file_dir= os.path.dirname(os.path.dirname(__file__))
source_dir=os.path.join(file_dir, 'data', 'CRWV')
# source_dir= r'data\CRWV'
slippage_dir = os.path.join(source_dir, "slippage")
os.makedirs(slippage_dir, exist_ok=True)


# Loop through all CSV files in the folder
for file_name in os.listdir(source_dir):
    if file_name.endswith(".csv"):
        file_path = os.path.join(source_dir, file_name)
        df = pd.read_csv(file_path)

        def compute_spread_and_mid(bids, asks):
            if bids and asks:
                best_bid = bids[0]['price']
                best_ask = asks[0]['price']
                spread = best_ask - best_bid
                mid_price = (best_ask + best_bid) / 2
                return spread, mid_price, best_bid, best_ask
            else:
                return None, None, None, None

        def apply_alpha_action(queue, action, price, size, depth):
            if action == 'A':
                queue.insert(depth, {'price': price, 'size': int(size)})
            elif action == 'M' and depth < len(queue):
                queue[depth]['price'] = price
                queue[depth]['size'] = int(size)
            elif action == 'C' and depth < len(queue):
                queue.pop(depth)
            elif action in ['T', 'F', 'N']:
                pass
            return queue

        def get_aggressor_direction(action, side_raw):
            if action in ['T', 'F', 'A', 'M', 'C']:
                return 'BUY' if side_raw == 'B' else 'SELL' if side_raw == 'A' else None
            return None

        def calculate_slippage(aggressor, action, size, bids, asks, mid_price):
            total_cost = 0
            remaining = size
            if action == 'T':
                if aggressor == 'SELL':
                    for level in bids:
                        px, sz = level['price'], level['size']
                        exec_sz = min(sz, remaining)
                        total_cost += exec_sz * px
                        remaining -= exec_sz
                        if remaining <= 0:
                            break
                elif aggressor == 'BUY':
                    for level in asks:
                        px, sz = level['price'], level['size']
                        exec_sz = min(sz, remaining)
                        total_cost += exec_sz * px
                        remaining -= exec_sz
                        if remaining <= 0:
                            break
                if remaining > 0:
                    return None
                return (total_cost / size) - mid_price
            elif action in ['A', 'M']:
                if aggressor == 'BUY' and bids:
                    return bids[0]['price'] - mid_price
                elif aggressor == 'SELL' and asks:
                    return asks[0]['price'] - mid_price
            return None

        # Slippage log
        slippage_log = []

        for idx, row in df.iterrows():
            bid_ask_data = row.iloc[13:73]
            bids, asks = [], []

            columns = bid_ask_data.index.tolist()
            values = bid_ask_data.values

            for i, col in enumerate(columns):
                if 'bid_px' in col and pd.notna(values[i]):
                    price = values[i]
                    size = values[i + 1] if pd.notna(values[i + 1]) else 0
                    bids.append({'price': price, 'size': int(size)})
                elif 'ask_px' in col and pd.notna(values[i]):
                    price = values[i]
                    size = values[i + 1] if pd.notna(values[i + 1]) else 0
                    asks.append({'price': price, 'size': int(size)})

            bids = sorted(bids, key=lambda x: -x['price'])
            asks = sorted(asks, key=lambda x: x['price'])

            action = str(row['action']).strip().upper()
            side_raw = row['side']
            price = row['price']
            size = row['size']
            depth = int(row['depth']) if pd.notna(row['depth']) else 0
            ts_event = row['ts_event'] if 'ts_event' in row else None

            aggressor = get_aggressor_direction(action, side_raw)

            if action == 'R':
                bids.clear()
                asks.clear()
            elif aggressor == 'BUY':
                bids = apply_alpha_action(bids, action, price, size, depth)
            elif aggressor == 'SELL':
                asks = apply_alpha_action(asks, action, price, size, depth)

            spread, mid_price, best_bid, best_ask = compute_spread_and_mid(bids, asks)
            slippage = calculate_slippage(aggressor, action, size, bids, asks, mid_price)

            slippage_log.append({
                'row': idx,
                'ts_event': ts_event,
                'action': action,
                'side': side_raw,
                'depth': depth,
                'price': price,
                'size': size,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'mid_price': mid_price,
                'spread': spread,
                'slippage': slippage
            })

        # Save file
        print("a")
        slippage_df = pd.DataFrame(slippage_log)
        base_name = os.path.splitext(file_name)[0]
        output_file = os.path.join(slippage_dir, base_name + "_slippage.csv")
        slippage_df.to_csv(output_file, index=False)
        print(f"Slippage file created: {output_file}")
