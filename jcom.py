#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import re
import requests
from datetime import datetime, timedelta
from urllib.parse import quote

# https://tvguide.myjcom.jp/detail/?channelType=2&serviceCode=24632_32375&eventId=604&programDate=20220413 # may be needed later

# Notes:
genres = {
    6: 'movie', 
    3: 'drama', 
    1: 'sports', 
    7: 'Anime/SFX', 
    4: 'music', 
    5: 'variety', 
    10: 'hobbies/education', 
    8: 'Documentary / Culture', 
    0: 'News', 
    9: 'Information / wide show', 
    11: 'Theater/Performance', 
    13: 'Others', 
    12: 'Welfare'
}

channelTypes = {
    2: 'Terrestial',
    3: 'BS',
    120: 'CS'
}

xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<!DOCTYPE tv SYSTEM "https://github.com/XMLTV/xmltv/raw/master/xmltv.dtd">\n'
xml += '<tv source-info-url="https://tvguide.myjcom.jp/" source-info-name="J-COM Program Guide" generator-info-name="samicrusader\'s EPG Parsers" generator-info-url="https://github.com/samicrusader/epg">\n'

channels = dict()
req = requests.get(f'https://tvguide.myjcom.jp/api/mypage/getEpgChannelList/?channelType=120&area=108&channelGenre=&course=&chart=&is_adult=true')
for channel in req.json()['header']:
    code = '120_'+channel['service_code']
    xml += f'    <channel id="{code}.myjcom.jp">\n'
    xml += f'        <display-name lang="jp">{channel["channel_name"]}</display-name>\n'
    xml += '    </channel>\n'
    channels.update({code: channel['channel_name']})

xml += '\n'

epg = dict()
for i in range(7):
    date = (datetime.now() + timedelta(days=i)).strftime('%Y%m%d')
    if not date in epg.keys():
        epg[date] = dict()
    epgchannels = list()
    for channel in channels:
        epgchannels.append(channel+'_'+date)
    req = requests.get(f'https://tvguide.myjcom.jp/api/getEpgInfo/?channels={"%2C".join(epgchannels)}&rectime=&rec4k=').json()
    for c, epgitems in req.items():
        for epgitem in epgitems:
            xml += f'    <programme start="{epgitem["programStart"]}" end="{epgitem["programEnd"]}" channel="120_{epgitem["serviceCode"]}.myjcom.jp">\n'
            xml += f'        <title lang="ja">{quote(epgitem["title"])}</title>\n'
            #xml += f'        <sub-title lang="ja">{}</sub-title>\n'
            xml += f'        <desc lang="ja">{quote(epgitem["commentary"])}</desc>\n'
            # TODO: credits
            xml += f'        <date>{epgitem["programDate"]}</date>\n'
            # TODO: dt object
            # TODO: category, keyword
            xml += f'        <language>ja</language>\n'
            xml += f'        <length units="minutes">{epgitem["duration"]}</length>\n'
            # TODO: icon, url, mediainfo
            xml += f'        <country>jp</country>\n'
            epnum = re.findall(r'#\d+', epgitem['title'])
            skipepnum = False
            if list(epgitem['sortGenre'])[0] == '6':
                skipepnum = True
            if not skipepnum:
                if epnum:
                    xml += f'        <episode-num system="onscreen">{epnum[0].replace("#", "")}</episode-num>\n'
                else:
                    xml += f'        <episode-num system="onscreen">{epgitem["programDate"]}</episode-num>\n'
            xml += '    </programme>\n'

xml += '</tv>'

fh = open('JCOM.xml', 'w')
fh.write(xml)
fh.close()