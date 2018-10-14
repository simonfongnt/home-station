# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 09:29:39 2018

@author: SF
https://global.download.synology.com/download/Document/DeveloperGuide/Synology_Download_Station_Web_API.pdf

nas.application.service.request(method, [params])

video/TEMPERORY
"""
#%%
import sys
from library.utility import *
from library.aminebt import *
from library.radioeps import *
from library.market import *
#%% 
def initHome(args):
    HomeProcesses = {}
#    HomeProcesses['aminebt'] = HomeProcess(aminebt, datetime.time(0, 0, 0), 1800, filename)
    HomeProcesses['aminebt'] = HomeProcess(aminebt, datetime.time(0, 0, 0), 3600 * 4, SPREADSHEET_ID)
    HomeProcesses['radioeps'] = HomeProcess(radioeps, datetime.time(0, 0, 0), 3600 * 24, args[1])
    HomeProcesses['marketsync'] = HomeProcess(marketsync, datetime.time(7, 0, 0), 3600 * 24)
    return HomeProcesses
#%%
def startHome(HomeProcesses):
    for key, func in HomeProcesses.items():
        func.start()
    return HomeProcesses
#%%
def stopHome(HomeProcesses):
    for key, func in HomeProcesses.items():
        func.stop()
    return HomeProcesses
#%%
def main():
    
    HomeProcesses = initHome(sys.argv)    
    while True:
        command = input()
        if command == 'killall':
            HomeProcesses = stopHome(HomeProcesses)
        elif command == 'runall':
            HomeProcesses = startHome(HomeProcesses)
        elif command == 'bye' or command == 'exit':
            HomeProcesses = stopHome(HomeProcesses)
            return 0
    
#%%
if __name__ == '__main__':
  main()
#xlsx = main()
  