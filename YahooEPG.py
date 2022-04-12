#!/usr/bin/env python3

import re
import requests
from datetime import datetime
from urllib.parse import quote

# Yahoo!Japan G-GuideのリストをXMLTV形式にダンプするためのツール。
# Tool for dumping Yahoo!Japan G-Guide listings to XMLTV format.
# This should match up to the channels provided by MujiTV last time I checked.
# https://samicrusader.me (私自身は日本語を理解できませんので、連絡は英語でお願いします。)

# 日本語での情報提供を希望される場合は、「False」に設定してください。(not currently configured)
useEnglish = True

# Notes:
genreMappingsEN = {
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
    #'0xB': "Welfare", # DeepL recommended "social welfare". Most shows in this category are dramas. 
    '0xB': "Other",
    # Where is 0xC-0xE?
    '0xF': "Other"
}

serviceMappingsEN = {
    1: "BS",
    # 2 is broken
    3: "Terrestial"
}

areaMappingsEN = {
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

###

listings = dict()

for servicemapping in serviceMappingsEN.keys():
    for areaid in areaMappingsEN.keys():
        x = requests.get(baseURL, params={'siTypeId': servicemapping, 'areaId': areaid, 'hours': 24, 'broadCastStartDate': 1649793300, '_api': 'programListingQuery'})
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
#print(listings[list(listings.keys())[1]]['listings'][3])

{
    'contentsId': '97949088',
    'programId': 39650,
    'siTypeId': 1,
    'siTypeName': 'BS(2K)',
    'networkId': '0x0004',
    'serviceId': '0x0067',
    'serviceName': 'NHKBSプレミアム',
    'channelNumber': 103,
    'channelSortOrder': 103,
    'broadCastStartDate': 1649796900,
    'broadCastEndDate': 1649797200,
    'duration': 300,
    'majorGenreId': ['0x4', '0xA', '0x8'],
    'programTitle': '名曲アルバム',
    'title': '名曲アルバム「水の変態」宮城道雄・作曲',
    'summary': '「春の海」で知られる箏曲家・宮城道雄が１４歳で挑んだ第一作。生涯をかけて箏曲の革新に挑み続けた道雄の原点というべき一曲を清らかな水の情景とともにお届けする。',
    'mitaiCount': 137,
    'reviewCount': 0,
    'ratingCount': 1,
    'ratingAverage': 5,
    'listingsFlg': True,
    'featureImage': '',
    'updateTime': '2022-04-08T03:00:15Z',
    'broadCastStartDateMinute': 1649796900,
    'broadCastEndDateMinute': 1649797200,
    'durationMinute': 5,
    'channelName': 'NHKBSプレミアム'
}

xml = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE tv SYSTEM "https://github.com/XMLTV/xmltv/raw/master/xmltv.dtd">\n<tv source-info-url="https://tv.yahoo.co.jp" source-info-name="Yahoo!テレビ - Gガイド" source-data-url="https://tv.yahoo.co.jp/listings" generator-info-name="YahooEPG.py" generator-info-url="https://www.youtube.com/watch?v=wg7tMJLSfwI">\n'

for item in listings.keys():
    xml += f'    <channel id="{item}">\n'
    xml += f'        <display-name lang="jp">{listings[item]["channelName"]}</display-name>\n'
    # TODO: icon, url
    xml += f'    </channel>\n'

xml += '\n'

for item in listings.keys():
    for listing in listings[item]['listings']:
        xml += f'    <programme start="" channel="{item}>\n'
        xml += f'        <title lang="ja">{quote(listing["programTitle"])}</title>\n'
        xml += f'        <sub-title lang="ja">{quote(listing["title"])}</sub-title>\n'
        xml += f'        <desc lang="ja">{quote(listing["summary"])}</desc>\n'
        # TODO: credits
        if not 'updateTime' in listing.keys():
            listing.update({'updateTime': datetime.fromtimestamp(listing['broadCastStartDate']).strftime('%Y-%m-%dT%H:%M:%SZ')})
        xml += f'        <date>{listing["updateTime"].split("T")[0].replace("-", "")}</date>\n' # TODO: dt object
        # TODO: category, keyword
        xml += f'        <language>ja</language>'
        xml += f'        <length units="minutes">{listing["durationMinute"]}</length>\n'
        # TODO: icon, url
        xml += f'        <country>JP</country>\n'
        epnum = re.findall(r'#\d+', listing['title'])
        skipepnum = False
        if 'majorGenreId' in listing.keys():
            if '0x6' in listing['majorGenreId']:
                skipepnum = True
        if not skipepnum:
            if epnum:
                xml += f'        <episode-num system="onscreen">{epnum[0]}</episode-num>\n'
            else:
                xml += f'        <episode-num system="onscreen">{listing["updateTime"].split("T")[0]}</episode-num>\n'
        xml += '    </programme>\n'
        
xml += '</tv>'

fh = open('YahooEPG.xml', 'w')
fh.write(xml)
fh.close()