# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 15:20:21 2021

@author: rrobles
"""
# %% Consts

NUM_DAYS = 365*6
WEEKS_PER_YEAR = 52

AVG_PERIODS = 52
RP_FILTER = 2

INDEX_SELECTION = 'IBEX 35'

STOCK_SELECTION = ['ANA',    # 0
                   'ACX',    # 1
                   'ACS',    # 2
                   'AENA',   # 3
                   'ALM',    # 4
                   'AMA',    # 5
                   'MTS',    # 6
                   'SABE',   # 7 
                   'BKT',    # 8
                   'BBVA',   # 9
                   'CABK',   #10
                   'CLNX',   #11 
                   'CIEA',   #12
                   'COL',    #13
                   'ENAG',   #14 
                   'ELE',    #15
                   'FER',    #16
                   'FLUI',   #17
                   'GRLS',   #18
                   'ICAG',   #19
                   'IBE',    #20
                   'ITX',    #21
                   'IDR',    #22
                   'MAP',    #23
                   'MEL',    #24
                   'MRL',    #25
                   'NTGY',   #26
                   'PHMR',   #27
                   'REE',    #28
                   'REP',    #29
                   'SAN',    #30
                   'SGREN',  #31
                   'SLRS',   #32
                   'TEF',    #33
                   'VIS']    #34

COUNTRY_SELECTION = 'spain'

# %% Imports
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import investpy
import seaborn as sns
import mplfinance as mpf

# %% Weekly data
def daterange(start_date, end_date):
     for n in range(0, int((end_date - start_date).days) + 1, 7):
         yield start_date + timedelta(n)
         
# %% Sunday finder
def findsunday(date):
    sunday = date - timedelta((date.weekday() + 1) % 7 )
    return sunday

# %% Is weekend?
def isweekend():
    return datetime.today().weekday() >= 5
    
# %% Get stocks and indexes
df_stocks = investpy.stocks.get_stocks(country=COUNTRY_SELECTION)
df_indexes = investpy.indices.get_index_countries()

# %% Fecth data
today = datetime.today()
yearAgo = today - timedelta(days = NUM_DAYS)
initDate = yearAgo.strftime('%d/%m/%Y')

endDate = findsunday(date.today()).strftime('%d/%m/%Y')
#endDate = findsunday(date.today() - timedelta(days = 6)).strftime('%d/%m/%Y')
#endDate = date(2021, 4, 4).strftime('%d/%m/%Y')
#endDate = today.strftime('%d/%m/%Y')

df_list = list()

for row in STOCK_SELECTION: #df_stocks.symbol:
    try:
        df = investpy.get_stock_historical_data(stock=row, country=COUNTRY_SELECTION, from_date=initDate, to_date=endDate, interval='Weekly')

        df_daily = investpy.get_stock_recent_data(stock=row, country=COUNTRY_SELECTION, interval='Daily')

        df['Ticker']=row
        if df.shape[0] > WEEKS_PER_YEAR:
            df_list.append(df)
        else:
            print('Insufficient data: ',row)
    except IndexError:
        print('Stock unavailable: ', row)
    
    
df_index = investpy.get_index_historical_data(index=INDEX_SELECTION, country=COUNTRY_SELECTION, from_date=initDate, to_date=endDate, interval='Weekly')
df_index['ROC'] = df_index.Close.pct_change() * 100

# %% Calculate Relative Performace y 52 weeks SMA Relative Performance
for df in df_list:
    df['ROC'] = df.Close.pct_change() * 100
    RPD = (df.Close/df_index.Close)*100
    RP = RPD.rolling(window=RP_FILTER).mean()
    SMA52RP = RPD.rolling(window=AVG_PERIODS).mean()
    df['RP'] = RP
    df['SMA52RP'] = SMA52RP

# %% Calculate MRP
for df in df_list:
    mansfieldRP = (df['RP']/df['SMA52RP']-1)*10
    df['mansfieldRP'] = mansfieldRP

# %%
RESULTS_SIZE = 3

df_results_list = list()
df_equity = pd.DataFrame(index=df.index, columns = ['Equity', 'EquityIndex'])


start_date = findsunday(date(2021, 1, 1))
#end_date = findsunday(date(2021, 4, 4))
#end_date = findsunday(date.today()) - timedelta(days = 6)
end_date = findsunday(date.today() - timedelta(days = 1))

cumROC = 100
cumROCIndex = 100

success_rate = 0
success = 0
fail = 0
fail_acc = 0
fail_max = 0

for dt in daterange(start_date, end_date):
    #print(dt.strftime("Analizando semana %d-%m-%Y"))
    df_result = pd.DataFrame(np.zeros((RESULTS_SIZE, 6)), columns = ['Date', 'mansfieldRP', 'Ticker', 'Name', 'ROC', 'ROCIndex'])
    # Buscamos los valores con mayor mansfieldRP
    for df in df_list:
        try:
            if df.loc[dt].mansfieldRP > df_result['mansfieldRP'].min():       
                # Sustituimos la menor con la actual
                min_index = df_result['mansfieldRP'].idxmin()
                mansfieldRP_value = df.loc[dt].mansfieldRP
                ticker_value = df.loc[dt].Ticker
                if dt + timedelta(days = 7) <= end_date:
                    ROC_next_week = df.loc[dt + timedelta(days = 7)].ROC
                    ROC_next_week_index = df_index.loc[dt + timedelta(days = 7)].ROC
                else:
                    ROC_next_week = 0
                    ROC_next_week_index = 0
                # Rellenamos los nombres
                stock_name = df_stocks.loc[df_stocks['symbol'] == ticker_value]['name'].iloc[0]
                #Guardamos el resultado
                df_result.loc[min_index] = dt, mansfieldRP_value, ticker_value, stock_name, ROC_next_week, ROC_next_week_index
        except KeyError:
            print('Date unavailable:', df['Ticker'][-1])
            
    ROCMean = df_result['ROC'].mean()
    ROCIndex = df_result['ROCIndex'][0]
    if ROCMean > ROCIndex:
        success = success + 1
        fail_acc = 0
    else:
        fail = fail + 1
        fail_acc = fail_acc + 1
        if fail_acc > fail_max:
            fail_max = fail_acc
    
    #Almacenamos retornos acumulados
    cumROC = cumROC * (1 + (ROCMean / 100))
    cumROCIndex = cumROCIndex * (1 + (ROCIndex / 100))
    
    df_result['ROCmean'] = ROCMean
    df_result['AccROC'] = cumROC
    df_result['AccROCIndex'] = cumROCIndex
    df_results_list.append(df_result)
    
    #Almacenamos equity de sistema y de índice
    df_equity.loc[dt] = cumROC, cumROCIndex 
 

print('\r\n SUCCESS RATE: ')
print('\r Aciertos:', success)
print('\r Fallos:', fail)
print('\r Máximo número de fallos consecutivos: ', fail_max)
print('\r Tasa:', success/(success + fail))

print('\r\n EQUITY: ')
print('\r Cartera:', df_equity.Equity[-1])
print('\r Indice:', df_equity.EquityIndex[-1])
    
print('\r\n RESULTADOS ÚLTIMA SEMANA: ', df_results_list[-3].Date[0] + timedelta(days = 8), ' al ',df_results_list[-3].Date[0] + timedelta(days = 14))
print('\r Cartera: ', df_results_list[-3].Ticker[0], df_results_list[-3].Ticker[1], df_results_list[-3].Ticker[2])
print('\r Retorno cartera: ', df_results_list[-3].ROCmean[0])
print('\r Retorno indice: ', df_results_list[-3].ROCIndex[0])
#print('\r', df_results_list[-2])
#print('\r', df_results_list[-1])
print('\r\n RESULTADOS SEMANA ACTUAL: ', df_results_list[-2].Date[0] + timedelta(days = 8), ' al ', df_results_list[-2].Date[0] + timedelta(days = 14))
print('\r Cartera: ', df_results_list[-2].Ticker[0], df_results_list[-2].Ticker[1], df_results_list[-2].Ticker[2])
print('\r Retorno latente cartera: ', df_results_list[-2].ROCmean[0])
print('\r Retorno latente indice: ', df_results_list[-2].ROCIndex[0])

print('\r\n COMPOSICIÓN PROVISIONAL SIGUIENTE CARTERA: ', df_results_list[-1].Date[0] + timedelta(days = 8), ' al ', df_results_list[-1].Date[0] + timedelta(days = 14))
print('\r Cartera: ', df_results_list[-1].Ticker[0], df_results_list[-1].Ticker[1], df_results_list[-1].Ticker[2])

# %% Plot equity (system + index)
plt.plot(df_equity.Equity)
plt.plot(df_equity.EquityIndex)
plt.xlabel('Time - Weeks')
plt.ylabel('Equity')
  
plt.title('Mansfield')
plt.show()

