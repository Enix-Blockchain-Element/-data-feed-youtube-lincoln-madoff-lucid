import requests
import isodate
import mysql.connector
from mysql.connector import errorcode, Error
import time
import re

# see http://en.wikipedia.org/wiki/ISO_8601#Durations
ISO_8601_period_rx = re.compile(
    'P'   # designates a period
    '(?:(?P<years>\d+)Y)?'   # years
    '(?:(?P<months>\d+)M)?'  # months
    '(?:(?P<weeks>\d+)W)?'   # weeks
    '(?:(?P<days>\d+)D)?'    # days
    '(?:T' # time part must begin with a T
    '(?:(?P<hours>\d+)H)?'   # hourss
    '(?:(?P<minutes>\d+)M)?' # minutes
    '(?:(?P<seconds>\d+)S)?' # seconds
    ')?'   # end of time part
)

# from pprint import pprint
# pprint(ISO_8601_period_rx.match('P1W2DT6H21M32S').groupdict())

def connect_DB():
    config = {
        'user': '',
        'password': '',
        'host': '',
        'database': '',
        'charset': 'utf8mb4'
    }

    cnx = cur = None
    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Something is wrong with your user name or password')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        return (cnx, cur)

def update_newest_video(videoEntry):
    cnx, cur = connect_DB()
    cur = cnx.cursor(buffered=True)

    records = []

    try:
        cur.execute('SELECT * FROM `lincoln_waiting_process` WHERE videoid = \'' + videoEntry['videoID'] + '\'')
        entry = cur.fetchone()

        if entry is None:
            sqlInsert = 'INSERT INTO `lincoln_waiting_process` ' \
                        '(user_id, post_title, videoid, description, post_link, duration)' \
                        'VALUES (1,' + repr(videoEntry['videoTitle']) + ',\''+ videoEntry['videoID'] + '\','\
                        + repr(videoEntry['videoDescription']) + ',\'https://www.youtube.com/watch?v=' + videoEntry['videoID']\
                        + '\',\'' + videoEntry['videoDuration'] + '\')'
            cur.execute(sqlInsert)
            cnx.commit()
            print(sqlInsert)
            # print('+++New entry added+++')
        else:
            print('---Entry is exist.---')

    except Error as error:
        print("ERROR : Column Maybe Exist : {}".format(error))
        pass

    finally:
        cur.close()
        cnx.close()

    return records

def feedLincoin_main():
    ##############################################################################################
    # Google API KEY
    API_KEY = ''
    CLIENT_ID = ''
    CLIENT_SECRET = ''

    ##############################################################################################
    # YOUTUBER CHANNEL ID
    username = "UCV61VqLMr2eIhH4f51PV0gA"
    url = "https://www.youtube.com/channel/"+username+"/videos?view=0&sort=dd&shelf_id=0"

    print("Start Feeding Video link to Lincoln DB")

    page = requests.get(url).content
    data = str(page).split(' ')
    # print(data)
    item = 'href="/watch?'
    # urls = [line.replace('href="', 'youtube.com').replace('"', '') for line in data if item in line] # list of all videos listed twice
    ids = [line.replace('href="/watch?v=', '').replace('"', '') for line in data if item in line] # list of all videos listed twice
    ids = list(dict.fromkeys(ids))
    print(len(ids)) # index the latest video

    for videoID in ids:
        url = "https://www.googleapis.com/youtube/v3/videos?part=contentDetails%2C%20snippet&id="+videoID+"&key="+API_KEY
        video_data = requests.get(url).json()['items'][0]
        videoEntry = {}
        videoEntry['videoID'] = videoID
        videoEntry['videoTitle'] = video_data['snippet']['title']
        videoEntry['videoDescription'] = video_data['snippet']['description']
        videoDuration = ISO_8601_period_rx.match(video_data['contentDetails']['duration']).groupdict()
        videoEntry['videoDuration'] = '{:02}:{:02}:{:02}'.format(int(videoDuration['hours'] if videoDuration['hours'] != None else 0),
                                                                 int(videoDuration['minutes'] if videoDuration['minutes'] != None else 0),
                                                                 int(videoDuration['seconds'] if videoDuration['seconds'] != None else 0))
        update_newest_video(videoEntry)
        time.sleep(1)

    print("End of feed lincoln Process")