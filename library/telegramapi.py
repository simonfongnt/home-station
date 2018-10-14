# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 11:02:54 2018

@author: SF
"""
##%%
#import telegram
#    def sendmsg(self, update_id, text):
#        msg = {  'update_id': 330416137, 
#                 'message': {
#                         'message_id': 39, 
#                         'date': 1538046002, 
#    #                     'chat': {
#    #                             'id': -284208650, 'type': 'group', 'title': 'testing', 'all_members_are_administrators': True
#    #                             }, 
#                         'text': 'hi', 
#                         'entities': [], 
#                         'caption_entities': [], 
#                         'photo': [], 
#                         'new_chat_members': [], 
#                         'new_chat_photo': [], 
#                         'delete_chat_photo': False, 
#                         'group_chat_created': False, 
#                         'supergroup_chat_created': False, 
#                         'channel_chat_created': False, 
#                         'from': {
#                                 'id': 691417373, 
#                                 'first_name': 'Simon', 
#                                 'is_bot': False, 
#                                 'language_code': 'en-us'}
#                         }
#                }    
# billy lau: 693508146

#{'message_id': 408, 
# 'date': 1538107009, 
# 'chat': {
#         'id': -309118685, 
#         'type': 'group', 
#         'title': 'constituents', 
#         'all_members_are_administrators': True
#         }, 
# 'text': '/resume@constituentsBot', 
# 'entities': [
#         {'type': 'bot_command', 
#          'offset':0, 'length': 23
#          }
#         ], 
# 'caption_entities': [], 
# 'photo': [], 
# 'new_chat_members': [],
# 'new_chat_photo': [], 
# 'delete_chat_photo': False, 
# 'group_chat_created': False, 
# 'supergroup_chat_created': False, 
# 'channel_chat_created': False, 
# 'from': {
#         'id': 691417373, 
#         'first_name': 'Simon', 
#         'is_bot': False, 
#         'language_code': 'zh-TW'
#         }
# }
#%%
#import logging
import telegram
from telegram.error import NetworkError, Unauthorized
import time
from threading import Thread
import datetime
import pandas as pd
import re
#%% Telegram API
class telegramobject(Thread):
    
    def __init__(self, cmd_queues, token, botname, authgp):
        super().__init__()
        self.cmd_queues = cmd_queues
        
        self.update_id = None
        self.authgp = authgp
#        self.authid = [691417373]
        self.TOKEN = token # @constituentsBot
        self.botname = botname
        # Telegram Bot Authorization Token
        self.bot = telegram.Bot(self.TOKEN)
    
        # get the first pending update_id, this is so we can skip over it in case
        # we get an "Unauthorized" exception.
        try:
            self.update_id = self.bot.get_updates()[0].update_id
        except IndexError:
            self.update_id = None
    
#        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
    def listen(self):
        """Echo the message the user sent."""
#        global update_id
        # Request updates after the last update_id
        for update in self.bot.get_updates(offset = self.update_id, timeout=10):
            self.update_id = update.update_id + 1
#            print (update)
#            print (update.message.chat.id, self.authgp)
#            print (update.message)
            try:
                if update.message.chat.id in self.authgp:
                    self.chat_id = update.message.chat.id
                    input_msg = update.message.text
                    try:
                        # entities exists and type is bot_command 
                        if update.message.entities and update.message.entities[0].type == 'bot_command':
                            input_msg = input_msg[1:-len(self.botname)] # /resume@constituentsBot
                            input_msg = input_msg.split('_')
                        # normal text include urgent commands
                        else: 
                            input_msg = input_msg.split(' ')
        #                print ('msg to telegram: ', update.message.text)
#                        self.cmd_queues['bot'].put(update.message.text.split(' '))
                        self.cmd_queues['bot'].put(input_msg)
                        self.cmd_queues['bot'].join()  # blocks until consumer calls task_done()
                    except Exception as e:
                        print ('invalid command: ', e)
            except Exception as e:
                print (e)
    
    def cycle(self):    
        try:
            self.listen()
        except NetworkError:
            time.sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            self.update_id += 1
        
    def run(self):
        """
        Run is the main-function in the new thread. Here we overwrite run
        inherited from threading.Thread.
        """
        self.status = True
        while self.status:       
#            print ('telegram running...')                
            if self.cmd_queues['telegram'].empty():
#                print ('telegram queue is empty...')
                self.cycle()
                time.sleep(1)                           # optional heartbeat
                
            else:   
#                print ('telegram queue has sth...')
                self.getprompt()
                self.cmd_queues['telegram'].task_done()  # unblocks prompter   
#                print ('telegram task_done')
                
    def stop(self):
        self.status = False
        Thread.join(self, None)
    
    def sendmsg(self, text):
        try:
            self.bot.send_message(chat_id = self.authgp, text = text)
        except Exception as e:
            xprint (e)
        
    def getprompt(self):
        try:
            while not self.cmd_queues['telegram'].empty():
                cmds = self.cmd_queues['telegram'].get()
#                self.bot.send_message(chat_id = self.chat_id, text = cmds)
                self.bot.send_message(chat_id = -309118685, text = cmds)
                
        except Exception as e:
            print(f'Command `{cmds}` is unknown: ', e)
    # Report Params
    def setparams(self, name, val):
        return None