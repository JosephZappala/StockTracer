from random import sample
import random
from datetime import timedelta
import PySimpleGUI as sg
import numpy as np
import pandas as pd
import os.path
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf

import reddit_scrape_psaw as rsp

#from Finance import bigBoiPlot

tickerString = "GME"

sg.theme('DarkGrey14') 
stockNameInput = ''
font = ("Sans", 20)

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def plot(x, y): 
    fig = plt.figure() 
    plt.plot(x, y) 
    return fig

# ----- Columns -----
stockList = [
    [sg.Text("Spreadsheet: "),sg.FolderBrowse(),],
]
stockStats = [
    [sg.Text("Stock Name", font = font, key = '-TITLE-')],
    [sg.Canvas(size = (450, 450), key='-CANVAS-')],
]
# ----- Full layout -----
inputt = sg.InputText(default_text='', size=(10, 1), key='-IN-', do_not_clear=False)
layout = [
    [sg.Text('Choose a Stock Ticker:', size =(25, 1), font = font)],
    [inputt],
    [sg.Submit(size = (10, 1), key="Add"), sg.Cancel("Clear") ,sg.ProgressBar(100, orientation='h', size=(20, 20), border_width=4, key='progbar',bar_color=['White','Green'])],
    [sg.Column(stockStats)]
    

]
# ----- Final Output Window -----
title = "Hackathon"
window = sg.Window(title, layout, finalize=True, margins=(60, 40)) # was 400, 150

############################################################################################################
############################################################################################################
############################################################################################################

#Create a fig for embedding.
# here is when things get realllll
plt.style.use('dark_background')
figure, bigPlot = plt.subplots(2, 2, figsize = (8.5,5.5), edgecolor = 'black', tight_layout = True)

figure.canvas.set_window_title(tickerString)

def get_closing_prices(ticker_pass, period="1mo"):  # default value of 1 day.
    try:
        data = ticker_pass.history(period)
        return data["Close"]
    except Exception as e:
        print("Failed to get required data.", e)

def reccomend():
    rec = ticker.recommendations
   
    numRows = int(len(rec) * 0.25)
    tempCol = rec[(-1 * numRows):]['To Grade']
    tempColList = list(tempCol)

    labels = 'Outperform', 'Underperform', 'Sell', 'Buy', 'Neutral'
    sizes =[]
    
    for i in labels:
        sum = 0
        for j in tempColList:
            if i == j:
                sum += 1
        sizes.append((sum / len(tempColList)) * 100)    
    
    explode = (0.1, 0.1, 0.1, 0.1, 0.1)  

    bigPlot[0,0].set_title('Buy Ratings')
    colors = ['#ce4411','#ff1493','#66b3ff','#0eb736', '#221266']
    bigPlot[0,0].pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', colors = colors, shadow=False, startangle=90)
    bigPlot[0,0].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

def pricePlot(period) :
    prices = get_closing_prices(ticker, period)
    prices_list = list(prices)
    keys = list(prices.keys())


    time_series = pd.Series(keys)
    price_series = pd.Series(prices.values)

    frame = {   'Time': time_series,
                'Price': price_series}
    price_df = pd.DataFrame(frame)
    price_df['Reddit'] = pd.Series(list())
    price_df.fillna(0, inplace=True)

    rsp.makeFile(stockNameInput)

    fname = 'CSV_files/' + tickerString + '.csv'
    # CSV_files/CCL.csv
    commentData = pd.read_csv(fname)

    timestamps = [ pd.to_datetime(t, dayfirst = True, errors='ignore') for t in commentData['Time'] ]
    commentList = commentData['Count']
    l = 0
    for j in timestamps:
        l +=1
        if keys[0] < j:
            break
    redditList = []
    for i in keys:
        if i > timestamps[l] and l < len(commentList) - 1:
            l += 1
        redditList.append(commentList.iloc[l])

    price_df['Reddit'] = pd.Series(redditList)

    bigPlot[0, 1].set_title('Reddit Popularity on Price Over Time')
    bigPlot[0, 1].grid()

    bigPlot[0,1].tick_params('x', labelbottom=False, labelrotation=40)
    
    keysbuff = keys
    
    sns.lineplot(ax=bigPlot[0, 1].twinx(), data = prices_list)
    sns.barplot(ax=bigPlot[0,1],x = keysbuff, y = price_df['Reddit'], palette = "Blues_d")
        

