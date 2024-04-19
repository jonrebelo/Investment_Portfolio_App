# Import initial libraries

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import yfinance as yf


from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

import plotly.graph_objs as go

print(__version__) # requires version >= 1.9.0

init_notebook_mode(connected=True)

filepath = "./New Sheet.xlsx"
print("filepath: ", filepath)
# Load the entire Excel file
xls = pd.ExcelFile(filepath)

# Load all sheet names
sheet_names = xls.sheet_names
print("sheet_names: ", sheet_names)
# Load all sheets into a dictionary of DataFrames
dfs = {sheet: pd.read_excel(xls, sheet) for sheet in sheet_names}

# Convert the 'Transaction Date' column to datetime format (only year, month, day) in the 'transactions' DataFrame
dfs['Transactions']['Transaction Date'] = pd.to_datetime(dfs['Transactions']['Transaction Date']).dt.date

# Get unique tickers from the 'Summary' sheet
tickers = dfs['Summary']['Ticker'].unique().tolist()  # Convert numpy array to list

# Fetch today's data for all tickers
data = yf.download(tickers, period='1d')

# Convert 'Adj Close' DataFrame to a Series
adj_close_series = data['Adj Close'].squeeze()

# Update the 'Price Today' column in the 'Summary' DataFrame
dfs['Summary']['Price Today'] = dfs['Summary']['Ticker'].map(adj_close_series).round(2)

# Update the 'Current Value' column in the 'Summary' DataFrame
dfs['Summary']['Current Value'] = dfs['Summary']['Quantity'] * dfs['Summary']['Price Today'].round(3)

# Update the 'Transaction Total' column in the 'Transactions' DataFrame
dfs['Transactions']['Transaction Total'] = dfs['Transactions']['Shares'] * dfs['Transactions']['Cost Per Share']

# Copy the 'Ticker' column from the 'Transactions' DataFrame to the 'Summary' DataFrame
dfs['Summary']['Ticker'] = dfs['Transactions']['Ticker']

# Calculate the total quantity for each ticker
quantity_series = dfs['Transactions'].groupby(['Ticker', 'Type'])['Shares'].sum().unstack().fillna(0)
quantity_series['Total'] = quantity_series['Buy'] - quantity_series['Sell']

# Update the 'Quantity' column in the 'Summary' DataFrame
dfs['Summary'] = dfs['Summary'].set_index('Ticker')
dfs['Summary']['Quantity'] = quantity_series['Total']
dfs['Summary'] = dfs['Summary'].reset_index()

# Calculate the total realized sales for each ticker
realized_sales_series = dfs['Transactions'][dfs['Transactions']['Type'] == 'Sell'].groupby('Ticker')['Transaction Total'].sum()

# Update the 'Realized Sales' column in the 'Summary' DataFrame
dfs['Summary'] = dfs['Summary'].set_index('Ticker')
dfs['Summary']['Realized Sales'] = realized_sales_series
dfs['Summary'] = dfs['Summary'].reset_index()

# Sort the 'Transactions' DataFrame by date
dfs['Transactions'] = dfs['Transactions'].sort_values('Transaction Date')

cost_basis_df = pd.DataFrame(columns=['Ticker', 'Shares', 'Transaction Total'])

# Initialize a Series to hold the profit for each ticker
profit_series = pd.Series(dtype='float64')

# Iterate over the sorted 'Transactions' DataFrame
for idx, row in dfs['Transactions'].iterrows():
    if row['Type'] == 'Buy':
        # Add the shares to the cost basis DataFrame
        cost_basis_df.loc[len(cost_basis_df)] = row[['Ticker', 'Shares', 'Transaction Total']]
    elif row['Type'] == 'Sell':
        # Subtract the shares from the cost basis DataFrame in the order they were added (FIFO)
        sell_shares = row['Shares']
        sell_ticker = row['Ticker']
        sell_price = row['Transaction Total'] / sell_shares
        profit = 0
        for i, cost_row in cost_basis_df[cost_basis_df['Ticker'] == sell_ticker].iterrows():
            if sell_shares <= 0:
                break
            shares_to_sell = min(sell_shares, cost_row['Shares'])
            profit += shares_to_sell * (sell_price - (cost_row['Transaction Total'] / cost_row['Shares']))
            sell_shares -= shares_to_sell
            cost_basis_df.loc[i, 'Shares'] -= shares_to_sell
        cost_basis_df = cost_basis_df[cost_basis_df['Shares'] > 0]
        profit_series[sell_ticker] = profit_series.get(sell_ticker, 0) + profit

# Initialize 'Cost Basis' column in the 'Summary' DataFrame
dfs['Summary']['Cost Basis'] = 0

# Convert 'Cost Basis', 'Realized Profit' and 'Unrealized Profit' to float
for column in ['Cost Basis', 'Realized Profit', 'Unrealized Profit']:
    dfs['Summary'][column] = dfs['Summary'][column].astype(float)

# Create a dictionary to hold the cost basis and shares of each ticker
cost_basis_dict = {ticker: [] for ticker in dfs['Summary']['Ticker'].unique()}

# Iterate over the 'Transactions' DataFrame
for idx, row in dfs['Transactions'].iterrows():
    if row['Type'] == 'Buy':
        # Add the transaction total and shares to the cost basis dictionary for the corresponding ticker
        cost_basis_dict[row['Ticker']].append((row['Transaction Total'], row['Shares']))
    elif row['Type'] == 'Sell':
        # Subtract the cost basis of the sold shares from the cost basis dictionary for the corresponding ticker
        sell_shares = row['Shares']
        while sell_shares > 0 and cost_basis_dict[row['Ticker']]:
            buy_total, buy_shares = cost_basis_dict[row['Ticker']][0]
            if buy_shares > sell_shares:
                cost_basis_dict[row['Ticker']][0] = (buy_total * (buy_shares - sell_shares) / buy_shares, buy_shares - sell_shares)
                sell_shares = 0
            else:
                sell_shares -= buy_shares
                cost_basis_dict[row['Ticker']].pop(0)

# Update the 'Cost Basis' column in the 'Summary' DataFrame
for ticker in dfs['Summary']['Ticker'].unique():
    dfs['Summary'].loc[dfs['Summary']['Ticker'] == ticker, 'Cost Basis'] = sum(total for total, shares in cost_basis_dict[ticker])


# Update the 'Realized Profit' column in the 'Summary' DataFrame
dfs['Summary'] = dfs['Summary'].set_index('Ticker')
dfs['Summary']['Realized Profit'] = profit_series
dfs['Summary'] = dfs['Summary'].reset_index()

# Calculate 'Unrealized Profit' for each ticker
dfs['Summary']['Unrealized Profit'] = dfs['Summary']['Current Value'] - dfs['Summary']['Cost Basis']

# Round 'Cost Basis', 'Realized Profit' and 'Unrealized Profit' to 2 decimal places
for column in ['Cost Basis', 'Realized Profit', 'Unrealized Profit']:
    dfs['Summary'][column] = dfs['Summary'][column].round(2)

# Write all DataFrames back to the Excel file
with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
    for sheet, df in dfs.items():
        df.to_excel(writer, sheet_name=sheet, index=False)


