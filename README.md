 
Data Science & Analytics Project Definition:

Updated: 2024.04.19

Project Name: Investment_Portfolio_App

Project and Work Product Description: 

   Capturing and maintaining Buy/Sell Stock investments (your portfolio) for the beginner.
   Keep all your Buy/Sell transactions in one manageable place.
   Pull desired/chosen Ticker symbols from yfiance RestAPI. 
   Calculate the cost basis, realized gains, and current value of each ticker in the excel file.
   Display the realized gains, unrealized gains, and cost basis of each ticker.  
     
High-level workflow Diagram:
      AS-IS <<Investment_Portfolio_App.drawio>> open at https://app.diagrams.net/?src=about#
      TO-BE <<Investment_Portfolio_App_v1.drawio>> open at https://app.diagrams.net/?src=about#

Description of Solution: 
	
     - Convert Jupyter Notebook code and markdown cells into a reusable Python program that performs Stock Portfolio (Buy/Sell) transactions.
     - Use real-time data feeds to obtain current data sets using RestAPI (yfinance).
     - Integrate the 2nd repo using streamlit framework to display and analyze the captured data sets.

     Additional requirements:
        - Enter buy/sell transaction in the "Transactions" sheet ensuring the stock ticker symbol is correct.
             note: Transaction total must be left blank (program will calculate this).
      
     
 Using two repo sources: 
    https://github.com/kdboller/pythonsp500  and  https://streamlit.io/gallery?category=finance-business  
    
    Refactor these repos to extend there current functionality as follows:
    v1:
       - Convert Jupyter Notebook code and markdown cells into a reusable Python program that performs Stock Portfolio (Buy/Sell) transactions.
       - Cse real-time data feeds to obtain current data sets using RestAPI (yfinance).
       - Integrate the 2nd repo using streamlit framework to view the captured data sets.
 
    v2:
       - Integrate a SQLite database to store the data in one or more tables. 
       - Query data from SQLite db and export data into either a comma delimited or excel file format.
       - Produce plotly or matplotlib graphics for certain data sets.
       
              
Solution Design (high-level):

 -- Change Log --

4/15/2024: 

    -- Jonathan -- Investment_Portfolio_App

    -Changed xlsx sheet to separate each transaction.
    -Rewrote most of the originally forked app to properly utilize FIFO accounting.  
    -Added code to pull current data from yfinance API.
    -Added code to iterate on each transaction in the transactions tab, and copy each ticker only once to the summary page.
    -Added calculations for profits, realized gains, and current value for each ticker.

    -- Joe -- Invesment Portfolio (SWAST Handover Delays -- source/repo)

    - Explored the existing projects for finance sector.
    - Created a new python file investment_portfolio.py
    - Added/updated the code/functions in the above file.
    - Added an image file with NTAI logo.
    - Tested the investment_portfolio.py

4/16/2024:  

    -- Jonathan --

    -Added cost basis calculation to summary page.
    -Added unrealized gains calculation to summary page. 
    -Added rounding to 2 decimal places. 

4/17/2024: 
    - Added a new column called "Investor" in the existing spreadsheet provided by Jonathan.
    - modify the code in streamlit repo to include the new column "Investor"  provided by Joe.   
    - create branch off master -> https://github.com/jonrebelo/Investment_Portfolio_App/tree/JoeLi_branch    

Ongoing issues: 

     -- Jonathan --

    -Adding new ticker in transaction sheet results in key error. 
    -Handle all the null values being displayed on streamlit app. 
    -Double check consistency of outputs to ensure cells don't change unexpectedly. 
     
       -- ** completed 4/18/2024 **
     
     -- Joe --
     
    - Continued the cycle "test > develop > debug > test". 
    - Added more code into the .py file for rendering the logo, title and content.
    - Added a column called "Investor" in the existing spreadsheet provided by Jonathan.
    - Created an env for running the web application.
    - Fixed the code after testing with the repo branch @ https://github.com/jonrebelo/Investment_Portfolio_App/tree/JoeLi_branch 
   
        -- ** completed 4/18/2024 **
     
