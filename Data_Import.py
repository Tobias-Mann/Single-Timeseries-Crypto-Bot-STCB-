import pandas as pd 
from ta import add_all_ta_features
import os

#PATH = "/Users/Tobias/OneDrive - Universitaet St.Gallen/MBF/CryptoBot/Single-Timeseries-Crypto-Bot/"
PATH = '/Users/tgraf/Google Drive/Uni SG/Master/Smart Data Analytics/00 Group Project/Repository/Single-Timeseries-Crypto-Bot/' # Set your path to the checkout
os.chdir(PATH)

"""
### DATA SOURCE 1: KAGGLE ------------------------------
# import dataframe
df_merged = pd.read_csv('./Data/400 - 1m - Trading Pairs (2013-2020)/btcusd.csv')
print(df_merged.info())

# convert values from timestamp to date
df_merged['time'] = pd.to_datetime(df_merged['time'], unit='ms')
print(df_merged['time'])

# this doesn't work well, we have multiple obs with the same timestamp but different price values

### DATA SOURCE 2: CRYPTODATADOWNLOAD.com ------------------------------
# import dataframe
df2 = pd.read_csv('./Data/Bitfinex_BTCUSD_minute.csv', 
    header=1)
print(df2.info())

# convert values from timestamp to date
df2['unix'] = pd.to_datetime(df2['unix'], unit = 'ms')
print(df2['unix'])

# we only have data until 15th of November, so less than a month
"""

### DATA SOURCE 3: GITHUB  ------------------------------
#https://github.com/Zombie-3000/Bitfinex-historical-data

headers = ['Time', 'Open', 'Close', 'High', 'Low', 'Volume']
df_13 = pd.read_csv('https://raw.githubusercontent.com/Zombie-3000/Bitfinex-historical-data/master/BTCUSD/Candles_1m/2013/merged.csv?raw=true', names = headers)
df_14 = pd.read_csv('https://raw.githubusercontent.com/Zombie-3000/Bitfinex-historical-data/master/BTCUSD/Candles_1m/2014/merged.csv?raw=true', names = headers)
df_15 = pd.read_csv('https://raw.githubusercontent.com/Zombie-3000/Bitfinex-historical-data/master/BTCUSD/Candles_1m/2015/merged.csv?raw=true', names = headers)
df_16 = pd.read_csv('https://raw.githubusercontent.com/Zombie-3000/Bitfinex-historical-data/master/BTCUSD/Candles_1m/2016/merged.csv?raw=true', names = headers)
df_17 = pd.read_csv('https://raw.githubusercontent.com/Zombie-3000/Bitfinex-historical-data/master/BTCUSD/Candles_1m/2017/merged.csv?raw=true', names = headers)
df_18 = pd.read_csv('https://raw.githubusercontent.com/Zombie-3000/Bitfinex-historical-data/master/BTCUSD/Candles_1m/2018/merged.csv?raw=true', names = headers)
df_19 = pd.read_csv('https://raw.githubusercontent.com/Zombie-3000/Bitfinex-historical-data/master/BTCUSD/Candles_1m/2019/merged.csv?raw=true', names = headers)

len(df_19)

# Merge dataframes
data_frames = [df_13, df_14, df_15, df_16, df_17, df_18, df_19]
df_merged = pd.concat(data_frames)

#convert timestamp to datae
df_merged['Time'] = pd.to_datetime(df_merged['Time'], unit = 'ms')
print(df_merged.info())

# we should have a df_merged with 3'679'200 rows (7y*365d*24h*60m)but only have 2'630'217 rows --> this is purely due to missing data cf sum([x.shape[0] for x in data_frames]) = 2'630'217

# plot the open prices against Time
# this takes a while
"""
df_merged.plot(x ='Time', y='open', kind = 'scatter')
plt.show()
"""

# reset index and sort values according to Time
df_merged = df_merged.sort_values(by=['Time'], ascending = True, na_position = 'last')
df_merged = df_merged.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')
df_merged = df_merged.rename(columns={"index": "old_index"})

### Feature Engineering ------------------------

# Time
df_merged['day'] = df_merged['Time'].dt.day
df_merged['Week'] = df_merged['Time'].dt.weekofyear
df_merged['Weekday'] = df_merged['Time'].dt.weekday
df_merged['month'] = df_merged['Time'].dt.month
df_merged['year'] = df_merged['Time'].dt.year

# shift 1 in order to calculate returns
for col in headers:
    df_merged[col] = df_merged[col].shift(1)
df_merged = df_merged.dropna()

# daily return
df_merged['Daily_return'] = (df_merged['Close'] / df_merged['Close'].shift(1)) - 1
df_merged['Daily_return_100'] = ((df_merged['Close'] / df_merged['Close'].shift(1)) - 1) * 100

# cumulative return
df_merged = df_merged.dropna()
df_merged['Cumulative_return'] = (df_merged['Close'] / df_merged['Close'].iloc[0]) - 1
df_merged['Cumulative_return_100'] = ((df_merged['Close'] / df_merged['Close'].iloc[0]) - 1) * 100

# all technical indicators
df_merged = add_all_ta_features(
    df_merged, open="Open", high="High", 
    low="Low", close="Close", volume="Volume", fillna=True)

print(df_merged)
print('Number of rows: {}, Number of columns: {}'.format(*df_merged.shape))

# Write csv of merged files
pd.DataFrame.to_csv(df_merged, 'df_raw.csv', sep=',', na_rep='.', index=False)