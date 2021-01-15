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
smd_yesterday

#### 어제꺼에서 feed 이용해서 오늘자 내용 읽어옴
post_titles = []
post_links = []
for b in range(np.shape(smd_yesterday)[0]):
  print(smd_yesterday['name'][b])


  if smd_yesterday['source'][b] != 'naver_feedx':
    rss_feed = feedparser.parse(smd_yesterday['rss_feed'][b])
    rss_list = []
    for entry in rss_feed.entries[:5]:
      # print(entry)
      rss_list.append(entry)

    temp =  rss_list[0]
    temp

    if smd_yesterday['name'][b] == 'dsba_seminar': ### feed 확인
      temp = rss_list[3]
    
    
    print(temp['title'])
    print(temp['link'])
    ## print(temp['author']) # 가끔 안나옴 --> 그냥 넣어줘야 할듯...



    post_titles.append(temp['title'].strip())
    post_links.append(temp['link'].strip())
    # post_titles.append(smd_yesterday['name'][b])
    print(" ")

  elif smd_yesterday['source'][b] == 'naver_feedx':
    print('')

### 뉴리스트 만들기(오늘자)
new_list = pd.DataFrame()
new_list['name'] = smd_yesterday['name']
new_list['rss_feed'] = smd_yesterday['rss_feed']
new_list['title'] = post_titles ###
new_list['link'] = post_links ### update 부분!
new_list

#### 과거와 비교
new_index = np.where(new_list['title'] != smd_yesterday['title']) ## 오늘 vs 과거
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
now = time.localtime()
daylist = ['월', '화', '수', '목', '금', '토', '일']
ccc = daylist[now.tm_wday]
 
year, month, day, hour, min = map(str, time.strftime("%Y %m %d %H %M").split())
today = year + "년 " + month +"월 " + day + "일 "+ ccc + "요일 오늘의 QT:" 
slack.chat.post_message(channel='#1_mlblog-bot',
                        text = "{0} \n*{1}* \n<{2}|{3}> :bell:".format(today, bible1, 'https://sum.su.or.kr:8888/bible/today' , script) )



## new post가 있는 경우에 
if len(new_index) > 0:
  print("updated is exist!")
  for n in new_index:
    # print(n)
    # print(new_list['title'][n])
    # print(new_list['link'][n])
    slack.chat.post_message(channel='#1_mlblog-bot',
                            #as_user = True,
                            #icon_url='https://cdn2.iconfinder.com/data/icons/artificial-intelligence-ai-color/64/diagram-deep-learning-machine-network-nural-512.png',
                            text = "{0}: <{1}|link>".format(new_list['name'][n],
                                                            new_list['link'][n]))

  #### ref 업데이트!
  for t in new_index:
    # print(t)
    smd_yesterday['title'][t] =  new_list['title'][t]
    smd_yesterday['link'][t] =  new_list['link'][t]

  smd_today = smd_yesterday
  # smd_today.to_excel('/content/drive/MyDrive/Colab Notebooks/3. Hobby/latest_list/20210110_old_list_ref.xlsx', index = False)
  # smd_today.to_excel(base_url + '/20210110_old_list_ref.xlsx', index = False)
  smd_today.to_excel('20210110_old_list_ref.xlsx', index = False)
    
    
    
    
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
