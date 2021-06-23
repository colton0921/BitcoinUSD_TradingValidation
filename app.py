import streamlit as st
# Raw Package
import numpy as np
import pandas as pd
import datetime
from dateutil import relativedelta

#Data Source
#import yfinance as yf

#Data viz
#import plotly.graph_objs as go
import matplotlib.pyplot as plt
import seaborn as sns

#   Global config
st.set_page_config(page_title='Bitcoin Earning Stretegy',layout='centered',initial_sidebar_state='expanded')
st.title(" Bitcoin Earning Stretegy ")

#   ---------------------------------Load CSV---------------------------------
@st.cache(persist=True,allow_output_mutation=True)
def get_data():
    url_recipe = "bitstampUSD_1-min_2012Jan_to_2021Mar.csv"    #data_recipe_clean  data_recipe_deploy
    df = pd.read_csv(url_recipe)
    df.dropna(inplace=True)
    df['time'] = df['Timestamp'].apply(lambda x: datetime.datetime.utcfromtimestamp(int(x)))
    df['year'] = df['Timestamp'].apply(lambda x: datetime.datetime.utcfromtimestamp(x).date().year)
    df['date'] = df['Timestamp'].apply(lambda x: datetime.datetime.utcfromtimestamp(x).date())
    df = df[df['year']>=2015]
    return df
df = get_data()   #Get general data
#st.write(df.head(15))

#   ---------------------------------Function---------------------------------
import time
def get_cloest_price(_time):
    while True:  # if df[df['time'] == _time]['Open'].shape[0] != 0:
        try:
            return df[df['time'] == _time]['Open'].iloc[0]
        except:
            _time += datetime.timedelta(minutes= 1)

def get_trade_result(start_year,start_month,start_day,end_year,end_month,end_day,buy_hour,sell_hour,buy_weekday,sell_weekday):
    start_time = datetime.datetime(int(start_year),int(start_month),int(start_day),int(buy_hour),0) #datetime.datetime(2018,6,1,1,0)
    end_time = datetime.datetime(int(end_year),int(end_month),int(end_day),0,0)
    cur_time = start_time
    cur_balance = 1000000
    d = {'Buy_time': [start_time], 'Sell_time': [end_time], 'Opening': [cur_balance], 'Buy_price':[0],  'Sell_price':[0], 'Profit': [0], 'Balance':[cur_balance]}
    trade_df = pd.DataFrame(data=d)

    dict_weekday = {
        1:relativedelta.relativedelta(weekday=relativedelta.MO(0)),
        2:relativedelta.relativedelta(weekday=relativedelta.TU(0)),
        3:relativedelta.relativedelta(weekday=relativedelta.WE(0)),
        4:relativedelta.relativedelta(weekday=relativedelta.TH(0)),
        5:relativedelta.relativedelta(weekday=relativedelta.FR(0)),
        6:relativedelta.relativedelta(weekday=relativedelta.SA(0)),
        7:relativedelta.relativedelta(weekday=relativedelta.SU(0))
    }
    Buy_time_relative_delta = dict_weekday[buy_weekday]
    Sell_time_relative_delta = dict_weekday[sell_weekday]

    while cur_time + datetime.timedelta(days= 7) < end_time:
        Buy_time = cur_time + Buy_time_relative_delta
        Sell_time = Buy_time + Sell_time_relative_delta + datetime.timedelta(hours= int(sell_hour)-int(buy_hour))  
        #st.write(Buy_time, Sell_time)

        cur_buy_in = get_cloest_price(Buy_time)  #df[df['time'] == Buy_time]['Open'].iloc[0]
        cur_buy_out = get_cloest_price(Sell_time)  #df[df['time'] == Sell_time]['Open'].iloc[0]
        #st.write(cur_buy_in, cur_buy_out, cur_balance)
        
        cur_time += datetime.timedelta(days= 7)
        opening_bal = cur_balance
        cur_balance = cur_balance * ( 1 + ( cur_buy_out - cur_buy_in) / cur_buy_in)
        
        trade_df.loc[trade_df.shape[0]] = [Buy_time, Sell_time, opening_bal, cur_buy_in, cur_buy_out, ( 1 + ( cur_buy_out - cur_buy_in) / cur_buy_in), cur_balance]

    return trade_df.iloc[1:]

st.sidebar.header("Start date: ")
start_year = st.sidebar.slider("start_year", min_value=2015, max_value=2021, value=2018, step=1, key= "001" )
start_month = st.sidebar.slider("start_month", min_value=1, max_value=12, value=6, step=1, key= "002" )
start_day = st.sidebar.slider("start_day", min_value=1, max_value=30, value=1, step=1, key= "003" )
st.sidebar.header("End date: ")
end_year = st.sidebar.slider("end_year", min_value=2015, max_value=2021, value=2021, step=1, key= "005" )
end_month = st.sidebar.slider("end_month", min_value=1, max_value=12, value=3, step=1, key= "006" )
end_day = st.sidebar.slider("end_day", min_value=1, max_value=31, value=31, step=1, key= "007" )

st.sidebar.header("Buying & Selling time: ")
buy_weekday = st.sidebar.slider("buy_weekday", min_value=1, max_value=7, value=7, step=1, key= "009" )
buy_hour = st.sidebar.slider("buy_hour", min_value=0, max_value=23, value=1, step=1, key= "004" )
sell_weekday = st.sidebar.slider("sell_weekday", min_value=1, max_value=7, value=5, step=1, key= "010" )
sell_hour = st.sidebar.slider("sell_hour", min_value=0, max_value=23, value=7, step=1, key= "008" )

trade_df = get_trade_result(start_year,start_month,start_day,end_year,end_month,end_day,buy_hour,sell_hour,buy_weekday,sell_weekday)
#st.dataframe(trade_df)

dict_weekday = {
        1:'Mon',
        2:'Tue',
        3:'Wed',
        4:'Thur',
        5:'Fri',
        6:'Sat',
        7:'Sun'
    }

st.write('You strategy is to buy on ', dict_weekday[buy_weekday], ' at ', buy_hour)
st.write('and sell on ', dict_weekday[sell_weekday], ' at ', sell_hour)
st.write('Your balance until: ', datetime.datetime(int(end_year),int(end_month),int(end_day),0,0).date(), ' is USD ', int(trade_df['Balance'].iloc[trade_df.shape[0]-1]))

fig, ax = plt.subplots(figsize=(10,8))
g = sns.lineplot(x="Sell_time", y="Balance", data=trade_df)
st.pyplot(fig)

