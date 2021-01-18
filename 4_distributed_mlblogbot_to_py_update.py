# -*- coding: utf-8 -*-
"""3. distributed_mlblogbot_To_py.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jGaP8ZU7D1_yCmAUB0hW5-A4x4oasnIY

# 패키지 임포트
"""

import pandas as pd
import numpy as np
import sys, os
import time
import requests
import json
import openpyxl

import datetime
import pytz 
from pytz import timezone

from bs4 import BeautifulSoup
# pip install feedparser
import feedparser
# pip install slacker
from slacker import Slacker

base_url = os.path.dirname(os.path.abspath(__file__))

# rd =  pd.read_excel('/content/drive/MyDrive/Colab Notebooks/3. Hobby/latest_list/20210110_old_list_ref.xlsx')
# rd =  pd.read_excel(base_url + '/20210110_old_list_ref.xlsx')
rd =  pd.read_excel('20210110_old_list_ref.xlsx')
rd.head(2)

#### 사용할 것으로 필터링
smd_yesterday = rd[rd['used'] == 'o']
smd_yesterday
smd_yesterday.reset_index(drop = True, inplace=True)
smd_yesterday.to_excel('Blogs_used_list.xlsx', index = False)

rd2 =  pd.read_excel('Blogs_used_list.xlsx') 
smd_today = rd2

#### 어제꺼에서 feed 이용해서 오늘자 내용 읽어옴
post_titles = []
post_links = []
for b in range(np.shape(smd_today)[0]):
  print(smd_today['name'][b])

  if smd_today['source'][b] != 'naver_feedx':
    rss_feed = feedparser.parse(smd_today['rss_feed'][b])
    rss_list = []
    for entry in rss_feed.entries[:5]:
      # print(entry)
      rss_list.append(entry)

    temp =  rss_list[0]
    temp

    if smd_today['name'][b] == 'dsba_seminar': ### feed 확인
      temp = rss_list[3]
    
    if smd_today['name'][b] == 'insightCampus': ### feed 확인
      temp = rss_list[1]
    
    print(temp['title'])
    print(temp['link'])
    ## print(temp['author']) # 가끔 안나옴 --> 그냥 넣어줘야 할듯...



    post_titles.append(temp['title'].strip())
    post_links.append(temp['link'].strip())
    # post_titles.append(smd_yesterday['name'][b])
    print(" ")

  elif smd_today['source'][b] == 'naver_feedx':
    print('')

### 뉴리스트 만들기(오늘자)
new_list = pd.DataFrame()
new_list['name'] = smd_today['name']
new_list['rss_feed'] = smd_today['rss_feed']
new_list['title'] = post_titles ###
new_list['link'] = post_links ### update 부분!
new_list

#### 과거와 비교
new_index = np.where(new_list['title'] != smd_today['title']) ## 오늘 vs 과거
new_index # 다른 index


# print(new_index)
# print(np.shape(new_index))
## new_list['title'][new_index]new_index

### 달라진 내용 확인
np.shape(new_index)[1]
new_index = np.concatenate(new_index)
for t in new_index:
  print('')
  # print(t)
  # print(new_list['title'][t])
  # print(new_list['link'][t])

## 오늘의 QT 말씀
# 매일성경
temp = 'https://sum.su.or.kr:8888/bible/today'
url = f'{temp}'
req = requests.get(url)
html = req.text
soup = BeautifulSoup(html, 'html.parser')

bible1 = soup.find_all(class_ = 'bible_text')
bible1 = bible1[0].getText().strip()
print(bible1)


script = soup.find_all(class_ = 'bibleinfo_box')
script = script[0].getText().strip()
print(script)


today_bible = bible1 + ", (" + script + ")"
print(today_bible)


#### 슬랙 메시지 보내기!

### 슬랙 토큰
token = os.environ.get('SLACK_URL')
slack = Slacker(token)


## 오늘의 
def getDay(x):
    daylist = ['월', '화', '수', '목', '금', '토', '일']
    return daylist[x]




# year, month, day, hour, min = map(str, time.strftime("%Y %m %d %H %M").split())
year, month, day, hour, min = map(str, datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y %m %d %H %M").split())
date = getDay(datetime.date(int(year), int(month), int(day)).weekday())
today = year + "년 " + month +"월 " + day + "일 "+ date + "요일 오늘의 QT:" 
# slack.chat.post_message(channel='#1_mlblog-bot',
#                        text = "{0} \n*{1}* \n<{2}|{3}> :bell:".format(today, bible1, 'https://sum.su.or.kr:8888/bible/today' , script) )

attachments_dict = dict()
attachments_dict['pretext'] =  today ## 맨위 날짜
attachments_dict['title'] = "{0}".format(bible1)
attachments_dict['title_link'] = 'https://sum.su.or.kr:8888/bible/today'
attachments_dict['text'] = "{0}/<{1}|날씨>/<{2}|오늘의영어> :bell:".format( 'Maeil bible', 'https://weather.naver.com/today', 'https://learn.dict.naver.com/m/endic/main.nhn') 
attachments_dict['color']= "#36a64f"
attachments_dict['mrkdwn'] = 'true'
attachments = [attachments_dict]

slack.chat.post_message(channel='#1_mlblog_bot',
                        text = None,
                        attachments = attachments,
                        #icon_url='https://cdn2.iconfinder.com/data/icons/artificial-intelligence-ai-color/64/diagram-deep-learning-machine-network-nural-512.png',
                        #as_user = True
                        )

# for no commit case
now = time.localtime()
file = open("qt.txt", "w");
file.write(str(now))

## new post가 있는 경우에 
if len(new_index) > 0:
  print("updated is exist!")
  for n in new_index:
    # print(n)
    # print(new_list['title'][n])
    # print(new_list['link'][n])
    slack.chat.post_message(channel='#1_mlblog_bot',
                            #as_user = True,
                            #icon_url='https://cdn2.iconfinder.com/data/icons/artificial-intelligence-ai-color/64/diagram-deep-learning-machine-network-nural-512.png',
                            text = "{0}: <{1}|link>".format(new_list['name'][n],
                                                            new_list['link'][n]))

  #### ref 업데이트!
  for t in new_index:
    # print(t)
    smd_today['title'][t] =  new_list['title'][t]
    smd_today['link'][t] =  new_list['link'][t]

  blog_today_list = smd_today
  # smd_today.to_excel('/content/drive/MyDrive/Colab Notebooks/3. Hobby/latest_list/20210110_old_list_ref.xlsx', index = False)
  # smd_today.to_excel(base_url + '/20210110_old_list_ref.xlsx', index = False)
  # blog_today_list.to_excel('20210110_old_list_ref.xlsx', index = False)
  blog_today_list.to_excel('Blogs_used_list.xlsx ', index = False)  
   
    
    
    
###
'''
now = time.localtime()
daylist = ['월', '화', '수', '목', '금', '토', '일']
ccc = daylist[now.tm_wday]
 
year, month, day, hour, min = map(str, time.strftime("%Y %m %d %H %M").split())
today = year + "년 " + month +"월 " + day + "일 "+ ccc + "요일 오늘의 QT:" 
# slack.chat.post_message(channel='#1_mlblog-bot',
#                         text = "{0} \n*{1}* \n<{2}|{3}> :bell:".format(today, bible1, 'https://sum.su.or.kr:8888/bible/today' , script) )

webhook_url= ''

payload = {
    "text": 'text  <https://www.google.com| This is a line of text>'
}


requests.post(
    url = webhook_url, data = json.dumps(payload),
    headers={'Content-Type':'application/json'}
)

'''


###
print("end!")
