def run_calc():
    # Import initial libraries
    import pandas as pd
    import numpy as np
    import datetime
    import matplotlib.pyplot as plt
    import yfinance as yf

    from plotly import __version__
    from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

    import plotly.graph_objs as go

    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.styles import numbers

    print(__version__) # requires version >= 1.9.0

    init_notebook_mode(connected=True)

    filepath = "./data.xlsx"

    # Load the entire Excel file
    xls = pd.ExcelFile(filepath)

    # Load all sheet names
    sheet_names = xls.sheet_names

    # Load all sheets into a dictionary of DataFrames
    dfs = {sheet: pd.read_excel(xls, sheet) for sheet in sheet_names}

    # Convert all numerical columns to float
    for df_name in dfs:
        for col in dfs[df_name].select_dtypes(include=[np.number]).columns:
            dfs[df_name][col] = dfs[df_name][col].astype(float)

    # Convert the 'Transaction Date' column to datetime format (only year, month, day) in the 'transactions' DataFrame
    dfs['Transactions']['Transaction Date'] = pd.to_datetime(dfs['Transactions']['Transaction Date']).dt.date

    # Update the 'Transaction Total' column in the 'Transactions' DataFrame
    dfs['Transactions']['Transaction Total'] = dfs['Transactions']['Shares'] * dfs['Transactions']['Cost Per Share']

    # Sort the 'Transactions' DataFrame by date
    dfs['Transactions'] = dfs['Transactions'].sort_values('Transaction Date')

    # Get unique tickers from the 'Summary' sheet
    tickers = dfs['Summary']['Ticker'].unique().tolist()  # Convert numpy array to list

    # Add new tickers to the 'Summary' DataFrame
    unique_tickers_in_transactions = dfs['Transactions']['Ticker'].unique()
    for ticker in unique_tickers_in_transactions:
        if ticker not in dfs['Summary']['Ticker'].values:
            new_row = {'Ticker': ticker, 'Quantity': 0, 'Price Today': 0, 'Current Value': 0, 'Cost Basis': 0, 'Realized Sales': 0, 'Realized Profit': 0, 'Unrealized Profit': 0}
            dfs['Summary'] = dfs['Summary']._append(new_row, ignore_index=True)

    # Update the list of unique tickers
    tickers = dfs['Summary']['Ticker'].unique().tolist()  # Convert numpy array to list

    # Initialize a DataFrame to hold the cost basis for each buy transaction
    cost_basis_df = pd.DataFrame(columns=['Ticker', 'Shares', 'Transaction Total'])

    # Initialize 'Cost Basis' column in the 'Summary' DataFrame
    dfs['Summary']['Cost Basis'] = 0

    # Initialize a Series to hold the profit for each ticker
    profit_series = pd.Series(dtype='float64')

    # Convert 'Cost Basis', 'Realized Profit' and 'Unrealized Profit' to float
    for column in ['Cost Basis', 'Realized Profit', 'Unrealized Profit']:
        dfs['Summary'][column] = dfs['Summary'][column].astype(float)

    # Initialize a DataFrame to hold the profit for each sell transaction
    profit_df = pd.DataFrame(columns=['Ticker', 'Profit'])

    # Initialize a DataFrame to hold the sales for each sell transaction
    sales_df = pd.DataFrame(columns=['Ticker', 'Sales'])

    for idx, row in dfs['Transactions'].iterrows():
        if row['Type'] == 'Buy':
            # Calculate cost per share for the buy transaction
            cost_per_share = row['Transaction Total'] / row['Shares']
            # Add the shares and cost per share to the cost basis DataFrame
            cost_basis_df = cost_basis_df._append({'Ticker': row['Ticker'], 'Shares': row['Shares'], 'Cost Per Share': cost_per_share}, ignore_index=True)
        elif row['Type'] == 'Sell':
            # Subtract the shares from the cost basis DataFrame in the order they were added (FIFO)
            sell_shares = row['Shares']
            sell_ticker = row['Ticker']
            sell_price = row['Cost Per Share']  # Use the sell price from the transaction
            profit = 0
            sales_df = sales_df._append({'Ticker': sell_ticker, 'Sales': sell_shares * sell_price}, ignore_index=True)
            for i, cost_row in cost_basis_df[cost_basis_df['Ticker'] == sell_ticker].iterrows():
                if sell_shares <= 0:
                    break
                shares_to_sell = min(sell_shares, cost_row['Shares'])
                cost_per_share = cost_row['Cost Per Share']  # Use the cost per share from the buy transaction
                profit += shares_to_sell * (sell_price - cost_per_share)
                sell_shares -= shares_to_sell
                cost_basis_df.loc[i, 'Shares'] -= shares_to_sell
            # Remove rows with zero shares from the cost basis DataFrame
            cost_basis_df = cost_basis_df[cost_basis_df['Shares'] > 0]
            profit_df = profit_df._append({'Ticker': sell_ticker, 'Profit': profit}, ignore_index=True)

    # Initialize a dictionary to store the cost basis for each ticker
    cost_basis_dict = {}

    for idx, row in dfs['Transactions'].iterrows():
        ticker = row['Ticker']
        if row['Type'] == 'Buy':
            cost_per_share = row['Transaction Total'] / row['Shares']
            # Add the total cost of the bought shares to the cost basis for this ticker
            cost_basis_dict[ticker] = cost_basis_dict.get(ticker, 0) + row['Transaction Total']
            cost_basis_df = cost_basis_df._append({'Ticker': ticker, 'Shares': row['Shares'], 'Cost Per Share': cost_per_share, 'Transaction Total': row['Transaction Total']}, ignore_index=True)
        elif row['Type'] == 'Sell':
            sell_shares = row['Shares']
            for i, cost_row in cost_basis_df[cost_basis_df['Ticker'] == ticker].iterrows():
                if sell_shares <= 0:
                    break
                shares_to_sell = min(sell_shares, cost_row['Shares'])
                sell_shares -= shares_to_sell
                cost_basis_df.loc[i, 'Shares'] -= shares_to_sell
                # Subtract the cost of the sold shares from the cost basis for this ticker
                cost_basis_dict[ticker] -= shares_to_sell * cost_row['Cost Per Share']

    # Remove rows with 0 shares after all transactions are processed
    cost_basis_df = cost_basis_df[cost_basis_df['Shares'] > 0]

    for ticker in dfs['Summary']['Ticker'].unique():
        # Use the cost basis from the dictionary instead of summing the 'Transaction Total' column
        dfs['Summary'].loc[dfs['Summary']['Ticker'] == ticker, 'Cost Basis'] = cost_basis_dict.get(ticker, 0)

    # Calculate the total sales for each ticker
    sales_series = sales_df.groupby('Ticker')['Sales'].sum()

    # Update the 'Realized Sales' column in the 'Summary' DataFrame
    for ticker, sales in sales_series.items():
        dfs['Summary'].loc[dfs['Summary']['Ticker'] == ticker, 'Realized Sales'] = sales

    # Calculate the total realized profit for each ticker
    profit_series = profit_df.groupby('Ticker')['Profit'].sum()

    # Update the 'Realized Profit' column in the 'Summary' DataFrame
    for ticker, profit in profit_series.items():
        dfs['Summary'].loc[dfs['Summary']['Ticker'] == ticker, 'Realized Profit'] = profit

    # Round 'Cost Basis', 'Realized Profit' and 'Unrealized Profit' to 2 decimal places
    for column in ['Cost Basis', 'Realized Profit', 'Unrealized Profit']:
        dfs['Summary'][column] = dfs['Summary'][column].round(2)

    # Fetch today's data for all tickers
    data = yf.download(tickers, period='1d')

    # Convert 'Adj Close' DataFrame to a Series
    adj_close_series = data['Adj Close'].squeeze()

    # Update the 'Price Today' column in the 'Summary' DataFrame
    dfs['Summary']['Price Today'] = dfs['Summary']['Ticker'].map(adj_close_series).round(2)

    # Update the 'Current Value' column in the 'Summary' DataFrame
    dfs['Summary']['Current Value'] = dfs['Summary']['Quantity'] * dfs['Summary']['Price Today']

    # Calculate the total quantity for each ticker
    quantity_series = dfs['Transactions'].groupby(['Ticker', 'Type'])['Shares'].sum().unstack().fillna(0)
    quantity_series['Total'] = quantity_series['Buy'] - quantity_series['Sell']

    # Update the 'Quantity' column in the 'Summary' DataFrame
    dfs['Summary'] = dfs['Summary'].set_index('Ticker')
    dfs['Summary']['Quantity'] = quantity_series['Total']


    # Set pandas display options
    pd.options.display.float_format = "{:.2f}".format

    # Calculate 'Unrealized Profit' for each ticker
    dfs['Summary']['Unrealized Profit'] = np.where(dfs['Summary']['Quantity'] == 0, 0, (dfs['Summary']['Current Value'] - dfs['Summary']['Cost Basis']).round(2))

    dfs['Summary'] = dfs['Summary'].reset_index()

    # Display the DataFrame
    print(dfs['Summary'])

    # After all calculations, replace all null values with 0 and round all numerical columns to 2 decimal places
    for df_name in dfs:
        dfs[df_name] = dfs[df_name].fillna(0).round(2)

    # When writing to Excel, ensure all numerical values are formatted to 2 decimal places
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
            # Get the openpyxl worksheet
            ws = writer.sheets[sheet]
            for row in ws.iter_rows():
                for cell in row:
                    if isinstance(cell.value, float):
                        cell.number_format = numbers.FORMAT_NUMBER_00

        # Get unique "Individual" values from the "Investor" sheet
        individuals = dfs['Investors']['Individual'].unique().tolist()

        # For each "Individual", filter the "Transactions" DataFrame and perform the same calculations as in the "Summary" sheet
        for individual in individuals:
            transactions = dfs['Transactions'][dfs['Transactions']['Investor'] == individual]
            summary = dfs['Summary'][dfs['Summary']['Ticker'].isin(transactions['Ticker'].unique())].copy()

            # Replace all null values with 0 and round all numerical columns to 2 decimal places
            summary = summary.fillna(0).round(2)

            # Write the resulting DataFrame to the corresponding sheet
            summary.to_excel(writer, sheet_name=str(individual), index=False)
            # Get the openpyxl worksheet
            ws = writer.sheets[str(individual)]
            for row in ws.iter_rows():
                for cell in row:
                    if isinstance(cell.value, float):
                        cell.number_format = numbers.FORMAT_NUMBER_00