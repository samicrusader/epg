#!/usr/bin/env python3

import re
import requests
from datetime import datetime, timezone

# Yahoo!Japan G-GuideのリストをXMLTV形式にダンプするためのツール。
# Tool for dumping Yahoo!Japan G-Guide listings to XMLTV format.
# This should match up to the channels provided by MujiTV last time I checked.
# https://samicrusader.me (私自身は日本語を理解できませんので、連絡は英語でお願いします。)

# Notes:
genreMappings = {
    '0x0': "News",
    '0x1': "Sports",
    '0x2': "Informational", # Other translations put this as "Informational/Variety", while there still being a category for variety shows.
    '0x3': "Drama",
    '0x4': "Music",
    '0x5': "Variety",
    '0x6': "Movie",
    '0x7': "Anime/SFX",
    '0x8': "Documentary",
    '0x9': "Theater",
    '0xA': "Educational", # Hobby/Educational
    '0xB': "Welfare", # DeepL recommended "social welfare". Most shows in this category are dramas. 
    '0xB': "Other",
    # Where is 0xC-0xE?
    '0xF': "Other"
}

serviceMappings = {
    1: "BS",
    # 2 is broken
    3: "Terrestial"
}

areaMappings = {
    #10: 'Hokkaido (Sapporo)',
    #11: 'Hokkaido (Hakodate)',
    #12: 'Hokkaido (Asahikawa)',
    #13: 'Hokkaido (Obihiro)',
    #14: 'Hokkaido (Kushiro)',
    #15: 'Hokkaido (Kitami)',
    #16: 'Hokkaido (Muroran)',
    #17: 'Miyagi',
    #18: 'Akita',
    #19: 'Yamagata',
    #20: 'Iwate',
    #21: 'Fukushima',
    #22: 'Aomori',
    23: 'Tokyo', #z
    #24: 'Kanagawa',
    #25: 'Gunma',
    #26: 'Ibaraki',
    #27: 'Chiba',
    #28: 'Tochigi',
    #29: 'Saitama', #z
    #30: 'Nagano',
    #31: 'Niigata',
    #32: 'Yamanashi',
    #33: 'Aichi',
    #34: 'Ishikawa',
    #35: 'Shizuoka',
    #36: 'Fukui',
    #37: 'Toyama',
    #38: 'Triple (?)', # "三重" What?
    #39: 'Gifu',
    40: 'Osaka', #z
    #41: 'Kyoto',
    42: 'Hyogo',
    #43: 'Wakayama',
    #44: 'Nara',
    #45: 'Shiga',
    #46: 'Hiroshima',
    #47: 'Okayama',
    #48: 'Shimane',
    #49: 'Tottori',
    #50: 'Yamaguchi',
    #51: 'Ehime',
    #52: 'Kagawa',
    #53: 'Tokushima',
    #54: 'Kochi',
    #55: 'Fukuoka',
    #56: 'Kumamoto',
    #57: 'Nagasaki',
    #58: 'Kagoshima',
    #59: 'Miyazaki',
    #60: 'Oita',
    #61: 'Saga',
    #62: 'Okinawa'
}

baseURL = 'https://tv.yahoo.co.jp/api/adapter'

def XMLQuote(input:str):
    input = input.replace('&', '&amp;')
    input = input.replace('\'', '&apos;')
    input = input.replace('"', '&quot;')
    input = input.replace('<', '&lt;')
    input = input.replace('>', '&gt;')
    return input

###

listings = dict()

xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<!DOCTYPE tv SYSTEM "https://github.com/XMLTV/xmltv/raw/master/xmltv.dtd">\n'
xml += '<tv source-info-url="https://tv.yahoo.co.jp" source-info-name="Yahoo!テレビ - Gガイド" source-data-url="https://tv.yahoo.co.jp/listings" generator-info-name="samicrusader\'s EPG Parsers" generator-info-url="https://github.com/samicrusader/epg">\n'

for i in range(7):
    for servicemapping in serviceMappingsEN.keys():
        for areaid in areaMappingsEN.keys():
            dt = datetime.now()
            dt = int(datetime(dt.year, dt.month, dt.day+i, 15, 0, 0, tzinfo=timezone.utc).timestamp())
            x = requests.get(baseURL, params={'siTypeId': servicemapping, 'areaId': areaid, 'hours': 24, 'broadCastStartDate': dt, '_api': 'programListingQuery'})
            try:
                #print(areaMappingsEN[areaid]+':', 'got', len(x.json()['ResultSet']['Result']), 'listings')
                for item in x.json()['ResultSet']['Result']:
                    sn = item['networkId']+'.'+item['serviceId']+'.tv.yahoo.co.jp'
                    if sn not in listings.keys():
                        print(f'Added from {areaMappingsEN[areaid]}: {item["serviceName"]}')
                        listings.update({
                            sn: {
                                'serviceName': item['serviceName'],
                                'channelName': item['channelName'],
                                'listings': list()
                            }
                        })
                    if item not in listings[sn]['listings']:
                        listings[sn]['listings'].append(item)
                if servicemapping == 1 and not areaid == 23:
                    break
            except:
                print(x.json())
                exit(1)

for item in listings.keys():
    xml += f'    <channel id="{item}">\n'
    xml += f'        <display-name lang="jp">{listings[item]["channelName"]}</display-name>\n'
    # TODO: icon, url
    xml += f'    </channel>\n'

xml += '\n'

programs = list()

for item in listings.keys():
    for listing in listings[item]['listings']:
        programme = f'    <programme start="{datetime.fromtimestamp(listing["broadCastStartDate"]).strftime("%Y%m%d%H%M%S")}" stop="{datetime.fromtimestamp(listing["broadCastEndDate"]).strftime("%Y%m%d%H%M%S")}" channel="{item}">\n'
        if not listing["programTitle"]:
            programme += f'        <title lang="ja">{XMLQuote(listing["title"])}</title>\n'    
        else:
            programme += f'        <title lang="ja">{XMLQuote(listing["programTitle"])}</title>\n'
            programme += f'        <sub-title lang="ja">{XMLQuote(listing["title"])}</sub-title>\n'
        if listing["summary"]:
            programme += f'        <desc lang="ja">{XMLQuote(listing["summary"])}</desc>\n'
        # TODO: credits
        if not 'updateTime' in listing.keys():
            listing.update({'updateTime': datetime.fromtimestamp(listing['broadCastStartDate']).strftime('%Y-%m-%dT%H:%M:%SZ')})
        programme += f'        <date>{listing["updateTime"].split("T")[0].replace("-", "")}</date>\n' # TODO: dt object
        # TODO: category, keyword
        programme += f'        <language>ja</language>\n'
        programme += f'        <length units="minutes">{listing["durationMinute"]}</length>\n'
        # TODO: icon, url
        programme += f'        <country>JP</country>\n'
        epnum = re.findall(r'#\d+', listing['title'])
        skipepnum = False
        if 'majorGenreId' in listing.keys():
            if '0x6' in listing['majorGenreId']:
                skipepnum = True
        if not skipepnum:
            if epnum:
                programme += f'        <episode-num system="onscreen">{epnum[0]}</episode-num>\n'
            else:
                programme += f'        <episode-num system="onscreen">{listing["updateTime"].split("T")[0]}</episode-num>\n'
        programme += '    </programme>\n'
        if not programme in programs:
            programs.append(programme)
xml += ''.join(programs)
xml += '</tv>'

fh = open('YahooEPG.xml', 'w')
fh.write(xml)
fh.close()
