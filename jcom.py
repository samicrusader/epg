#!/usr/bin/env python3

import json
import requests
from datetime import datetime
from datetime import timedelta

list_url = 'https://tvguide.myjcom.jp/api/mypage/getEpgChannelList/?channelType={channelType}&area={area}&channelGenre=&course=&chart=&is_adult=true'
epg_url = 'https://tvguide.myjcom.jp/api/getEpgInfo/?channels={channels}&rectime=&rec4k='
channel = '{channelType}_{service_code}_{date}'
datefmt = '%Y%m%d'
programdatefmt = '%Y%m%d%H%M%S'
currentdate = datetime.now()
epg = dict()

# channelType:
## 2 = Terrestial
## 3 = BS Digital
## 120 = Cable
channelTypes = [2, 3, 120]

def grabChannels(area:int, channelTypes:list):
    channels = dict()
    for t in channelTypes:
        req = requests.get(list_url.format(channelType=t, area=area))
        for channel in req.json()['header']:
            channels.update({str(t)+'_'+channel['service_code']: channel['channel_name']})
    return channels

def addEPG(channels:list, days:int):
    for i in range(days+1):
        date = currentdate + timedelta(days=i)
        strdate = date.strftime(datefmt)
        if not strdate in epg.keys():
            epg[strdate] = dict() # 
        epgchannels = list()
        for channel in channels:
            epgchannels.append(channel+'_'+strdate)
        urlchannels = '%2C'.join(epgchannels)
        req = requests.get(epg_url.format(channels=urlchannels)).json() # epg parse
        print(req)
        input('')
        for c, epgitems in req.items():
            for epgitem in epgitems:
                channel = epgitem['channel_type']+'_'+str(epgitem['serviceCode'])
                channelname = epgitem['channelName']
                dateStart = datetime.strptime(str(epgitem['programStart']), programdatefmt)
                dateEnd = datetime.strptime(str(epgitem['programEnd']), programdatefmt)
                title = epgitem['title']
                title = title.replace('&', '%26')
                title = title.replace('<', '%3C')
                title = title.replace('>', '%3E')
                description = epgitem['commentary']
                description = description.replace('&', '%26')
                description = description.replace('<', '%3C')
                description = description.replace('>', '%3E')
                stereo = False
                if 'stereo' in epgitem['attr']:
                    stereo = True
                if not channel in epg[strdate].keys(): ##
                    epg[strdate][channel] = {
                        'name': channelname,
                        'programs': list()
                    }
                epg[strdate][channel]['programs'].append({ ##
                    'start': dateStart,
                    'end': dateEnd,
                    'title': title,
                    'description': description,
                    'stereo': stereo
                })
            #print(epg[strdate].keys())
        #print(epg[strdate].keys())
        #input()

channelslol = dict()

channelslol.update(grabChannels(108, [2]))
channelslol.update(grabChannels(28, [2]))
channelslol.update(grabChannels(32, [2]))
channelslol.update(grabChannels(108, [3, 120]))

addEPG(channelslol.keys(), 14)

xml = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE tv SYSTEM "https://github.com/XMLTV/xmltv/raw/master/xmltv.dtd">\n<tv source-info-url="https://tvguide.myjcom.jp/" source-info-name="J-COM Program Guide" generator-info-name="samicrusader\'s EPG Parsers" generator-info-url="https://github.com/samicrusader/epg">\n'
xmlfoot = '</tv>'
xmlchannels = list()
xmllistings = list()

# process channels
for i, channel in epg[list(epg.keys())[0]].items():
    xc = f'  <channel id="{i}.myjcom.jp">\n    <display-name>{channel["name"]}</display-name>\n    <icon src="" />\n  </channel>\n'
    xmlchannels.append(xc)

# process listings
for date, channels in epg.items():
    for i, channel in channels.items():
        for listing in channel['programs']:
            start = listing['start'].strftime('%Y%m%d%H%M%S')+' +0900'
            stop = listing['end'].strftime('%Y%m%d%H%M%S')+' +0900'
            xl = f'  <programme start="{start}" stop="{stop}" channel="{i}.myjcom.jp">\n    <title lang="jp">{listing["title"]}</title>\n    <desc lang="jp">{listing["description"]}</desc>\n    <date>{date}</date>'
            if listing['stereo']:
                xl += '\n    <audio>\n      <stereo>stereo</stereo>\n    </audio>'
            xl += '\n  </programme>\n'
            xmllistings.append(xl)

xml += ''.join(xmlchannels)
xml += ''.join(xmllistings)
xml += xmlfoot
fh = open('jcom.xml', 'w', encoding='utf8')
fh.write(xml)
fh.close()