
# Nanddika Agarwal

# This program is to calculate Slippage One row in a excel file
# Also display Order Book
# Calculating Mid-Price and Spread
# All this is for one row in a excel file given as in filepath variable 



import pandas as pd
import os



# Loading the data
#file_path = r'C:\Projects\Blockhouse\CRWV\CRWV_2025-04-03 00_00_00+00_00.csv'
file_dir= os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(file_dir, r'data\CRWV', 'CRWV_2025-04-03 00_00_00+00_00.csv')
df = pd.read_csv(file_path)


#Select one row
record_index = 2
row = df.iloc[record_index]
bid_ask_data = row.iloc[13:73]  # Columns N to BU


#Designing order book
bids = []
asks = []

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

# Sort bid/ask sides orderbook, bid side will in descending order 
#and ask side will be in ascending order
bids = sorted(bids, key=lambda x: -x['price'])
asks = sorted(asks, key=lambda x: x['price'])


# Print Order book Function
def print_order_book(bids, asks, title="ORDER BOOK"):
    print(f"\n{title.center(50, '-')}")
    print(f"{'ASK (SELL)':<25} | {'BID (BUY)':>22}")
    print("-" * 50)
    max_levels = max(len(bids), len(asks))
    for i in range(max_levels):
        ask_str = ""
        bid_str = ""
        if i < len(asks):
            ask = asks[i]
            ask_str = f"{ask['size']:>5} @ ${ask['price']:.2f}"
        if i < len(bids):
            bid = bids[i]
            bid_str = f"${bid['price']:.2f} @ {bid['size']:<5}"
        print(f"{ask_str:<25} | {bid_str:>22}")
    print("-" * 50)


# Defining Action Function
def apply_alpha_action(queue, action, price, size, depth):
    if action == 'A':
        queue.insert(depth, {'price': price, 'size': int(size)})
    elif action == 'M':
        if depth < len(queue):
            queue[depth]['price'] = price
            queue[depth]['size'] = int(size)
    elif action == 'C':
        if depth < len(queue):
            queue.pop(depth)
    elif action == 'R':
        pass
    elif action == 'T':
        print("\n[Trade occurred] (no book update)")
    elif action == 'F':
        print("\n[Order filled] (no book update)")
    elif action == 'N':
        print("\n[No action taken]")
    return queue



# Determine aggressing order (market order) direction
def get_aggressor_direction(action, side_raw):
    if action == 'T':
        return 'BUY' if side_raw == 'B' else 'SELL' if side_raw == 'A' else None
    elif action in ['A', 'M', 'C', 'F']:
        return 'BUY' if side_raw == 'B' else 'SELL' if side_raw == 'A' else None
    return None



# Reading action, side, depth, price and size values from excel for one row
action = str(row['action']).strip().upper()
side_raw = row['side']
price = row['price']
size = row['size']
depth = int(row['depth'])



# Print order book before update
print_order_book(bids, asks, title="ORDER BOOK BEFORE ACTION")


# Executing the trade based on "Action" and "Side" condition given in 
#documentation
if action == 'R':
    print("\n[Clear Book Action: Clearing both bid and ask queues]")
    bids.clear()
    asks.clear()
else:
    aggressor = get_aggressor_direction(action, side_raw)
    if aggressor == 'BUY':
        bids = apply_alpha_action(bids, action, price, size, depth)
    elif aggressor == 'SELL':
        asks = apply_alpha_action(asks, action, price, size, depth)
    else:
        print(f"[Action '{action}' skipped: invalid side '{side_raw}']")



# Print after update
print_order_book(bids, asks, 
                 title=f"""ORDER BOOK AFTER ACTION '{action}', 
                 SIDE '{side_raw}', DEPTH '{depth}', at PRICE '{price}', 
                 SIZE '{size}'\n""")



#Compute mid price and spread of order book
def compute_spread_and_mid(bids, asks):
    if bids and asks:
        best_bid = bids[0]['price']
        best_ask = asks[0]['price']
        spread = best_ask - best_bid
        mid_price = (best_ask + best_bid) / 2
        return spread, mid_price, best_bid, best_ask
    else:
        return None, None, None, None

spread, mid_price, best_bid, best_ask = compute_spread_and_mid(bids, asks)

if spread is not None:
    print(f"\nBest Bid: ${best_bid:.2f}")
    print(f"Best Ask: ${best_ask:.2f}")
    print(f"Spread:   ${spread:.4f}")
    print(f"Mid Price: ${mid_price:.4f}")
else:
    print("\nUnable to compute spread and mid price.")



# Defining the Slippage function based on Action and Side type orders
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
            print(f"""\n[Warning] Not enough liquidity to execute market 
                  order for full {size} shares.""")
            return None
        avg_exec_price = total_cost / size
        slippage = avg_exec_price - mid_price
        return slippage

    elif action in ['A', 'M']:
        if aggressor == 'BUY' and bids:
            return bids[0]['price'] - mid_price
        elif aggressor == 'SELL' and asks:
            return asks[0]['price'] - mid_price

    return None



# Calling slippage function
aggressor = get_aggressor_direction(action, side_raw)
slippage = calculate_slippage(aggressor, action, size, bids, asks, mid_price)


# Printing Slippage for one row in the file
if slippage is not None:
    print(f"\nSlippage for action '{action}' ({aggressor}): ${slippage:.5f}")
else:
    print("\nSlippage not applicable or insufficient liquidity.")
