# -*- coding: utf-8 -*-
# sample url : https://play.google.com/store/apps/details?id=com.neowizgames.game.browndust.srpg.gamfs
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd

driver = webdriver.Chrome('./chromedriver')
driver.get('https://play.google.com/store/apps/details?id=com.neowizgames.game.browndust.srpg.gamfs&showAllReviews=true') #접속할 Review URL

SCROLL_PAUSE_TIME = 3 #sleep time setting

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

# review의 volumn control이 필요시 while문 이전에 for i in range(n): 에 포함시킴


while True: #전체 review crawling 진행
    try:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        time.sleep(SCROLL_PAUSE_TIME)
        driver.find_elements_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div[2]/div/content')[0].click()
    except IndexError:
        pass

table_dict = {}
date_list = []
contents_list = []
stars_list = []

reviews=driver.find_elements_by_xpath("//*[@jsname='fk8dgd']//div[@class='d15Mdf bAhLNe']")

star_cnt = 0
for review in reviews: #text로 설명된 rating
    soup=BeautifulSoup(review.get_attribute("innerHTML"),"lxml")
    ratings=soup.find('div',role='img').get('aria-label')
    stars_list.append(ratings)
    star_cnt += 1

print("{}개의 review를 수집합니다.".format(star_cnt))

for i in range(1,star_cnt+1): #review text
    review_txt = driver.find_elements_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div['+ str(i) + ']/div/div[2]/div[2]/span[1]')[0].text
    contents_list.append(review_txt)
    if i%100==0:
        print("{}th review text".format(i))
    
for i in range(1,star_cnt+1): #review date
    review_date = driver.find_elements_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div['+ str(i) + ']/div/div[2]/div[1]/div[1]/div/span[2]')[0].text
    date_list.append(review_date)
    if i%100==0:
        print("{}th review date".format(i))
    

table_dict['time'] = date_list
table_dict['review_txt'] = contents_list
table_dict['stars_txt'] = stars_list

print('\n','\n','\n')

review_df = pd.DataFrame.from_dict(table_dict)
review_df['time'] = review_df.loc[:,'time'].str.replace(" ","")
review_df['time'] = pd.to_datetime(review_df.loc[:,'time'], format = '%Y년%m월%d일')
print('가장 최근 작성 review 날짜 : {} '.format(review_df['time'].max()))
print('가장 오래전 작성 review 날짜 : {} '.format(review_df['time'].min()))

review_df['ratings'] = review_df['stars_txt'].str[10]
review_df['ratings'] = review_df['ratings'].astype(int)

print('review 별 평점 분포', '\n', review_df['ratings'].value_counts())
print('review 별 평점 분포 %', '\n', review_df['ratings'].value_counts(normalize = True))
    
review_df.to_csv('review_crwl.csv', index = False)

driver.close()