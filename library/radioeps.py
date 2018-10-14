# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 13:52:29 2018

http://bbs.cantonese.asia/forum-118-1.html
881 881 十八樓C座  2018-08-27
881 光明頂  2018-08-27
@author: SF
"""
import os
import sys
import time
import re
import pandas
import base64

import zipfile
import shutil

from ffmpy import FFmpeg   

from library.utility import *
from library.youtubes import *
from library.endecrytion import *
#%%
pydir = os.getcwd() + '\\'

radiocodes = ['十八樓C座', '光明頂']
zipsuffixes = {
        '十八樓C座'    : '-1230-1300.zip',
        '光明頂'       : '-2300-0000.zip',
        }

RadioProcesses = {}
rplist = [
        'radioconv',
        'radiounziprename',
        'radioul',
        'radiodl',
        ]
rpstatus = {
        }
def setrpstatus(name, status):
    if name in rpstatus:
        rpstatus[name] = status
    return 0
def getrpstatus(name):
    if name in rpstatus:
        return rpstatus[name]
    return None
#%%            
def radiounziprename():
    print ('Radio Unzip and Rename Process...')
    # Parameters
    radiostitles = {
        '1300.wma' : '18F.Block.C.',
        '0000.mp3' : 'Summit.',
        }
    # browse all files
    zfiles = os.listdir('.')
    time.sleep(3)
    # loop target radio codes
    for radiocode in radiocodes:
        # loop through all zip file
        for zfile in zfiles:
            # radio code at suffix
            if zfile.endswith(zipsuffixes[radiocode]):
                # Unzip the file folder
                zref = zipfile.ZipFile(zfile, 'r')
                zref.extractall()
                zref.close()
                # del the zip file
                try:
                    os.remove(zfile)
                except Exception as e:
                    print (e)
                # Move and Del
                radiofilespath = zfile.replace('.zip', '') + '\\'
                radiofiles = os.listdir(radiofilespath)
                for radiofile in radiofiles:
                    # prepare suitable name
                    string = radiofile.split('-')
                    title = radiostitles[string[-1]]
                    date = string[1][:4] + '-' + string[1][4:6] + '-' + string[1][6:]   
                    newname = title + date + radiofile[-4:]
                    # Rename and move, otherwise, del if exists
                    try:
                        os.rename(radiofilespath + radiofile, radiofilespath + newname)                        
                        shutil.move(radiofilespath + newname, pydir)
                    except Exception as e:
                        print (e)
                        os.remove(radiofilespath + newname)  
                # del the unzip folder
                try:
                    shutil.rmtree(radiofilespath)
                except Exception as e:
                    print (e)
#%%
def radioul():    
    xprint ('Radio Upload Process...')
    # load playlist from youtube
    try:
        playlist = listvdos()
        print ('playlist is avaioable...')
    except Exception as e:
        print (e)
        return
# Upload mp4 to youtube
    files = os.listdir('.')
    for file in files:
        # focus on mp4 file for youtube
        if file.endswith('.mp4'):
            # see if it is not in youtube
            if file not in playlist:
                # start to upload
                try:
                    uploadvdo(['--file=%s'%(file), '--title=%s'%(file)])
                except Exception as e:
                    print (e)
            else:
                print ('%s exists in Youtube.'%file)            
            # remove no matter what
            try:
                os.remove(file)
            except Exception as e:
                print (e)
#        else:
#            print ('No mp4 files...')
    # Remove oauth json
    files = os.listdir(".")
    for file in files:
        if file.startswith('--file=') and file.endswith('-oauth2.json'):
            try:
                os.remove(file)
            except Exception as e:
                print (e)         
#%%
def radioconv():        
    print ('Radio Conversion Process...')
    # initialize upload process if not exist
    global RadioProcesses
    if 'radioul' not in RadioProcesses:
        RadioProcesses['radioul'] = HomeProcess(radioul, datetime.time(16, 0, 0), 3600 * 6)
    radiounziprename()
    # Convert mp3 to x2 mp3
    files = os.listdir('.')
    for file in files:
        # see if Summit file exists but not the x2 version
        if file.startswith('Summit.') and file.endswith('.mp3') and not file.endswith('x2.mp3'):
            #for %a in (Summit.*.mp3) do ffmpeg -i %a -filter:a "atempo=2.0" %a".mp3"           
            string = file.split('-')
            ff = FFmpeg(
                    inputs={file: None},
                    outputs={file[:-4] +'x2.mp3': '-filter:a \"atempo=2.0\"'}
                    )
            ff.cmd            
            try:
                ff.run()
            except Exception as e:
                print (e)
            # move x1 version to destination
            try:
                shutil.move(file, '\\\\GBE_NAS\\music')
            except Exception as e:
                print (e)
            # remove x1 version if exist
            try:
                os.remove(file)
            except Exception as e:
                print (e)
    # Convert wma to mp3
    files = os.listdir('.')
    for file in files:
        # search for wma (18 block C) file
        if file.endswith('.wma'):
            #for %a in (*.wma) do ffmpeg -i %a -ab 32 %a".mp3"  
            ff = FFmpeg(
                    inputs={file: None},
                    outputs={file[:-4] +'.mp3': '-ab 32'}
                    )
            ff.cmd
            try:
                ff.run()
            except Exception as e:
                print (e)
            # remove the file after conversion
            try:
                os.remove(file)
            except Exception as e:
                print (e)
    # Convert mp3 to mp4
    files = os.listdir('.')
    for file in files:
        if file.endswith('.mp3'):
#            #for %a in (*.mp3) do "ffmpeg" -loop 1 -r 1 -i "image.jpg" -vcodec mpeg4 -i %a -shortest -acodec copy %a".mp4"
            ff = FFmpeg(
                    inputs={'image.jpg': '-loop 1 -r 1', file: '-vcodec mpeg4'},
                    outputs={file[:-4] +'.mp4': '-shortest -acodec copy'}
                    )
            ff.cmd
            try:
                ff.run()
            except Exception as e:
                print (e)
            # remove the file after conversion
            try:
                os.remove(file)
            except Exception as e:
                print (e)
#%%
def radiodl():
    print ('Radio Download Process...')
    # initialize File conversion process if not exist
    global RadioProcesses    
    if 'radioconv' not in RadioProcesses:
        RadioProcesses['radioconv'] = HomeProcess(radioconv, datetime.time(15, 0, 0), 3600 * 6)
    # initialize parameters
    hostname = 'http://' + decrypt('ggx.hfsytsjxj.fxnf/')
    topic = 'forum-118-1.html'
    urlcode = urlsource(hostname + topic)
    
    topictemplate = r'''a href=\"(\S+)\" onclick=\"atarget\(this\)\" class=\"s xst\">\w+\s+%s\s+(\w+)-(\w+)-(\w+)</a>'''
    posttemplate = r'''<a href=\"(https://u\d+.pipipan.com/fs/\d+-\d+)\"'''
    
    code2list = {
            '十八樓C座': '18F.Block.C.', 
            '光明頂'   : 'Summit.',
                 }        
    # load playlist from youtube
    try:
        playlist = listvdos()
        print ('playlist is avaioable...')
    except Exception as e:
        print (e)
        return    
    # Initialize source address and matches    
    matches = {}
    # loop target radio codes
    for radiocode in radiocodes:
        # find all matches on radio codes
        matches[radiocode] = re.findall(topictemplate%radiocode, urlcode)
        # Retrieve link and datetime from matches
        radioposts = {}
        # loop matches per code
        for match in matches[radiocode]:
            # check if radio ep exists in youtube
            ep = (code2list[radiocode] + '-'.join(match[1:4]) + '.mp4')
            # if ep exists in youtube or its file exists
            if (ep not in playlist) or any((file.endswith(zipsuffixes[radiocode]) and (''.join(match[1:4]) in file)) for file in os.listdir('.')):
                # launch explorer
                explorer = Chrome()
                print ('Downloading %s'%ep)
                # search the link from the page
                postlink = re.search(posttemplate, urlsource(match[0])).group(1)
                # browse the extracted link
                explorer.browse(postlink)
                # click the link
                explorer.click_by_id('''free_down_link''')
                # wait until file exists
                while not any((file.endswith(zipsuffixes[radiocode]) and (''.join(match[1:4]) in file)) for file in os.listdir('.')): pass
                print ('%s File Found...'%ep)
                # close the explorer
                explorer.kill()     
    # Delete Unconfirmed....crdownload files if any
    files = os.listdir('.')
    for file in files:
        if file.startswith('Unconfirmed ') and file.endswith('.crdownload'):      
            try:
                os.remove(file)   
            except Exception as e:
                print (e)
#%%
def radioeps(youtubeacc):
    try:        
        setyoutubeacc(youtubeacc)
        print ('Selected Youtube Account.')
    except Exception as e:
        print (e)
        return
        
    global RadioProcesses
    if 'radiodl' not in RadioProcesses:
        RadioProcesses['radiodl'] = HomeProcess(radiodl, datetime.time(13, 0, 0), 3600 * 6)