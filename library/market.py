# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 23:19:09 2018

@author: SF
"""
#CCL
#http://www1.centadata.com/cci/cci_e.htm
#MLL
#https://wws.midland.com.hk/mpp/data/mr_market_index
#HIBOR
#http://www.hkab.org.hk/hibor/listRates.do?lang=en&Submit=Detail
#https://www.hangseng.com/en-hk/personal/mortgages/reference-rate/historical-hibor/
#SHIBOR
#http://www.shibor.org/shibor/web/html/shibor_e.html
#LIBOR
#https://www.global-rates.com/interest-rates/libor/american-dollar/american-dollar.aspx
#EURBOR
#https://www.global-rates.com/interest-rates/euribor/euribor.aspx
#EFFR
#https://apps.newyorkfed.org/markets/autorates/fed%20funds
#'SPCS20RSA',
#https://www.bloomberg.com/quote/SPCS20:IND
#'CSUSHPINSA',
#https://www.bloomberg.com/quote/SPCSUSA:IND
#https://us.spindices.com/indices/real-estate/sp-corelogic-case-shiller-us-national-home-price-nsa-index

#%%
from __future__ import print_function
#from googleapiclient import discovery
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import pandas
#import pandas as pd
import datetime
from datetime import datetime
from dateutil import tz
import time
import sys
import os

from queue import Queue
from threading import Thread
from library.utility import *
#%% https://yourbittorrent.com/?q=Tangled.The.Series.S02E09
import requests
import re
import datetime
def urlsource(url):
    r = requests.get(url)
    return r.text
#%% Google Sheet

class syncvals(Thread): 
    def __init__(self, ID):
        super().__init__()
        # If modifying these scopes, delete the file token.json.
        self.SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
        
        # The ID and range of a sample spreadsheet.
        self.SPREADSHEET_ID = ID
        self.VALUE_INPUT_OPTION = 'USER_ENTERED'
        self.INSERT_DATA_OPTION = 'INSERT_ROWS'
#        self.SHEET_ID = 'DATE'
        self.RANGE_NAME = '%s!A1'   
        
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', self.SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('sheets', 'v4', http=creds.authorize(Http()))
        
        # general params        
        self.index = 'Time'
        self.col = 11
        self.sheets, self.tabs = self.gettabsheets()
        
        # input params
        self.accounts = None
        self.syncs = None
        
        self.append('Global', None)
        
    def gettabsheets(self):  
        # Extract aminenames into dict
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId = self.SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        tabs = []
        for sheet in sheets:
            tab = sheet.get("properties", {}).get("title", "Sheet1")
            sheet_id = sheet.get("properties", {}).get("sheetId", 0) 
            tabs.append(tab)
        sheets = {}
        for tab in tabs:
            RANGE_NAME = '%s!A1:BN'%tab
            result = self.service.spreadsheets().values().get(spreadsheetId = self.SPREADSHEET_ID, range = RANGE_NAME).execute()
            sheets[tab] = result.get('values', [])
        return sheets, tabs

    def add_sheet(self, sheetname, columnCount):
        body = {
            'requests': [{
                    'addSheet': {
                            "properties": {    
                                    "title": sheetname,
                                    "gridProperties":  {
                                                        "rowCount": 1,
                                                        "columnCount": columnCount
                                                      },                   
                               }
                        }
            }]
        }
        batch_update_response = self.service.spreadsheets() \
            .batchUpdate(spreadsheetId = self.SPREADSHEET_ID, body = body).execute()
            
    def update_titles(self, sheetname, *titles):
        values = [
            [
                *titles# Cell values ...
            ],
            # Additional rows
        ]
        data = [
            {
                'range': self.RANGE_NAME%sheetname,
                'values': values
            },
            # Additional ranges to update ...
        ]
        body = {
            'valueInputOption': self.VALUE_INPUT_OPTION,
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId = self.SPREADSHEET_ID, body = body).execute()
    #    print('{0} cells updated.'.format(result.get('updatedCells')))
    def loadsheets(self):
        return self.sheets
    def loadtabs(self):
        return self.tabs
    def loadtabsheets(self):
        return self.tabs, self.sheets
    def addtab(self, tab):
        if tab not in self.tabs:
#            xprint ('tab is not exist...')
            self.add_sheet(tab, self.col)
            self.update_titles(tab, 'Order#', 'Time', 'Code', 'BuySell', 'Qty', 'Price', 'Close', 'High', 'Low', 'HS50+', 'HS50-')
            self.sheets, self.tabs = self.gettabsheets()
#        else:
#            xprint ('tab exists.')
            
#    def formatting(self, tab):
#        myRange = {
#            'sheetId': 210146726,
##            'startRowIndex': 5,
##            'endRowIndex': 8,
#            'startColumnIndex': 1,
##            'endColumnIndex': 2,
#        }
#        
#        reqs = [
#                
### Green fill with dark green text.
##format_big_rise = workbook.add_format({'bg_color': '#00FF00'})
##format_middle_rise = workbook.add_format({'bg_color': '#00EE00'})
##format_small_rise = workbook.add_format({'bg_color': '#ADFF2F'})
### Light red fill with dark red text.
##format_big_drop = workbook.add_format({'bg_color': '#FF0000'})
##format_middle_drop = workbook.add_format({'bg_color': '#FF4500'})
##format_small_drop = workbook.add_format({'bg_color': '#FF6A6A'})
##
##worksheet.conditional_format('C2:CJ6552', {'type':     'formula',
##                                        'criteria': '=AND((C2 - C1) / C1 > 0.01, (C2 - C1) / C1 <= 0.05)',
##                                        'format':   format_small_rise})
##worksheet.conditional_format('C2:CJ6552', {'type':     'formula',
##                                        'criteria': '=AND((C2 - C1) / C1 > 0.05, (C2 - C1) / C1 <= 0.10)',
##                                        'format':   format_middle_rise})
##worksheet.conditional_format('C2:CJ6552', {'type':     'formula',
##                                        'criteria': '=AND((C2 - C1) / C1 > 0.10)',
##                                        'format':   format_big_rise})
###    
##worksheet.conditional_format('C2:CJ6552', {'type':     'formula',
##                                        'criteria': '=AND((C1 - C2) / C1 > 0.01, (C1 - C2) / C1 <= 0.05)',
##                                        'format':   format_small_drop})
##worksheet.conditional_format('C2:CJ6552', {'type':     'formula',
##                                        'criteria': '=AND((C1 - C2) / C1 > 0.05, (C1 - C2) / C1 <= 0.10)',
##                                        'format':   format_middle_drop})
##worksheet.conditional_format('C2:CJ6552', {'type':     'formula',
##                                        'criteria': '=AND((C1 - C2) / C1 > 0.10)',
##                                        'format':   format_big_drop})
#                
#            {'addConditionalFormatRule': {
#                'index': 0,
#                'rule': {
#                    'ranges': [ myRange ],
#                    'booleanRule': {
#                        'format': {
#                                'backgroundColor': {'red': 1, 'green': 1, 'blue': 1}
#                        },
#                        'condition': {
#                            'type': 'CUSTOM_FORMULA',
#                            'values':
#                                [{'userEnteredValue': '= AND((B5 - B6) / B5 <= 0.01, (B6 - B5) / B5 <= 0.01)'}]
#                                
#                        },
#                    },
#                },
#            }},  
#            {'addConditionalFormatRule': {
#                'index': 0,
#                'rule': {
#                    'ranges': [ myRange ],
#                    'booleanRule': {
#                        'format': {
#                                'backgroundColor': {'red': 1, 'green': 0.67, 'blue': 0.18}
#                        },
#                        'condition': {
#                            'type': 'CUSTOM_FORMULA',
#                            'values':
#                                [{'userEnteredValue': '= AND((B6 - B5) / B5 > 0.01, (B6 - B5) / B5 <= 0.05)'}]
#                                
#                        },
#                    },
#                },
#            }},
#            {'addConditionalFormatRule': {
#                'index': 0,
#                'rule': {
#                    'ranges': [ myRange ],
#                    'booleanRule': {
#                        'format': {
#                                'backgroundColor': {'red': 0.93, 'green': 0, 'blue': 0}
#                        },
#                        'condition': {
#                            'type': 'CUSTOM_FORMULA',
#                            'values':
#                                [{'userEnteredValue': '= AND((B6 - B5) / B5 > 0.01, (B6 - B5) / B5 <= 0.10)'}]
#                                
#                        },
#                    },
#                },
#            }},
#            {'addConditionalFormatRule': {
#                'index': 0,
#                'rule': {
#                    'ranges': [ myRange ],
#                    'booleanRule': {
#                        'format': {
#                                'backgroundColor': {'red': 1, 'green': 0, 'blue': 0}
#                        },
#                        'condition': {
#                            'type': 'CUSTOM_FORMULA',
#                            'values':
#                                [{'userEnteredValue': '= (B6 - B5) / B5 > 0.1'}]
#                                
#                        },
#                    },
#                },
#            }},
#        ]
#        
#        self.service.spreadsheets().batchUpdate(spreadsheetId=self.SPREADSHEET_ID,
#                body={'requests': reqs}).execute()
            
    def append(self, sheetname, data):#*data):
        values = [
            data
#            [
#                data# Cell values ...
#            ],
            # Additional rows ...
        ]
        body = {
            'values': values
        }
        result = self.service.spreadsheets().values().append(
            spreadsheetId = self.SPREADSHEET_ID, 
            range = self.RANGE_NAME%sheetname,
            valueInputOption = self.VALUE_INPUT_OPTION, 
            insertDataOption = self.INSERT_DATA_OPTION, 
            body = body
            ).execute()
    
    def cycle(self):    
        try:
            account = None
#            accounts = params['accounts']                
#            for code, acc_info in accounts.items():
            for code, acc_info in self.accounts.items():
                account = acc_info.ClientId.decode()
            self.addtab(account)            
#            syncs = params['sync']
            sheets, tabs = self.gettabsheets()
#            for key, sync in syncs.items():         
            for key, sync in self.syncs.items():
#                print (key, sheets[account].keys(), key not in sheets[account].keys(), key not in sheets[account])
                if key not in sheets[account]:
#                        print (*sync)
                    self.append(account, *sync)
        except Exception as e:
#                print (e)
            pass
        
    def run(self):
        """
        Run is the main-function in the new thread. Here we overwrite run
        inherited from threading.Thread.
        """
#        self.status = True
#        while self.status:
#            self.cycle()
#            time.sleep(60)          # optional heartbeat
        
        self.sheets, self.tabs = self.gettabsheets()
        
            
    def stop(self):
        self.status = False
        Thread.join(self, None)
        
    # Report Params
    def setparams(self, name, val):
        if name == 'accounts':
            self.accounts = val
        if name == 'syncs':
            self.syncs = val
        return None
    
def marketsync():    
    xprint ('Uploading Market Data...')
    #%%
    quotes = {
                'BTCUSD=X',
                'CL=F',
                'PL=F',
                'GC=F',            
                '^IRX',
                '^FVX',
                '^TNX',
                '^TYX',
                'EUR=X',
                'GBP=X',
                'CNY=X',
                'HKD=X',
                'JPY=X',
                'AUD=X',
                'BRL=X',
                'MYR=X',
                'IDR=X',         
                'INR=X',
                '^HSIL',#'VHSI',
                '^VIX',        
                
                '^KLSE',             
                '^FTSE',
                }
    #https://finance.yahoo.com/quote/GC=F            
                
    indices = {            
                '^DJI',
                '^IXIC',
                '^RUT',     
                '^GDAXI',
                '^FCHI',
                '^GSPC',
                '000001.SS',
                '^HSI',            
                '^N225',            
                '^AXJO',            
                '^BVSP',   
                '^BSESN',           
                '^JKSE',         
                }
    #https://finance.yahoo.com/quote/%5EHSI/history?p=%5EHSI   
    #
    others = {
                'MLL', 
                'CCL', 
                'EFFR',
                'LIBOR',
                'EURBOR',
                'SHIBOR',
                'HIBOR',
                'SPCS20RSA',
                'CSUSHPINSA',
                }
    
    info = {}
    limit = 10
    #%%
    #print (datetime.datetime.now().date() - datetime.timedelta(days = 1))
    for quote in quotes:
        print (quote)
        retry = 0
        while quote not in info and retry < limit:
            retry = retry + 1
            source = urlsource('https://finance.yahoo.com/quote/%s/'%(quote))
            #quote_tempplate = r'''summaryDetail\":{\"previousClose\":{\"raw\":(\d+.*\d*),\"fmt":\"\S+\"},"regularMarketOpen'''
            quote_tempplate = r'''summaryDetail\":\{\"previousClose\":{\"raw\":(\d+[\d.]*),\"fmt":\"\S+\"},"regularMarketOpen'''
            
            #quote_tempplate = r'''regularMarketTime\":{\"raw\":(/d+)'''#,\"fmt\":\"[\w :]+\"},\"fiftyTwoWeekRange\":{\"raw\":\"[\d .-]+\",\"fmt\":\"[\d .,-]+\"},\"regularMarketDayHigh\":{\"raw\":[\d.-]+,\"fmt\":\"[\d.,-]+\"},\"shortName\":\"[\w\\]+\",\"exchangeTimezoneName\":\"[\w\\]+\",\"regularMarketChange\":{\"raw\":0,\"fmt\":\"[\d.]+\"},\"regularMarketPreviousClose\":{\"raw\":([\d.-]+)6711'''
            
            #summaryDetail":{"previousClose":{"raw":18.62,"fmt":"18.62"},"regularMarketOpen
            #summaryDetail":{"previousClose":{"raw":6535.9478,"fmt":"6,535.947754"},"regularMarketOpen
            #summaryDetail":{"previousClose":{"raw":14840,"fmt":"14,840.00"},"regularMarketOpen
            result = re.search(quote_tempplate, source)
            #print (result.group(1), result.group(2))  
            try:
                print (result.group(1))
                info[quote] = result.group(1)
            except Exception as e:
                print (quote, e)
        # retry exceeds limit
        if quote not in info:
            info[quote] = 0
        
    #%%
    #product = '000001.SS'
    #product = '^GSPC'
    history_tempplate = r'''date\":(\d+),\"open\":\d+.*\d*,\"high\":\d+.*\d*,\"low\":\d+.*\d*,\"close\":(\d+.*\d*),\"volume\":(\d+),\"adjclose'''
    history_tempplate = r'''date\":(\d+),\"open\":\d+[\d.]*,\"high\":\d+[\d.]*,\"low\":\d+[\d.]*,\"close\":(\d+[\d.]*),\"volume\":(\d+),\"adjclose'''
    previous_date = datetime.datetime.now().date() - datetime.timedelta(days = 1)
    print (previous_date)
    for indice in indices:
        print (indice)
        retry = 0
        while indice not in info and retry < limit:
            retry = retry + 1
            source = urlsource('https://finance.yahoo.com/quote/%s/history?p=%s'%(indice, indice))
            #"date":1537407000,"open":2732.169921875,"high":2743.965087890625,"low":2724.083984375,"close":2729.243896484375,"volume":111400,"adjclose":2729.243896484375}
            results = re.findall(history_tempplate, source)
        #    for result in results:
        #        print (datetime.datetime.fromtimestamp(int(result[0])).date(), result[1:])
        #    if datetime.datetime.fromtimestamp(int(results[0][0])).date() <= previous_date:
            try:
                info[indice] = results[0][1:]
                print (indice, info[indice])
            except Exception as e:
                print (indice, e)
        # retry exceeds limit
        if indice not in info:
            info[indice] = 0
        
    #%%
    #CCL
    #http://www1.centadata.com/cci/cci_e.htm    
    CCL_Date_tempplate = r'''from (\d+/\d+/\d+) to (\d+/\d+/\d+)'''
    CCL_Price_tempplate = r'''Centa-City Leading Index]</b></font></td>\s+<td bgcolor="#ffdbdb" height="1" nowrap="nowrap" width="165">\s+<font color="black" size="3"><center>\s+<p>(\d+[\d.]*)</p></center></font></td>'''
    retry = 0
    while 'CCL' not in info and retry < limit:
        retry = retry + 1
        source = urlsource('http://www1.centadata.com/cci/cci_e.htm')        
        result = re.search(CCL_Date_tempplate, source)
        print (result.group(1))
        result = re.search(CCL_Price_tempplate, source)
        try:
            print (result.group(1))
            info['CCL'] = result.group(1)
        except Exception as e:
            print ('CCL', e)
    # retry exceeds limit
    if 'CCL' not in info:
        info['CCL'] = 0
    #%%
    #MLL
    #https://wws.midland.com.hk/mpp/data/mr_market_index    
    MLL_template = r'''m_date\": \"(\d+-\d+-\d+)\",\s+\"mr_index\": (\d+[\d.]*)'''
    retry = 0
    while 'MLL' not in info and retry < limit:
        retry = retry + 1
        source = urlsource('https://wws.midland.com.hk/mpp/data/mr_market_index')
        results = re.findall(MLL_template, source)
        print (datetime.datetime.now().date())
        for result in results:
            print (result[0], result[1])
        try:
            info['MLL'] = results[-1][1]
            print (info['MLL'])
        except Exception as e:
            print ('MLL', e)
    # retry exceeds limit
    if 'MLL' not in info:
        info['MLL'] = 0
    #%%
    #EFFR
    #https://apps.newyorkfed.org/markets/autorates/fed%20funds    
    EFFR_template = r'''<td class=\"dirColLTight\" align=\"left\" width=\"40\">\s+(\d+/\d+)<sup class=\"paraNotes-markets\"></sup>\s+</td>\s+<td class=\"dirColTight numData\" align=\"right\" width=\"50\">\s+(-*\d+[\d.]*)<br />'''
    retry = 0
    while 'EFFR' not in info and retry < limit:
        retry = retry + 1
        source = urlsource('https://apps.newyorkfed.org/markets/autorates/fed%20funds')
        results = re.findall(EFFR_template, source)
        print (datetime.datetime.now().date())
        for result in results:
            print (result[0], result[1])
        try:
            info['EFFR'] = results[0][1]
            print (info['EFFR'])
        except Exception as e:
            print ('EFFR', e)
    # retry exceeds limit
    if 'EFFR' not in info:
        info['EFFR'] = 0
    #%%
    #LIBOR
    LIBOR_Date_template = r'''lbl_hdr\d+\">(\d+-\d+-\d+)'''
    LIBOR_Price_template = r'''3 months</a></td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>'''
    retry = 0
    while 'LIBOR' not in info and retry < limit:
        retry = retry + 1
        #https://www.global-rates.com/interest-rates/libor/american-dollar/american-dollar.aspx
        source = urlsource('https://www.global-rates.com/interest-rates/libor/american-dollar/american-dollar.aspx')
        results = re.findall(LIBOR_Date_template, source)
        print (datetime.datetime.now().date())
        for result in results:
            print (result)
        result = re.search(LIBOR_Price_template, source)
        try:
            print (result.group(1), result.group(2), result.group(3), result.group(4), result.group(5))
            info['LIBOR'] = result.group(1)
            print (info['LIBOR'])
        except Exception as e:
            print ('LIBOR', e)
    # retry exceeds limit
    if 'LIBOR' not in info:
        info['LIBOR'] = 0
        
    #%%
    #EURBOR
    #https://www.global-rates.com/interest-rates/euribor/euribor.aspx
    EURBOR_Date_template = r'''lbl_hdr\d+\">(\d+-\d+-\d+)'''
    EURBOR_Price_template = r'''3 months</a></td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>\s+<td align="center">(-*\d+[\d.]*)&nbsp;%</td>'''    
    retry = 0
    while 'EURBOR' not in info and retry < limit:
        retry = retry + 1
        try:
            source = urlsource('https://www.global-rates.com/interest-rates/euribor/euribor.aspx')
            results = re.findall(EURBOR_Date_template, source)
            print (datetime.datetime.now().date())
            for result in results:
                print (result)
            result = re.search(EURBOR_Price_template, source)
            print (result.group(1), result.group(2), result.group(3), result.group(4), result.group(5))
            info['EURBOR'] = result.group(1)
            print (info['EURBOR'])
        except Exception as e:
            print ('EURBOR', e)
    # retry exceeds limit
    if 'EURBOR' not in info:
        info['EURBOR'] = 0
    #%%
    #SHIBOR
    #http://www.shibor.org/shibor/web/html/shibor_e.html
    SHIBOR_Date_template = r'''class="infoTitleW" nowrap>(\d+-\d+-\d+)'''
    SHIBOR_Price_template = r'''3M</font></a></td>\s+<td width="30%" align="center">(-*\d+[\d.]*)</td>'''
    retry = 0
    while 'SHIBOR' not in info and retry < limit:
        retry = retry + 1
        try:
            source = urlsource('http://www.shibor.org/shibor/web/html/shibor_e.html')
            result = re.search(SHIBOR_Date_template, source)
            print (result.group(1))
            result = re.search(SHIBOR_Price_template, source)
            print (result.group(1))
            info['SHIBOR'] = result.group(1)
            print (info['SHIBOR'])
        except Exception as e:
            print ('SHIBOR', e)
    # retry exceeds limit
    if 'SHIBOR' not in info:
        info['SHIBOR'] = 0
    #%%
    #HIBOR
    #http://www.hkab.org.hk/hibor/listRates.do?lang=en&Submit=Detail
    #https://www.hangseng.com/en-hk/personal/mortgages/reference-rate/historical-hibor/
    HIBOR_Date_template = r'''Hong Kong Time on\s+<B>(\d+/\d+/\d+)</B>'''
    HIBOR_Price_template = r'''3 Months</TD>\s+<TD align=middle>(-*\d+[\d.]*)'''
    retry = 0
    while 'HIBOR' not in info and retry < limit:
        retry = retry + 1
        try:
            source = urlsource('http://www.hkab.org.hk/hibor/listRates.do?lang=en&Submit=Detail')
            result = re.search(HIBOR_Date_template, source)
            print (result.group(1))
            result = re.search(HIBOR_Price_template, source)
            print (result.group(1))
            info['HIBOR'] = result.group(1)
            print (info['HIBOR'])
        except Exception as e:
            print ('HIBOR', e)
    # retry exceeds limit
    if 'HIBOR' not in info:
        info['HIBOR'] = 0
    #%%
    #'SPCS20RSA',
    #'CSUSHPINSA',
    #https://us.spindices.com/indices/real-estate/sp-corelogic-case-shiller-us-national-home-price-nsa-index
    CSUSHPINSA_Date_template = r'''EDT\",\"formattedDateForWidget\":\"(\w+ \d+)'''
    CSUSHPINSA_Price_template = r'''<h4><span>([\w\s\/\&\-]+)</span></h4>\s+<div>\s+<p class=\"data dark\">\s+(-*\d+[\d.]*)'''
    retry = 0
    while 'CSUSHPINSA' not in info and retry < limit:
        retry = retry + 1
        source = urlsource('https://us.spindices.com/indices/real-estate/sp-corelogic-case-shiller-us-national-home-price-nsa-index')
        try:
            results = re.findall(CSUSHPINSA_Date_template, source)
            print (datetime.datetime.now().date())
            for result in results:
                print (result)
            results = re.findall(CSUSHPINSA_Price_template, source)
            print (datetime.datetime.now().date())
            for result in results:
                print (result)
            
            info['CSUSHPINSA'] = results[3][1]
            print (info['CSUSHPINSA'])
        except Exception as e:
            print ('CSUSHPINSA', e)
    # retry exceeds limit
    if 'CSUSHPINSA' not in info:
        info['CSUSHPINSA'] = 0
    #%%
    uploadvals = syncvals('12RZ1_c-Zrxt9atg7-Km6BgByyxnYXOsvyr0Erj6OMLM')
    sheets = uploadvals.sheets
    tabs = uploadvals.tabs
    uploadvals.append(
            'Global', 
            [
            str(previous_date.strftime('%d/%m/%Y')),
            info['BTCUSD=X'],
            0,
            info['CL=F'],
            0,
            info['PL=F'],
            0,
            info['GC=F'],
            0,
            info['^IRX'],
            info['^FVX'],
            info['^TNX'],
            info['^TYX'],
            info['EFFR'],
            0,
            info['CSUSHPINSA'],
            info['^VIX'],
            info['^DJI'][0],
            info['^DJI'][1],
            info['^IXIC'][0],
            info['^IXIC'][1],
            info['^RUT'][0],
            info['^RUT'][1],
            info['EUR=X'],
            info['EURBOR'],
            info['^FTSE'],
            0,
            info['^GDAXI'][0],
            info['^GDAXI'][1],
            info['^FCHI'][0],
            info['^FCHI'][1],
            info['GBP=X'],
            info['LIBOR'],
            info['^GSPC'][0],
            info['^GSPC'][1],
            info['HKD=X'],
            info['HIBOR'],
            info['CCL'],
            info['MLL'],
            info['^HSIL'],
            info['^HSI'][0],
            info['^HSI'][1],
            info['CNY=X'],
            info['SHIBOR'],
            info['000001.SS'][0],
            info['000001.SS'][1],
            info['JPY=X'],
            info['^N225'][0],
            info['^N225'][1],
            info['AUD=X'],
            info['^AXJO'][0],
            info['^AXJO'][1],
            info['BRL=X'],
            info['^BVSP'][0],
            info['^BVSP'][1],
            info['INR=X'],
            info['^BSESN'][0],
            info['^BSESN'][1],
            info['MYR=X'],
            info['^KLSE'],
            0,
            info['IDR=X'],
            info['^JKSE'][0],
            info['^JKSE'][1],
            ]
            )    
    xprint ('Uploaded Market Data...')
#%%