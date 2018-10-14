# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 19:09:19 2018

@author: SF
"""
#%%
from __future__ import print_function
#from googleapiclient import discovery
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
#%%
import threading 
from threading import Event
from threading import Thread
import pandas
import datetime
import time
import requests
from library.endecrytion import *
from library.telegramapi import *
#%%
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
#%%
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1nEajpzv1yOkw9hyP1w4iuehC7A9v3-cS5Ij53EieMEc'
#SPREADSHEET_ID = decrypt('1sjfouea1dtpb9mdu1b4n8jmh7f9a3-hx5no53jnjrjh')
VALUE_INPUT_OPTION = 'USER_ENTERED'
INSERT_DATA_OPTION = 'INSERT_ROWS'
SHEET_ID = 'DATE'
RANGE_NAME = '%s!A1'


"""Shows basic usage of the Sheets API.
Prints values from a sample spreadsheet.
""" 
store = file.Storage("token.json")
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

#%%
def add_sheet(sheetname, columnCount):
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
    batch_update_response = service.spreadsheets() \
        .batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
#%%
STATUS = {
        'FAIL': -1,
        'NONE': 0,
        'RUN': 1,
        'STOP': 2,
        }

#%%

telegrambot = telegramobject(None, '673187479:AAEHrVwTnYhskRj4XRa0wuCF45yApufoQ4A', '@homestation_Bot', -283725883)
def xprint(*text):
    now = datetime.datetime.now()
    print (now.strftime("%Y-%m-%d %H:%M:%S: "), *text)
    # transmit to telegram
    telegrambot.sendmsg(' '.join(str(x) for x in [*text]))

#%% https://yourbittorrent.com/?q=Tangled.The.Series.S02E09
def urlsource(url):
    r = requests.get(url)
    return r.text
#%%
def gettabsheets(filename, index):    
    # if file is excel
    if filename.endswith('.xlsx'):                
        xlsx = pandas.read_excel(filename, None)
        # Extract aminenames into dict
        sheets = {}
        tabs = []
        for tab, sheet in xlsx.items():
            sheets[tab] = sheet
            sheets[tab].set_index(index, inplace=True, drop=True)
            tabs.append(tab)
        return sheets, tabs  
    # file is google sheet
    else:
        # Extract aminenames into dict
        sheet_metadata = service.spreadsheets().get(spreadsheetId=filename).execute()
        sheets = sheet_metadata.get('sheets', '')
        tabs = []
        for sheet in sheets:
            tab = sheet.get("properties", {}).get("title", "Sheet1")
            sheet_id = sheet.get("properties", {}).get("sheetId", 0) 
            tabs.append(tab)
        sheets = {}
        for tab in tabs:
            RANGE_NAME = '%s!A1:B'%tab
            result = service.spreadsheets().values().get(spreadsheetId=filename,
                                                        range=RANGE_NAME).execute()
            # df column name
            header = result.get('values', [])[0]
            # df data
            values = result.get('values', [])[1:]  # Everything else is data.
            all_data = []
            for col_id, col_name in enumerate(header):
                column_data = []
                for row in values:
                    column_data.append(row[col_id])
                ds = pandas.Series(data=column_data, name=col_name)
                all_data.append(ds)
            df = pandas.concat(all_data, axis=1)
            df.set_index(index, inplace=True, drop=True)            
            sheets[tab] = df            
        return sheets, tabs
#%%
def gettabs(filename, index):      
    sheets, tabs = gettabsheets(filename, index)
    return tabs
#%%
def getsheets(filename, index):    
    sheets, tabs = gettabsheets(filename, index)
    return sheets  
#%%
def updatesheets(filename, index, sheets):
    # if file is excel
    temp, aminenames = gettabsheets(filename, index)    
    if filename.endswith('.xlsx'):    
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pandas.ExcelWriter(filename, engine='xlsxwriter')
        for tab, sheet in sheets.items():                    
            sheet.to_excel(writer, sheet_name = tab)
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()    
#        return sheets  
    # file is google sheet
    else:
#    if True:
        data = []
        for tab, sheet in sheets.items():
            values = []
            for index, row in sheet.itertuples():
                values.append([index, row])            
            data.append({
                    'range': '%s!A2:Z'%tab,
                    'values': values
                    })        
        body = {
            'valueInputOption': VALUE_INPUT_OPTION,
            'data': data
        }
        filename = SPREADSHEET_ID
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=filename, body=body).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')));
    return sheets  
#%%
def joinstatusus(filename, index, f_status, *statuses):
    if len(statuses) == 1:
        for key, sheet in f_status.items(): 
            f_status[key] = f_status[key].combine_first(statuses[0][key])
    return updatesheets(filename, index, f_status)
#%%
class Future(object):
    def __init__(self):
        self._ev = Event()

    def set_result(self, result):
        self._result = result
        self._ev.set()

    def set_exception(self, exc):
        self._exc = exc
        self._ev.set()

    def result(self):
        self._ev.wait()
        if hasattr(self, '_exc'):
            raise self._exc
        return self._result
#%%
class HomeProcess(object):
    def __init__(self, function, begin, interval, *args, **kwargs):
        self._timer = None
        self.begin = begin
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
    #    self.next_call = time.time()
        self.next_call = None
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
              if self.next_call is None:
                  now = datetime.datetime.now()
                  self.next_call = datetime.datetime(now.year, now.month, now.day, self.begin.hour, self.begin.minute, 0)
                  if self.next_call < now:
                      self.next_call = datetime.datetime.now() + datetime.timedelta(seconds = 30)
                  self.next_call = self.next_call.timestamp()              
              else:
                  self.next_call += self.interval
              self._timer = threading.Timer(self.next_call - time.time(), self._run)
              self._timer.start()
              self.is_running = True
              print ('%s schedules after %ds '%(self.function.__name__, self.next_call - time.time()))
              
    def reset(self, begin):
        self._timer.cancel()
        self.next_call = None
        self.begin = begin
        self.is_running = False
        self.start()
        
    def stop(self):
        self._timer.cancel()
        self.is_running = False
#%%  
class Chrome():    
    def __init__(self,):
        # Killing until not found
        while (os.system("taskkill /f /im  chrome.exe") != 128): pass
        while (os.system("taskkill /f /im  chromedriver.exe") != 128): pass
        time.sleep(3)
        # Target to .py folder
        self.options = Options()        
        self.options.add_argument("user-data-dir=C:\\Users\\%s\\AppData\\Local\\Google\\Chrome\\User Data"%(os.getlogin()))
        #                options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')                
        #                options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--start-maximized")    
        #                options.add_argument(r('download.default_directory=' + pydir))        
        self.options.add_experimental_option("prefs", {
          "download.default_directory": (os.getcwd() + '\\'),
          "download.prompt_for_download": False,
          "download.directory_upgrade": True,
          "safebrowsing.enabled": True
        })
        self.driver = webdriver.Chrome(chrome_options=self.options)

    def _run(self):
        pass

    def browse(self, link):
        try:
            self.link = link        
            self.driver.get(self.link)
        except Exception as e:
            print (e)

    def click_by_xpath(self, _xpath):
#        while True:
        try:
#            self.driver.find_element_by_xpath(_xpath).click()
            self.element = WebDriverWait(self.driver, 10).until(
                         EC.presence_of_element_located((By.XPATH, _xpath)))
#            self.element.location_once_scrolled_into_view    
            self.driver.execute_script("arguments[0].scrollIntoView();", self.element)        
            actions = webdriver.ActionChains(self.driver)
            actions.move_to_element(self.element).perform()
#            time.sleep(5)
            self.element.click()
#            break
        except Exception as e:
            print (e)
        
    def click_by_id(self, _id):
#        while True:
        try:
#            self.driver.find_element_by_id(_id).click()
            self.element = WebDriverWait(self.driver, 10).until(
                         EC.presence_of_element_located((By.ID, _id)))
#            self.element.location_once_scrolled_into_view    
            self.driver.execute_script("arguments[0].scrollIntoView();", self.element)        
            actions = webdriver.ActionChains(self.driver)
            actions.move_to_element(self.element).perform()
#            time.sleep(5)
            self.element.click()
#            break
        except Exception as e:
            print (e)       
        
    def kill(self):
        try:
#            time.sleep(10)
            self.driver.quit()   
        except Exception as e:
            print (e)