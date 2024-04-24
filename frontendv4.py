"""
Based on the Streamlit Handover Delays Dashboard

@author: JL
Created on Tue Apr 16 2024
Updagted on Tue Apr 23 2024

"""
import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules import backend
from st_aggrid import AgGrid

st.set_page_config(page_title='Investment Portfolio App',  layout='wide', page_icon=':dollar:')

t1, t2 = st.columns((0.08,1)) 

t1.image('images/NTAI.png', width = 120)
t2.title("Networking Technology Academy Institute:")
t2.title("\n Personal Investment Portfolio Report")
t2.markdown(" **tel:** 617-123-4567 **| website:** https://www.networktechnologyacademy.org **| email:** xyz@ntai.com")

dataFile = "data.xlsx"

column_defs = [
    {'headerName': 'Ticker', 'field': 'Ticker'},
    {'headerName': 'Price Today', 'field': 'Price Today'},
    {'headerName': 'Quantity', 'field': 'Quantity'},
    {'headerName': 'Realized Sales', 'field': 'Realized Sales'},
    {'headerName': 'Current Value', 'field': 'Current Value'},
    {'headerName': 'Cost Basis', 'field': 'Cost Basis'},
    {'headerName': 'Realized Profit', 'field': 'Realized Profit'},
    {'headerName': 'Unrealized Profit', 'field': 'Unrealized Profit'},
    {'headerName': '% Change', 'field': '% Change'}
]

transaction_column_defs = [
    {'headerName': 'Investor', 'field': 'Investor'},
    {'headerName': 'ID', 'field': 'ID'},
    {'headerName': 'Transaction Date', 'field': 'Transaction Date'},
    {'headerName': 'Ticker', 'field': 'Ticker'},
    {'headerName': 'Type', 'field': 'Type'},
    {'headerName': 'Shares', 'field': 'Shares'},
    {'headerName': 'Cost Per Share', 'field': 'Cost Per Share'}
]

with st.spinner('Updating Report...'):    
    invstr_df = pd.read_excel(dataFile,sheet_name = 'Investors')
    invstr = st.selectbox('Choose Investor', invstr_df, help = 'Filter report to show only one investor', index = 0)
    backend.run_calc() #required to update new transactions
    cw1, cw2 = st.columns((2.7, 2.5))
    if invstr == 'All':
        cwdf = pd.read_excel(dataFile,sheet_name = 'Summary')
    elif invstr != 'All':
        print("inverstor selected is: ", invstr)         
        cwdf = pd.read_excel(dataFile,sheet_name = invstr)    
    cw1.subheader("Summary")
    AgGrid(cwdf, gridOptions={
        'columnDefs': column_defs,
        'defaultColDef': {'flex': 1},
        'fit_columns_on_grid_load': False
    })

    # Create new columns for the charts
    chart1, chart2 = st.columns((2.7, 2.5))

    # Create a pie chart for the Summary table
    pie_chart = px.pie(cwdf, values='Current Value', names='Ticker', title='Portfolio Allocation')
    chart1.plotly_chart(pie_chart, use_container_width=False)

    # Reshape the DataFrame
    cwdf_melt = cwdf.melt(id_vars='Ticker', value_vars=['Current Value', 'Cost Basis'], var_name='Variable', value_name='Value')

    # Create a bar chart
    bar_chart = px.bar(cwdf_melt, x='Ticker', y='Value', color='Variable', barmode='group', title='Current Value vs Cost Basis', color_discrete_sequence=['green', 'red'])
    chart2.plotly_chart(bar_chart, use_container_width=False)

cwdf = pd.read_excel(dataFile,sheet_name = 'Transactions')    
if invstr == 'All':
    cwdf = cwdf
elif invstr != 'All':
    cwdf = cwdf[cwdf['Investor']==invstr]   

st.subheader("Transactions")
AgGrid(cwdf, gridOptions={
    'columnDefs': transaction_column_defs,
    'defaultColDef': {'flex': 1},
    'fit_columns_on_grid_load': False
})

with st.expander("Add Transaction"):
    with st.form(key='add_transaction', clear_on_submit=True):
        investor = st.text_input('Investor')
        id = st.text_input("ID")
        transaction_date = st.text_input('Transaction Date')
        ticker = st.text_input("Stock Ticker")
        type = st.selectbox("Type", ["Buy", "Sell"])
        shares = st.number_input("Quantity of Shares", value=0)
        cost_per_share = st.number_input('Cost Per Share', value=0.00)

        submit_button = st.form_submit_button(label='Add Transaction')
        if submit_button:
            xlsx = pd.read_excel(dataFile, sheet_name=None)
            new_transaction = pd.DataFrame([[investor, id, transaction_date, ticker, type, shares, cost_per_share]], columns=['Investor', 'ID', 'Transaction Date', 'Ticker', 'Type', 'Shares', 'Cost Per Share'])
            xlsx['Transactions'] = xlsx['Transactions']._append(new_transaction, ignore_index=True)

            with pd.ExcelWriter(dataFile, engine='openpyxl') as writer:
                for sheet_name, df in xlsx.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            backend.run_calc()

with st.spinner('Report updated!'):
    time.sleep(1)     

with st.expander("Contact us"):
    with st.form(key='contact', clear_on_submit=True):
        email = st.text_input('Contact Email')
        st.text_area("Query","Please fill in all the information or we may not be able to process your request")  
        submit_button = st.form_submit_button(label='Send Information')