4/17/2024: 
    - confirm if adding any new columns in excel spreadsheet for 2nd repo will affect
      the existing code in the 1st repo (Investment_Portfolio_App).
    - add flowchart for 2nd repo to show how the code works.
    - update yml file with the latest changes.
       -- ** completed 4/18/2024 **

4/18/2024 & 4/19/2024:
-- Joe --
   - Joined a team daily stand-up meeting with Jonathan and Michael at 1:00PM for 40 minutes to 80 minutes. Reported what I had done and any issues and next steps.
   - Developed investment_portfoli.py to implement the design.
   - Modified my python code to accommodate the new requirements for personal trading data to be rendered with streamlit.
   - Debugged and fixed the errors and bugs and created investment_portfolio_2.py
   - Added package "import subprocess" for calling another .py file created by Jonathon (backend process/calculation).
   - Changed the file path from absolute to relative.
   - To call existing .py file (--Joe --).
   - added package "import subprocess" for calling another .py file created by Jonathon (backend process/calculation).
   - Changed the file path from absolute to relative.
   - Add column for different investors (Joe / Jonathan) in the excel file.

-- Jonathan --
   - fixed the key error issue by changing the excel sheet name.
   - fixed the null values being displayed on streamlit app.
   - Our investors sheet had "All" listed as one of the investors but there was no "All" sheet name so it didn't know what to pull.
   - I changed the excel sheet so that instead of "All" being tied to ID 99 it's "Summary" instead and everything works as expected.
   - Add column for different investors (Joe / Jonathan) in the excel file.

--All members--
   - Work with my teammates for the <<README.md>> and <<00-Investment_Portfolio_App-v2024.04.17.yml>> file.
   - v1 of the project is complete end of day 4/19/2024.

To do (Future work):
    
    - To add a SQLite database to store the data in one or more tables.
    - To query data from SQLite db and export data into either a comma delimited or excel file format.
    - To produce plotly or matplotlib graphics for certain data sets.
    - To explore web page input option.
    - Clean up the python code (such as print() for debugging)

Solution Code Description (low-level design): 
    * Add a transaction (buy/sell) to the "Transactions" sheet of the excel file.
        - [Investor, ID, Transaction Date, Ticker, Type, Shares, Cost Per Share] fields only, leave "Total" blank.
	* yfinance API to pull current stock data into Transaction sheet of excel file.
    * Calculate the cost basis, realized gains, and current value of each ticker in the excel file.
    * Summary page to display the realized gains, unrealized gains, and cost basis of each ticker.
    * Streamlit to display the data per ticker for each investor.

    * Software packages (Python packages, etc.)
          yfinance, pandas, numpy, datetime, matplotlib.pyplot, plotly, plotly import __version__, plotly.offline, 
          plotly.graph_objs, plotly.graph_objects, plotly.express, streamlit, time, openpyxl, openpyxl.utils.dataframe,
          openpyxl.styles, subprocess
	
Actual Working Product Code: 
    Functions, modules, packages, documentation found in the 
    (master branch) repo @ https://github.com/jonrebelo/Investment_Portfolio_App 
    
    
Application Instructions:

    * Step-by-step instructions for OTHERS:
        Instructions to install, set-up, and use your software:
        # obtain repo from github
            download the code from the repo (master branch) @ https://github.com/jonrebelo/Investment_Portfolio_App  
          
         # create virtual envrionment 
            conda create --name Investment_Portfolio_App -c conda-forge yfinance pandas numpy datetime matplotlib.pyplot plotly streamlit time openpyxl subprocess
          
        ## Activate the environment
            conda activate Investment_Portfolio_App

        ## Install additional packages in the environment for generating diagrams
        plotly import __version__ plotly.offline plotly.graph_objs plotly.graph_objects plotly.express openpyxl openpyxl.utils.dataframe openpyxl.styles
        
        ## Run the code
           - streamlit run Investment_Portfolio_App.py       
           - Enter buy/sell transaction in the "Transactions" sheet ensuring the stock ticker symbol is correct.
             note: Transaction total must be left blank (program will calculate this).