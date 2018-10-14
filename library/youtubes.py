# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 22:47:51 2018

ID:     838411343127-k5fpd3l6o30sl4dgkgq89ssb038t1j7d.apps.googleusercontent.com
secret: sepn5hVC_rPfJob1GIMrFT3d

python upload_video.py --file="a.mp4" --privacyStatus="private"
                       --title="Summer vacation in California"
                       --description="Had fun surfing in Santa Cruz"
                       --keywords="surfing,Santa Cruz"
                       --category="22"

@author: SF
"""

#!/usr/bin/python
import http.client
#import httplib
import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
#from oauth2client.tools import argparser, run_flow
from oauth2client.tools import argparser#, run_flow

from library.tools import run_flow
from library.tools import set_google_account


import argparse
#import os
import re

import google.oauth2.credentials
#import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#from google_auth_oauthlib.flow import InstalledAppFlow

import library.flow
from library.flow import InstalledAppFlow

youtubeacc = None
youtube = None
# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
  http.client.IncompleteRead, http.client.ImproperConnectionState,
  http.client.CannotSendRequest, http.client.CannotSendHeader,
  http.client.ResponseNotReady, http.client.BadStatusLine)
#RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
# user's account, but not other types of account access.
YOUTUBE_LIST_SCOPE = ['https://www.googleapis.com/auth/youtube.readonly']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This OAuth 2.0 access scope allows for read-only access to the authenticated
#API_SERVICE_NAME = 'youtube'
#API_VERSION = 'v3'

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


argparser.add_argument("--file", required=True, help="Video file to upload")
argparser.add_argument("--title", help="Video title", default="Test Title")
argparser.add_argument("--description", help="Video description",
                       default="Test Description")
argparser.add_argument("--category", default="22",
                       help="Numeric video category. " +
                       "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
argparser.add_argument("--keywords", help="Video keywords, comma separated",
                       default="")
argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
                       default=VALID_PRIVACY_STATUSES[1], help="Video privacy status.")

def get_my_uploads_list():
    # Retrieve the contentDetails part of the channel resource for the
    # authenticated user's channel.
    channels_response = youtube.channels().list(
            mine=True,
            part='contentDetails'
            ).execute()


    for channel in channels_response['items']:
        # From the API response, extract the playlist ID that identifies the list
        # of videos uploaded to the authenticated user's channel.
        return channel['contentDetails']['relatedPlaylists']['uploads']

    return None

def list_my_uploaded_videos(uploads_playlist_id):
    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet',
            maxResults=5
            )

#    print ('Videos in list %s' % uploads_playlist_id)
    playlist = []
    i = 20
    while playlistitems_list_request:
#    if playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Print information about each video.
        for playlist_item in playlistitems_list_response['items']:
            title = playlist_item['snippet']['title']
            video_id = playlist_item['snippet']['resourceId']['videoId']
#            print ('%s (%s)' % (title, video_id))
            playlist.append(title)
            i = i - 1
        if i == 0:
            break
        playlistitems_list_request = youtube.playlistItems().list_next(
                playlistitems_list_request, playlistitems_list_response)
    return playlist

def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body=dict(
        snippet=dict(
            title = options.title,
            description = options.description,
            tags = tags,
            categoryId = options.category
        ),
        status = dict(
        privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(part=",".join(body.keys()), body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print ("Uploading file...")
            status, response = insert_request.next_chunk()
            if 'id' in response:
                print ("Video id '%s' was successfully uploaded." % response['id'])
            else:
                exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print (error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print ("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

#def inityoutube():
##if __name__ == '__main__':
#  youtube = get_authenticated_service()
def setyoutubeacc(acc):
    global youtubeacc
    global youtube
    youtubeacc = acc
    if youtube == None:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, YOUTUBE_LIST_SCOPE)
        #credentials = flow.run_console()
        set_google_account(acc)
        flow.set_google_account(acc)   
        credentials = flow.run_local_server()
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials = credentials)

## Authorize the request and store authorization credentials.
#def get_authenticated_service():
#  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, YOUTUBE_LIST_SCOPE)
#  credentials = flow.run_console()
#  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials = credentials)
def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE, message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)
        print ('Google Account Credentials is received.')

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
        
def getyoutubeacc(): 
    return youtubeacc
    
def uploadvdo(args):   
#if __name__ == '__main__':
    sys.argv = args
#    print (sys.argv)    
    args = argparser.parse_args(args)

    if not os.path.exists(args.file):
        exit("Please specify a valid file using the --file= parameter.")
        
    youtube = get_authenticated_service(args)
    
    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

def listvdos():
    playlists = []
    try:
        uploads_playlist_id = get_my_uploads_list()
        if uploads_playlist_id:
#            list_my_uploaded_videos(uploads_playlist_id)
            playlists = list_my_uploaded_videos(uploads_playlist_id)
            return playlists
        else:
            print('There is no uploaded videos playlist for this user.')
            return None
    except HttpError as e:
        print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)) 
        return None
