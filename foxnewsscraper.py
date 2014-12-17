from selenium import webdriver
import time
import numpy as np
from dateutil import parser
from datetime import datetime as dt
import mysql.connector
import os

"""
Super thanks to
https://github.com/ethancheung2013
You are awesome and I owe you a beer
"""


def getHref(webelements):
#        for i, element in enumerate(webelements):
#            print element.find_element_by_tag_name('a').get_attribute('href')
    return [wElement.find_element_by_tag_name('a').get_attribute('href') for wElement in webelements]

def showmore():
    # get the next page
    for i, element in enumerate(browser.find_elements_by_class_name("more-btn")):
        print element.find_element_by_tag_name('a').get_attribute('href')

def connect_to_db():
    ''' 
    NAME
        connect_to_db
    SYNOPSIS
        Connect to postgres
    DESCRIPTION
        Connect to postgres at __main__
    '''  

    # query database for a list of urls and put in set

    DBNAME = 'foxnews'
    DBUSER = 'tiger'

    pf = open('password.txt')
    passwd = pf.readline()
    PASSWRD = passwd
    #ipdb.set_trace()
    return mysql.connector.connect(database= DBNAME, user=DBUSER, password=PASSWRD)

def getContent(setOfURL):
    connection = connect_to_db()
    for oneURL in setOfURL:
        browser.get(oneURL)
        strTitle = ''
        datePub = ''

        articleHeader = browser.find_elements_by_xpath('//*[@id="content"]/div/div/div[2]/div/div[3]/article')
        if len(articleHeader) > 0:
            for eHeader in articleHeader[0].find_elements_by_tag_name('h1'):
                strTitle = eHeader.text

            for dHeader in articleHeader[0].find_elements_by_tag_name('time'):
                datePub = dHeader.get_attribute('datetime')
        # retrieve the content via p tags
        mainStory = browser.find_elements_by_xpath('//*[@id="content"]/div/div/div[2]/div/div[3]/article/div/div[3]')

        if len(mainStory) == 1:
            content = ''
            for eContent in mainStory[0].find_elements_by_tag_name('p'):
                content += ''.join(eContent.text)

        print storeContent(strTitle, datePub, content, oneURL, connection=connection)
    return True

def storeContent(strTitle, datePub, content, iurl, connection=None):
    '''
    NAME
            storeContent
    SYNOPSIS
            Stores raw string data to Postgres using 'psql newscontent' generated with Django
            
    DESCRIPTION
           Stored variables:
                id      | integer                  | not null default nextval('stocknews_newscontent_id_seq'::regclass)
                url     | character varying(1000) 
                title   | character varying(4000) 
                content | character varying(50000)
                date    | date                    
           table: stocknews_newscontent       
    '''
    if connection is None:
        connection = connect_to_db()
    cur = connection.cursor(prepared=True)


    dateObj = str(parser.parse(datePub.strip() , tzinfos={'EST', -18000}))
    if dateObj == '' or dateObj is None:
        dateObj = dt.now()

    sql = "INSERT into stocknews_newscontent (url, title, content, date) values (%s, %s, %s, %s);"
    try: 
        cur.execute(sql, (iurl, strTitle, content, datePub))
    except:
        datePub = dt.now()
        cur.execute(sql, (iurl, strTitle, content, datePub))

    connection.commit()
    return "The item : %s was successfully saved to the databse" % strTitle

def main():
    '''
    NAME: main
    SYNOPSIS:
       Macro economic news scraper for Fox News
    DESCRIPTION:
       'Show More' button displays an extra 10 links
       Scraper clicks the 'Show More' button a configured number of times
       Then opens each link individual and scrapes the content going through H3 tags
    '''
    url = 'http://www.foxnews.com/politics/index.html#'

    browser.get(url)
    numClicks = 1
    advanceClicks = 50
    while numClicks < advanceClicks:
        if numClicks == 1:
                #url = 'http://www.foxnews.com/us/economy/index.html#'
                for eClick in np.arange(advanceClicks):
                    if numClicks % 10 == 0:
                        print numClicks
                    # find the Show More button and click it a bunch of times
                    browser.find_element_by_class_name("load").click()
                    time.sleep(2)
                    numClicks += 1

    # all news headlines are li but on under ul
    setURL = set()
    for i, element in enumerate(browser.find_elements_by_xpath('//*[@id="content"]/div/div[3]/div[6]/section/div/ul/li')):
        try:
            h3Element = element.find_element_by_tag_name('article')
#            ipdb.set_trace()
            url = h3Element.find_element_by_tag_name('a').get_attribute('href')
            # we want to throw out all the links to genre pages and only want articles.
            if url.startswith('http://www.foxnews.com/politics/20'):
                setURL.add(url)
        except: # NoSuchElementException:
            pass
    #strTitle, datePub, strContent, strUrl  = getContent(setURL)

    getContent(setURL)

if __name__ == '__main__':
    chromedriver = "/Users/mbrown/Downloads/chromedriver/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    browser = webdriver.Chrome(chromedriver)
    main()