def FutureProjection (period) :
    prices = get_closing_prices(ticker, period)
    prices_list = list(prices)
    #prices_list = [round(val, 2) for val in prices.tolist()]

    keys = list(prices.keys())
    #
    with plt.style.context('dark_background'):
        addDate = int(.5 * len(prices_list))
        keys = keys[addDate:]
        prices_list = prices_list[addDate:]
        sns.lineplot(ax=bigPlot[1, 0], x = keys, y = prices_list)
        bigPlot[1, 0].tick_params(labelrotation=40)
        
        bigPlot[1, 0].set_title('Projected Price')
        bigPlot[1,0].grid()
        bigPlot[1,0].mouseover = True

        date = [ keys[len(keys)- 1]  ,keys[len(keys) - 1] + timedelta(days = addDate)]

        medium = [prices_list[len(prices_list)-1], ticker.info["targetMedianPrice"]]
        sns.lineplot(ax=bigPlot[1, 0], x = date, y = medium, linestyle = "dashed")

        higher = [prices_list[len(prices_list)-1], ticker.info["targetHighPrice"]]
        sns.lineplot(ax=bigPlot[1, 0], x = date, y = higher, linestyle = "dashed")

        lower = [prices_list[len(prices_list)-1], ticker.info["targetLowPrice"]]
        sns.lineplot(ax=bigPlot[1, 0], x = date, y = lower, palette= 'y' ,linestyle = "dashed")


def getVolatilty(period):
    mean = np.std(ticker)
    prices = get_closing_prices(ticker, period)
    prices_list = [round(val, 2) for val in prices.tolist()]
    currentPrice = ticker[len(prices_list) - 1]
    volPer = (mean / currentPrice) * 100
    return volPer

def majorHolders():
    holdData = ticker.major_holders
    holdData
    labels = ['Insider', 'Institutions', 'Retail']
    tempCol = holdData[:2][0]
    tempColList = list(tempCol)
    data = []
    for i in tempColList:
        data.append(float(i[:-1]))
    
    sumHold = sum(data)
    data.append(100 - sumHold)
    
    explode = (0.05, 0.05, 0.05) 
    colors = ['#0eb736','#ff1493','#221266'] 

    bigPlot[1,1].set_title('Holdings')
    bigPlot[1,1].pie(data, explode=explode, labels=labels, autopct='%1.1f%%', colors = colors, shadow=False, startangle=90)
    bigPlot[1,1].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
############################################################################################################
############################################################################################################
############################################################################################################


fig_agg = draw_figure(window['-CANVAS-'].TKCanvas, figure)

#Event loop
while True:
    event, values = window.read()
    stockNameInput = values['-IN-']

    print(stockNameInput)

    # End program if user closes window or presses the OK buttonks
    if event == "EXIT" or event == sg.WIN_CLOSED:
        break
    #Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".png", ".gif", ".jpg"))
        ]
        window["-FILE LIST-"].update(fnames)

    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-IMAGE-"].update(filename=filename)
        except:
            pass
    elif event == "Add":

        ticker = yf.Ticker(stockNameInput)
        try:
            
            if ticker.ticker != stockNameInput:
                #print("That is not a ticker symbol")
                inputt.default_text = "That ticker don\'t work bro" 
                raise ValueError('A very specific bad thing happened.')  
            # print("That is a ticker symbol")
            #inputt.default_text = ''
            # window.Element('-TITLE-').DisplayText = "fuck"
            # window.Element('-TITLE-').update()
            #dataTitle.default_text = "Stock Ticker: " + stockNameInput 
            #dataTitle.update(values=['new value 1'])
            num = 100
            randNum = random.randint(0, num)
            pricePlot('2y')
            val = randNum
            num -= randNum
            randNum = random.randint(0, num)
            window['progbar'].update_bar(val)
            reccomend()
            val += randNum
            num -= randNum
            randNum = random.randint(0, num)
            window['progbar'].update_bar(val)
            majorHolders()
            val += randNum
            num -= randNum
            randNum = random.randint(0, num)
            window['progbar'].update_bar(val)
            FutureProjection('2y')  
            val = 100
            window['progbar'].update_bar(val)
            #After making changes, fig_agg.draw()Reflect the change with.
            fig_agg.draw()
            val = 0
            window['progbar'].update_bar(val)
        except:
            #change text of input field to "That ticker don't work bro"
            #print("That is not a ticker symbol")
            #dataTitle.default_text = "Choose a Stock Ticker:"
            inputt.default_text = "That ticker don\'t work bro"
            pass
        
        

    elif event == "-CLEAR-":
        plt.clf()
        fig_agg.draw()

window.close()