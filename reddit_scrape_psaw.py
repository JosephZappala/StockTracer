from psaw import PushshiftAPI

import praw
import datetime as dt
import time as tm
import csv 
import re
import pandas as pd
import numpy as np 

import os.path

reddit = praw.Reddit(
    client_id='QdrJ38ixUfNCq1F9Qvrj8g',
    client_secret='ivzb7L0bBMqrJiTo4nog7f4D4iLXPA',
    password='hackathon2022$',
    user_agent='scrape_script',
    username='jesk_hacks'
)

api = PushshiftAPI(reddit)

def getDic(post):
    # post.comments.replace_more(limit=0)
    # comments = post.comments.list()
    return {    "Title": post.title,
                "Subreddit": post.subreddit,
                "Created": dt.datetime.fromtimestamp((post.created)),
                "Downs": post.downs,
                "Ups": post.ups,
                "Score": post.score,
                "Likes": post.likes,
                "Num. Comments": post.num_comments,
                "Num. Crossposts": post.num_crossposts,
                "Views": post.view_count,
                # "Comments": [comment.body for comment in comments[:100]]
                
                }

def getStocks(stocklistfilename):
    stockList = []
    try:
        infile = open(stocklistfilename, 'r')
    except Exception as e:
        print("Error opening file.")
        exit(1)
    reader = csv.reader(infile)
    for row in reader:
        stockList.append(   {'symbol': row[0],
                                'name': row[1] })
    infile.close()
    return stockList

def searchReddit(   startDateString, endDateString,
                    subreddit, q, max_results, limit=100):
    # after = int(dt.datetime(2020, 12, 1).timestamp())
    # before = int(dt.datetime(2021, 3, 1).timestamp())
    sm, sd, sy = int(startDateString[0:2]), int(startDateString[2:4]), int(startDateString[4:])
    em, ed, ey = int(endDateString[0:2]), int(endDateString[2:4]), int(endDateString[4:])
    after = int(dt.datetime(sy, sm, sd).timestamp())
    before = int(dt.datetime(ey, em, ed).timestamp())   
    gen = api.search_submissions(   after=after,
                                    before=before,
                                    subreddit=subreddit,
                                    q=q,
                                    max_results_per_request = max_results,
                                    limit=limit)
    
    return [ getDic(submission) for submission in gen ]

def getDaysInMonth(month, year):
    if month in ['01', '03', '05', '07', '08', '10', '12']:
        return 31
    elif month in ['02', '04', '06', '09', '11']:
        return 30
    elif int(year) % 4 == 0:
        return 29
    else:
        return 28

def findAndWrite(fname, ticker, name=None, limit=100):
    # fname = ticker + '.csv'
    # fname = 'CSV_files\\' + ticker + '.csv'
    # print(fname)
    # CSV_files\TSLA.csv
    # exit()
    # if os.path.exists(fname):
    #     # print('Found')
    #     sel = input(f'\nFile {fname} already exists. Would you like to overwrite? (Y/N): ')

    #     if sel == 'Y' or sel == 'y':
    #         pass
    #     elif sel == 'N' or sel == 'n':
    #         print("Exiting program.")
    #         exit(2)
    #     else:
    #         print("Invalid entry. Exiting program.")
    #         exit(3)
    # else:
    #     print(f'\nFile {fname} not found. Creating new file.')

    subreddit_list = ['wallstreetbets', 'stocks', 'investing', 'pennystocks', 'robinhood']
    subreddit_names = [ 'r/' + sub for sub in subreddit_list ]

    print(f'\nSearching for {limit} posts in each subreddit: {subreddit_names}')

    print()
    print('Dates written in DD/MM/YYYY format')
    tm.sleep(2)

    stockDictList = list()
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    years = ['2020', '2021', '2022']
    
    for year in years:
        if year == '2022' and int(month) > 2:
            continue 
        else:
            for month in months:
                # timestring = year + '-' + month + '-' + '01' + ' 00:00:00'
                timestring = '01/' + month + '/' + year
                print('\n' + timestring)
                count = 0
                for sub in subreddit_list:
                    print(f'Searching {limit} posts in r/{sub}')
                    d = searchReddit(   startDateString=month+'01'+year,
                                        endDateString=month+'28'+year,
                                        subreddit=sub,
                                        q=None,
                                        max_results=100,
                                        limit=limit)

                    for dic in d:
                        if (re.search(r'\s+\$?' + ticker + r'\$?\s+', dic['Title'])) or ((re.search(r'\s+\$?' + name + r'\$?\s+', dic['Title'])) if name is not None else False):
                            count += 1
                
                stockDictList.append(   {'Time': timestring,
                                'Count': count} )

    csv_columns = ['Time', 'Count']
    with open(fname, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        for stockDict in stockDictList:
            writer.writerow(stockDict)
    print(f'File {fname} successfully written.')
    

def fillDataframe(df):
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    years = ['2020', '2021', '2022']

def loadTickerListFile(filename='CSV_files\\tickers2.csv', limit=200):
    stonks = getStocks(filename)
    for stonk in stonks:
        symbol, name = stonk['symbol'], stonk['name']
        fname = 'CSV_files\\' + symbol + '.csv'
        findAndWrite(fname, symbol, limit=limit)

if __name__ == '__main__':
    default = str(input('Load from default file? (Y/N): '))
    if default == 'Y' or default == 'y':
        loadTickerListFile(filename=r'tickers2.csv')
        
    else:
        ticker = str(input("Enter a ticker symbol: ")).upper()
        num = str(input("Enter number of posts to search in each subreddit (press ENTER for default 100): "))
        if len(num.strip()) == 0:
            num = 100
        else:
            num = int(num)
        fname = 'CSV_files/' + ticker + '.csv'
        # CSV_files/AMC.csv
        # CSV_files/GME.csv
        if os.path.exists(fname):
            # print('Found')
            print('\nFile {fname} already exists')
            print("Exiting program.")
            exit(2)
            
        else:
            print(f'\nFile {fname} not found. Creating new file.')
        findAndWrite(fname, ticker, limit=num)

def makeFile(ticker):
    # if you want choice for like the amount
    """
    ticker = str(input("Enter a ticker symbol: ")).upper()
    num = str(input("Enter number of posts to search in each subreddit (press ENTER for default 100): "))
    if len(num.strip()) == 0:
        num = 100
    else:
        num = int(num)
        """

    num = 100
    fname = 'CSV_files/' + ticker + '.csv'
    # CSV_files/AMC.csv
    # CSV_files/GME.csv
    if os.path.exists(fname):
        # print('Found')
        print('\nFile {fname} already exists')
        #print("Exiting program.")
        #exit(2)
        
    else:
        print(f'\nFile {fname} not found. Creating new file.')
        findAndWrite(fname, ticker, limit=num)
    