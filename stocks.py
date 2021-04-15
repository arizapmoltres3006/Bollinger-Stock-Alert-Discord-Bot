import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from emoji import emojize
import discord
from discord.ext import commands

import nest_asyncio
nest_asyncio.apply()
Name = "LGHL"
equity = yf.Ticker(Name)

df = equity.history(period='2mo')[['Close']]
df.reset_index(level=0, inplace=True)
df.columns = ['ds', 'y']
df = df.set_index('ds')

# calculate Simple Moving Average with 20 days window
sma = df.rolling(window=20).mean() 
exp = df.y.ewm(span=20, adjust=False).mean()

# calculate the standar deviation
rstd = df.rolling(window=20).std()

upper_band = sma + 2 * rstd
upper_band = upper_band.rename(columns={'y': 'upper'})
lower_band = sma - 2 * rstd
lower_band = lower_band.rename(columns={'y': 'lower'})

# Making of plot
bb = df.join(upper_band).join(lower_band)
bb = bb.dropna()
buyers = bb[bb['y'] <= bb['lower']]
sellers = bb[bb['y'] >= bb['upper']]

plt.style.use('dark_background')
plt.figure(figsize=(10,10))
plt.plot(bb['upper'], color='#ADCCFF', alpha=0.2, label='Bollinger Bands')
plt.plot(bb['lower'], color='#ADCCFF', alpha=0.2)
plt.plot(bb['y'], label=Name)
plt.plot(sma, linestyle='--', alpha=0.7, label='Simple Moving Average')
plt.plot(buyers, "-o")
plt.plot(sellers,"-p")
plt.title("Stock Price and BB")
plt.legend(loc='best')
plt.fill_between(bb.index, bb['lower'], bb['upper'], color='#ADCCFF', alpha=0.2)

ax = plt.gca()
fig = plt.gcf()
fig.autofmt_xdate()
plt.ylabel('SMA and BB')
plt.grid()
plt.savefig('bollinger')

# Calculate evolution
evolution = round((bb['y'][-1]-sma['y'][-1])/(2*rstd['y'][-1])*100)

today = bb['y'][-1]
yesterday = bb['y'][-2]

percentage_increase = 100 * (today - yesterday) / yesterday
date = str(bb.index[-1]).split()[0]



client = discord.Client()

TOKEN = open("Token.txt","r").readline()
@client.event
async def on_ready():
    channel=client.get_channel(831644232795160680)
    message = emojize(":date:", use_aliases=True) + ' ' + date + '\n'
    message += (percentage_increase > 0)*emojize(":small_red_triangle:", use_aliases=True) + (percentage_increase < 0)*emojize(":small_red_triangle_down:", use_aliases=True)
    message += '{}% | {}$\n\n'.format(round(percentage_increase,2), round(today, 2))
    await channel.send(message)   
 
    if evolution > 0:
        message += '{}% recommended *SELL* for added rentability'.format(evolution)
    else:
        message += '{}% recommended *BUY* for added rentability'.format(-evolution)
    if abs(percentage_increase) >= 0.5 or evolution >= 50: 
        await channel.send(file=discord.File('bollinger.png'))
client.run(TOKEN)  


