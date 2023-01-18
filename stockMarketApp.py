import sqlite3
import datetime
from yahoo_fin.stock_info import *
import streamlit as st
import yfinance as yf
from ta.volatility import BollingerBands
from ta.trend import MACD
from ta.momentum import RSIIndicator

# created a connection
con = sqlite3.connect("stock.db")
#created a cursor
cur = con.cursor()
#Use the cursor To execute the command use if not exist to eliminate any errors
cur.execute("CREATE TABLE IF NOT EXISTS stocks(Date, Open, High, Low, Close, Adj_Close, Volume, bb_h, bb_l)")




# Header & sidebar
st.title("US Stock Market")
# store live prices in a dictionary
stock_prices = {'AAPL': get_live_price('AAPL'),
                'AMZN': get_live_price('AMZN'),
                'MSFT': get_live_price('MSFT'),
                'TSLA': get_live_price('TSLA')}

# the dictionary will display the current price of the selected stock
option = st.sidebar.selectbox(
    'Please select your prefered stock',
    ('AAPL', 'MSFT', 'TSLA','AMZN'))

st.write(f"{option} current price:",stock_prices[option])

today = datetime.date.today()
before = today - datetime.timedelta(days=700)
start_date = st.sidebar.date_input('Start date', before)
end_date = st.sidebar.date_input('End date', today)
if start_date < end_date:
    st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.sidebar.error('Error: End date must fall after start date.')


#The computation of the finanical technical indicatiors
df = yf.download(option,start = start_date,end = end_date, progress=False)
print(type(start_date))
# Bollinger Bands
indicator_bb = BollingerBands(df['Close'])
bb = df
bb['bb_h'] = indicator_bb.bollinger_hband()
bb['bb_l'] = indicator_bb.bollinger_lband()
bb = bb[['Close','bb_h','bb_l']]

# Moving Average Convergence Divergence
macd = MACD(df['Close']).macd()
# Resistence Strength Indicator
rsi = RSIIndicator(df['Close']).rsi()

# Set up main app
#plot the prices and the bolinger bands
st.write('Stock Bollinger Bands')
st.line_chart(bb)
progress_bar = st.progress(0)

# Plot MACD
st.write('Stock Moving Average Convergence Divergence (MACD)')
st.area_chart(macd)
# Plot RSI
st.write('Stock RSI')
st.line_chart(rsi)

# data of recent days
st.write('Recent data')
st.dataframe(df.tail(40))

#save button
save_button=st.sidebar.button('Save To Database')
delete_button=st.sidebar.button('Delete All From Database')
if delete_button:
    cur.execute("DROP TABLE stocks")

if save_button:
    #reset the index of the df
    df.reset_index(inplace=True)
    #.to_sql function to save data from dataframe to sql
    df.to_sql('stocks',con, if_exists='replace', index=False)
    #mydb.stock_collection2.insert_many(df.reset_index().to_dict('records'))

# read the data from database
try:
    database_datafrom_s = pd.read_sql("SELECT * FROM stocks", con = con)
    st.write('Data From Database')
    if len(database_datafrom_s) > 0:
        try:
            # Set the index to date
            database_datafrom_s.set_index('Date', inplace=True)
            # the data type of index from string to datetime
            database_datafrom_s.index = pd.to_datetime(database_datafrom_s.index)
            # slicing the database data from user input of start and end date
            st.dataframe(database_datafrom_s.loc[start_date:end_date])
        except Exception as e:
            st.warning('Slicing Error')
    else:
        st.warning('DataBase Empty Click on Button To Save')
except:
    st.write('Data Base Doesnt Exist')