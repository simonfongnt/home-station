# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 10:41:43 2018

@author: SF
"""

from library.synolopy.devices import *
#import devices
#%%
def dltorrent(link):
    nas = NasApi('http://192.168.0.160:5000/webapi/', 'admin', '74108520')
#    nas.downloadstation.info.request('getinfo')    
#    nas.downloadstation.info.request('getinfo')
#    params = {
#            'method' : 'SetServerConfig',
#            'bt_max_upload': "0",
#              }
#    nas.downloadstation.info.request(**params)
#    params = {
#            'method' : 'list',
#    #        'url': "http://yourbittorrent.com/down/13175291.torrent",
#    #          "destination": "video/TEMPERORY",
#              }
#    nas.downloadstation.task.request(**params)
    params = {
            'method' : 'create',
            'uri': link,
            "destination": "video/TEMPERORY",
              }
    nas.downloadstation.task.request(**params)