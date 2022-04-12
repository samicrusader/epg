#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# https://bangumi.org/epg/cs?broad_cast_date=20220412

baseURL = 'https://bangumi.org/epg/cs'

req = requests.get(baseURL)#, params={})
soup = BeautifulSoup(req.text, 'html.parser')

channelslist = soup.find('li', {'class': 'js_channel'}).findall('p')
channels = dict()

for channel in channelslist:
    channel = channel.text.split(' ', 1)
    channels.update({channel[0]: channel[1]})

#          <li style="top:2308px;height:64px;" class="sc-past" s="202204121800" e="202204121830"
#              pid="-1" se-id="218-52545">
#            <div class="program_time gc-anime">00</div>
#            <div class="program_text">
#              <a class="title_link js-logging" data-content="{&quot;category&quot;:&quot;event&quot;,&quot;action&quot;:&quot;si_click&quot;,&quot;title&quot;:&quot;宇宙戦隊キュウレンジャー #47&quot;,&quot;contentsId&quot;:97867625,&quot;programId&quot;:&quot;-1&quot;,&quot;programDate&quot;:&quot;20220412&quot;,&quot;timePosition&quot;:-1,&quot;shadeFlg&quot;:0}" href="/tv_events/AfwgDazUEAI">
#                <p class="program_title">宇宙戦隊キュウレンジャー #47</p>
#</a>              <p class="program_detail">宇宙×星座をモチーフとしたスーパー戦隊シリーズ第41作。
##47 救世主たちの約束
#出演：岐洲匠／岸洋佑 2017年 全48話</p>
#            </div>
#            <div class="cover"></div>
#          </li>

programarea = soup.find('div', {'id': 'program_area'})
for listing in programarea.findall('li', {'class': 'sc-future'})+programarea.findall('li', {'class': 'sc-current'})+programarea.findall('li', {'class': 'sc-past'}):
    channel = listing['se-id'].split('-')[0]
    id = listing['se-id'].split('-')[1]
    date = listing['s']
    title = listing.find('p', {'class': 'program_title'})
    desc = listing.find('p', {'class': 'program_title'})
    inforeq = requests.get(f'https://bangumi.org{listing.find("a")["href"]}')
    infosoup = BeautifulSoup(inforeq.text, 'html.parser')
    pass