"""
Based on the Streamlit Handover Delays Dashboard

Created on Tue Apr 16 2024
@author: JL

"""
import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess
# import yfinance as yf

st.set_page_config(page_title='Investment Portfolio App',  layout='wide', page_icon=':ambulance:')

#this is the header
 

# t1, t2 = st.columns((0.07,1)) 
t1, t2 = st.columns((0.08,1)) 

t1.image('images/NTAI.png', width = 120)
t2.title("Networking Technology Academy Institute:")
t2.title("\n Personal Investment Portfolio Report")
t2.markdown(" **tel:** 617-123-4567 **| website:** https://www.networktechnologyacademy.org **| email:** xyz@ntai.com")

dataFile = "New Sheet.xlsx"

## Data

with st.spinner('Updating Report...'):
    
    #Metrics setting and rendering
    subprocess.call(["python", "Investment_Portfolio_App.py"])
    invstr_df = pd.read_excel(dataFile,sheet_name = 'Investors')
    invstr = st.selectbox('Choose Investor', invstr_df, help = 'Filter report to show only one investor', index = 0)
    subprocess.call(["python", "Investment_Portfolio_App.py"])
    # Current Investment Table
    cw1, cw2 = st.columns((2.7, 2.5))
    # cwdf = pd.read_excel(dataFile,sheet_name = 'All')    
    if invstr == 'All':
        cwdf = pd.read_excel(dataFile,sheet_name = 'Summary')
    elif invstr != 'All':
        print("inverstor selected is: ", invstr)         
        cwdf = pd.read_excel(dataFile,sheet_name = invstr)
    
    
    fig = go.Figure(
            data = [go.Table (columnorder = [0,1,2,3,4,5,6,7], columnwidth = [10,20,20,20,20,20,20,20],
                header = dict(
                 values = list(cwdf.columns),
                 font=dict(size=12, color = 'white'),
                 fill_color = '#264653',
                 align = 'center',
                 height=20
                 )
              , cells = dict(
                  values = [cwdf[K].tolist() for K in cwdf.columns], 
                  font=dict(size=12),
                  align = 'center',
                  fill_color='#F0F2F6',
                  height=20))]) 
        
    fig.update_layout(title_text="Summary",title_font_color = '#264653',title_x=0,margin= dict(l=0,r=10,b=10,t=30), height=480)
        
    cw1.plotly_chart(fig, use_container_width=True)

    cwdf = pd.read_excel(dataFile,sheet_name = 'Transactions')    
    if invstr == 'All':
        cwdf = cwdf
    elif invstr != 'All':
        cwdf = cwdf[cwdf['Investor']==invstr]   
    
    
    fig = go.Figure(
            data = [go.Table (columnorder = [0,1,2,3,4,5,6,7], columnwidth = [25,20,20,20,20,20,20,20],
                header = dict(
                 values = list(cwdf.columns),
                 font=dict(size=12, color = 'white'),
                 fill_color = '#264653',
                 align = 'center',
                 height=20
                 )
              , cells = dict(
                  values = [cwdf[K].tolist() for K in cwdf.columns], 
                  font=dict(size=12),
                  align = 'left',
                  fill_color='#F0F2F6',
                  height=20))]) 
        
    fig.update_layout(title_text="Transactions",title_font_color = '#264653',title_x=0,margin= dict(l=0,r=10,b=10,t=30), height=480)
        
    cw2.plotly_chart(fig, use_container_width=True)


with st.spinner('Report updated!'):
    time.sleep(1)     
    
# Assume we have a DataFrame
# df = pd.DataFrame({
#     'A': [1, 2, 3, 4, 5],
#     'B': [10, 20, 30, 40, 50]
# })

# row_number = st.number_input('Input row number', min_value=0, max_value=len(df)-1, format="%i")
# column_name = st.selectbox('Select column', df.columns)
# new_value = st.number_input('Input new value', value=df.loc[row_number, column_name])

# if st.button('Update Data'):
#     df.loc[row_number, column_name] = new_value
#     st.write(df)


# Contact Form

with st.expander("Contact us"):
    with st.form(key='contact', clear_on_submit=True):
        
        email = st.text_input('Contact Email')
        st.text_area("Query","Please fill in all the information or we may not be able to process your request")  
        
        submit_button = st.form_submit_button(label='Send Information')
        
        
        
        
        
        
        
        
        
        