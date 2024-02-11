import pandas as pd
import yfinance as yf
from datetime import datetime
from termcolor import colored
def print_colored_line(text, color = 'yellow', font_size = 100):
    colored_text = colored(text, color)
    print(f"\033[1;{30+font_size}m{colored_text}\033[0m")

file_path = 'csv/2-10.csv'

df = pd.read_csv(file_path)


count_df = df.groupby(['Symbol', 'Trans']).size().reset_index(name='Count')

buy_counts = count_df[count_df['Trans'] == 'Buy']
sell_counts = count_df[count_df['Trans'] == 'Sell']

# Merge 'Buy' and 'Sell' counts based on 'Symbol'
merged_df = pd.merge(buy_counts, sell_counts, on='Symbol', how='outer', suffixes=('_buy', '_sell'))

# Fill NaN values with 0 (for symbols with only 'Buy' or 'Sell' transactions)
merged_df = merged_df.fillna(0)

# Calculate the difference between 'Buy' and 'Sell' counts
merged_df['Difference'] = merged_df['Count_buy'] - merged_df['Count_sell']


total_sell_count = df[df['Trans'] == 'Sell']['Trans'].count()
total_buy_count = df[df['Trans'] == 'Buy']['Trans'].count()

# Print the results

print_colored_line("TOTAL TRADES \n")
print(f"\033[91mTotal 'Sell' transactions: {total_sell_count}\033[0m")
print(f"\033[92mTotal 'Buy' transactions: {total_buy_count}\033[0m")  
print("\n")

# Print the results with color formattin

print_colored_line("DIFFERENCE \n")
for index, row in merged_df.iterrows():
    difference = row['Difference']
    if abs(difference) > 2:
        if difference > 0:
            color_code = '\033[92m'  # Green
        elif difference < 0:
            color_code = '\033[91m'  # Red
        else:
            color_code = '\033[0m'  # Default (no color)

        print(f"{color_code}Stock Symbol: {row['Symbol']} - Difference: {difference}\033[0m")


filtered_df_Buy = df[df['Trans'] == 'Buy'].groupby('Symbol').size().reset_index(name='Count')
filtered_df_Buy = filtered_df_Buy[filtered_df_Buy['Count'] > 2]

# Filter and count 'sell' transactions
filtered_df_Sell = df[df['Trans'] == 'Sell'].groupby('Symbol').size().reset_index(name='Count')
filtered_df_Sell = filtered_df_Sell[filtered_df_Sell['Count'] > 2]
print("\n")
# Print the results
print_colored_line("INDIVIDUAL\n")
for index, row in filtered_df_Buy.iterrows():
    print(f"\033[92mStock Symbol: {row['Symbol']} - Count: {row['Count']} Buy\033[0m") 

for index, row in filtered_df_Sell.iterrows():
    print(f"\033[91mStock Symbol: {row['Symbol']} - Count: {row['Count']} Sell\033[0m")   

print("\n")

print_colored_line("TOTAL MAGNITUDE \n")

df['Trans Total<sup>*</sup>'] = pd.to_numeric(df['Trans Total<sup>*</sup>'], errors='coerce')

# Drop rows with NaN values in 'Trans Total<sup>*</sup>'
df = df.dropna(subset=['Trans Total<sup>*</sup>'])

# Adjust 'Trans Total<sup>*</sup>' based on the 'Trans' column
df['Trans Total<sup>*</sup>'] = df.apply(lambda row: row['Trans Total<sup>*</sup>'] if row['Trans'] == 'Buy' else -row['Trans Total<sup>*</sup>'], axis=1)

# Group by 'StockSymbol' and calculate the total for each group
stock_totals = df.groupby('Symbol')['Trans Total<sup>*</sup>'].sum().reset_index(name='Total')

# Sort the DataFrame based on the absolute values of 'Total'
stock_totals['AbsTotal'] = stock_totals['Total'].abs()
sorted_stock_totals = stock_totals.sort_values(by='AbsTotal', ascending=False)

# Print the three largest results with color formatting
for index, row in sorted_stock_totals.head(3).iterrows():
    total = row['Total']
    if total > 0:
        color_code = '\033[92m'  # Green
    elif total < 0:
        color_code = '\033[91m'  # Red
    else:
        color_code = '\033[0m'  # Default (no color)

    print(f"{color_code}Stock Symbol: {row['Symbol']} - Total: {total}\033[0m")


def get_stock_prices(symbol, start_date, end_date):
    try:
        stock_data = yf.download(symbol, start=start_date, end=end_date)
        print(stock_data)
        if stock_data.empty:
            raise Exception(f"No price data found for {symbol}, symbol may be delisted.")
        return stock_data['Adj Close']
    except Exception as e:
        raise Exception(f"Error fetching data for {symbol} on {start_date}: {e}")
    
stock_prices = get_stock_prices("APPL", '2024-02-08', pd.Timestamp.utcnow())
# def get_stock_prices(symbol, start_date, end_date):
#     stock_data = yf.download(symbol, start=start_date, end=end_date)
#     return stock_data['Adj Close']

# Calculate the gains for each buy trade
# for index, row in df[df['Trans'] == 'Buy'].iterrows():
#     symbol = row['Symbol']
#     start_date = datetime.strptime(row['Date'], '%m/%d/%Y').strftime('%Y-%m-%d')
#     end_date = start_date  # You might want to adjust the end date as needed
    
#     try:
#         stock_prices = get_stock_prices(symbol, start_date, end_date)
#         initial_price = stock_prices.iloc[0]
#         current_price = stock_prices.iloc[-1]
#         percentage_gain = ((current_price - initial_price) / initial_price) * 100
#         profit = (row['Trans Total'] * current_price) - (row['Trans Total'] * initial_price)

#         # Update the trading_df with calculated values
#         df.at[index, 'InitialInvestment'] = row['Trans Total'] * initial_price
#         df.at[index, 'CurrentInvestment'] = row['Trans Total'] * current_price
#         df.at[index, 'PercentageGain'] = percentage_gain
#         df.at[index, 'Profit'] = profit

#     except Exception as e:
#         print(f"Error fetching data for {symbol} on {start_date}: {e}")

# # Print the results
# print(df[['StockSymbol', 'Date', 'Trans Tota', 'Price', 'CurrentPrice', 'PercentageGain', 'Profit']])