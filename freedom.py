# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 15:20:21 2021

@author: rrobles
"""
# %% Consts
TICKER = 'SAN'
INDEX = 'IBEX 35'
NUM_DAYS = 400
WEEKS_PER_YEAR = 52
RESULTS_SIZE = 5

# %% Imports
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import investpy
import seaborn as sns
import mplfinance as mpf

# %% Get stocks and indexes
df_stocks = investpy.stocks.get_stocks(country='spain')
df_indexes = investpy.indices.get_index_countries()

# %% Fecth data
today = datetime.today()
yearAgo = today - timedelta(days = NUM_DAYS)
initDate = yearAgo.strftime('%d/%m/%Y')
endDate = today.strftime('%d/%m/%Y')

df_list = list()

for row in df_stocks.symbol:
    try:
        df = investpy.get_stock_historical_data(stock=row, country='spain', from_date=initDate, to_date=endDate, interval='Weekly')
        df['Ticker']=row
        if df.shape[0] > WEEKS_PER_YEAR:
            df_list.append(df)
        else:
            print('Insufficient data: ',row)
    except IndexError:
        print('Stock unavailable: ', row)
    
    
df_index = investpy.get_index_historical_data(index=INDEX, country='spain', from_date=initDate, to_date=endDate, interval='Weekly')

# %% Calculate Relative Performace y 52 weeks SMA Relative Performance
for df in df_list:
    df['ROC'] = df.Close.pct_change() * 100
    RP = (df.Close/df_index.Close)*100
    SMA52RP = RP.rolling(window=52).mean()
    df['RP'] = RP
    df['SMA52RP'] = SMA52RP

# %% Calculate MRP
for df in df_list:
    mansfieldRP = (df['RP']/df['SMA52RP']-1)*10
    df['mansfieldRP'] = mansfieldRP

# %%
max = 0
df_result = pd.DataFrame(np.zeros((RESULTS_SIZE, 3)), columns = ['mansfieldRP', 'Ticker', 'Name'])
#df_results_list = list()

# Buscamos los RESULT_SIZE valores con mayor mansfieldRP
for df in df_list:
    if df['mansfieldRP'].iloc[-1] > df_result['mansfieldRP'].min():       
        # Sustituimos la menor con la actual
        min_index = df_result['mansfieldRP'].idxmin()
        mansfieldRP_value = df['mansfieldRP'].iloc[-1]
        ticker_value = df['Ticker'].iloc[-1]
        # Rellenamos los nombres
        stock_name = df_stocks.loc[df_stocks['symbol'] == ticker_value]['name'].iloc[0]
        df_result.loc[min_index] = mansfieldRP_value, ticker_value, stock_name
        
# %% Plot
fig, ax = plt.subplots(2)
#ax[0].plot(data)
ax[0].plot(df_index.Close)
#ax[1].plot(RP, 'r')
#ax[1].plot(SMA52RP, 'b')
#ax[2].plot(mansfieldRP, 'b')
#ax[2].axhline(y=0, color='r')
