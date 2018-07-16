


from bs4 import BeautifulSoup
import numpy as np
import seaborn as sns
import pandas as pd
from DbManager import DatabaseManager
import json
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from datetime import datetime
import calendar
from selenium.webdriver.common.action_chains import ActionChains

class Scraper():

    def __init__(self, initialize_db):

        self.browser = webdriver.Chrome("/Users/susysk/Downloads/odds-portal-scraper-master/chromedriver/chromedriver")
        #self.league = self.parse_json(league_json)
        self.db_manager = DatabaseManager(initialize_db)


    def scrape_all_urls(self, do_verbose_output=False):

        if do_verbose_output is True:
            output_str = "Start scraping " + self.league["league"] + " of "
            output_str += self.league["area"] + "..."
            print(output_str)

        for url in self.league["urls"]:
            try:
                self.scrape_url(url)
            except: pass
        self.browser.close()

        if do_verbose_output is True:
            print("Done scraping this league.")

    def getLeague(self,url):
        league = url.split('/')[5]
        if ('-2' in league):
            league = league[0:league.find('-2')]
        return league

    def getSeason(self,url):
        league = url.split('/')[5]
        if ('-2' in league):
            season = league[league.find('-2')+1:]
        else: season = "2017-2018"
        return season

    def getScore(self,tag):
        score = tag.find(class_="result").findChildren()[1].string
        return score

    def getCountry(self,url):
        return url.split('/')[4]


    def getBookmakers(self,tag):
        numOfBookmakers = len(tag.find_all(class_="name2"))
        bookmakers= tag.find_all(class_="name")[1:numOfBookmakers+1]
        return list(map(lambda x:x.text,bookmakers))

    def getDataQuotePerSegnoDC(self,bookmaker,quota):
        if(quota=='1X'):
            data = self.browser.find_elements_by_xpath("//*[contains(text(),'"+bookmaker+"')]")[0].find_elements_by_xpath('../../../td[2]')[0]
        elif (quota=='X2'):
            data = self.browser.find_elements_by_xpath("//*[contains(text(),'"+bookmaker+"')]")[0].find_elements_by_xpath('../../../td[3]')[0]
        else: data = self.browser.find_elements_by_xpath("//*[contains(text(),'"+bookmaker+"')]")[0].find_elements_by_xpath('../../../td[4]')[0]
        hov = ActionChains(self.browser).move_to_element(data)
        hov.perform()
        quoteData = list(filter(lambda x: x!='' and x!='Opening odds:',self.browser.find_elements_by_class_name("spc-nowrap")[0].get_attribute("innerText").split('\n')))
        return quoteData


    def getDataQuotePerSegno1X2(self,bookmaker,quota):
        if(quota=='1'):
            data = self.browser.find_elements_by_xpath("//*[contains(text(),'"+bookmaker+"')]")[0].find_elements_by_xpath('../../../td[2]')[0]
        elif (quota=='X'):
            data = self.browser.find_elements_by_xpath("//*[contains(text(),'"+bookmaker+"')]")[0].find_elements_by_xpath('../../../td[3]')[0]
        else: data = self.browser.find_elements_by_xpath("//*[contains(text(),'"+bookmaker+"')]")[0].find_elements_by_xpath('../../../td[4]')[0]
        hov = ActionChains(self.browser).move_to_element(data)
        hov.perform()
        quoteData = list(filter(lambda x: x!='' and x!='Opening odds:',self.browser.find_elements_by_class_name("spc-nowrap")[0].get_attribute("innerText").split('\n')))
        return quoteData

    def findDropOdds(self, book, country, league, season, match_date, current_date_str, current_date_unix, score, participants,url):
        dataAndQuote1=self.getDataQuotePerSegno1X2(book,'1')
        dataAndQuoteX=self.getDataQuotePerSegno1X2(book,'X')
        dataAndQuote2=self.getDataQuotePerSegno1X2(book,'2')

        quotaFinaleIniziale1 =(dataAndQuote1[0:1][0],dataAndQuote1[-1:][0])
        quotaFinaleInizialeX =(dataAndQuoteX[0:1][0],dataAndQuoteX[-1:][0])
        quotaFinaleIniziale2 =(dataAndQuote2[0:1][0],dataAndQuote2[-1:][0])
        data = quotaFinaleIniziale1[0][:quotaFinaleIniziale1[0].find(':')+4]
        quotaFinaleIniziale1=(float(quotaFinaleIniziale1[0][len(data):len(data)+4]),float(quotaFinaleIniziale1[1][len(data):len(data)+4]))
        quotaFinaleInizialeX=(float(quotaFinaleInizialeX[0][len(data):len(data)+4]),float(quotaFinaleInizialeX[1][len(data):len(data)+4]))
        quotaFinaleIniziale2=(float(quotaFinaleIniziale2[0][len(data):len(data)+4]),float(quotaFinaleIniziale2[1][len(data):len(data)+4]))
        #print(country+" "+league+" "+season+" "+current_date_str+" "+ str(current_date_unix)+" "+score +" "+ str(participants)+" "+ book+" 1 "+dataWithYear+" "+str(dataUnix)+" "+str(quota)," ",url)
        drop1 = (quotaFinaleIniziale1[0]-quotaFinaleIniziale1[1])/max(quotaFinaleIniziale1[0],quotaFinaleIniziale1[1]) * 100
        dropX = (quotaFinaleInizialeX[0]-quotaFinaleInizialeX[1])/max(quotaFinaleInizialeX[0],quotaFinaleInizialeX[1]) * 100
        drop2 = (quotaFinaleIniziale2[0]-quotaFinaleIniziale2[1])/max(quotaFinaleIniziale2[0],quotaFinaleIniziale2[1]) * 100
        self.db_manager.add_dropodds(country, league, season, current_date_str,
         str(current_date_unix), score,participants[0],participants[1],book,
         str(quotaFinaleIniziale1[1]),str(quotaFinaleInizialeX[1]),str(quotaFinaleIniziale2[1]),
         str(quotaFinaleIniziale1[0]),str(quotaFinaleInizialeX[0]),str(quotaFinaleIniziale2[0]),
         str(drop1),str(dropX),str(drop2),
         url)


    def findAndSaveQuota(self, book, segno, country, league, season, match_date, current_date_str, current_date_unix, score, participants,url):
        dataAndQuote=None
        if (segno=='1' or segno == '2' or segno =='X'):
            dataAndQuote=self.getDataQuotePerSegno1X2(book,segno)
        if (segno =='1X' or segno == 'X2' or segno == '12'):
            dataAndQuote = self.getDataQuotePerSegnoDC(book,segno)
        if (dataAndQuote != None):
            for q in dataAndQuote:
                    data = q[:q.find(':')+4]
                    dataWithYear = (data+str(match_date.today().year)).replace(',','')
                    dataUnix = calendar.timegm(datetime.strptime(dataWithYear, "%d %b %H:%M %Y").utctimetuple())
                    quota = float(q[len(data):len(data)+4])
                    #print(country+" "+league+" "+season+" "+current_date_str+" "+ str(current_date_unix)+" "+score +" "+ str(participants)+" "+ book+" 1 "+dataWithYear+" "+str(dataUnix)+" "+str(quota)," ",url)
                    self.db_manager.add_surebet(country, league, season, current_date_str, str(current_date_unix), score,participants[0],participants[1],book,segno,str(quota),dataWithYear,str(dataUnix), url)


    def saveQuote1X2(self, url, country, league, season, current_date_str, date, current_date_unix, participants, score, book):
        self.findAndSaveQuota(book, "1", country, league, season, date, current_date_str, current_date_unix, score, participants, url)
        self.findAndSaveQuota(book, "X", country, league, season, date, current_date_str, current_date_unix, score, participants, url)
        self.findAndSaveQuota(book, "2", country, league, season, date, current_date_str, current_date_unix, score, participants, url)


    def saveQuoteDC(self, url, country, league, season, current_date_str, date, current_date_unix, participants, score, book):
        self.findAndSaveQuota(book, "1X", country, league, season, date, current_date_str, current_date_unix, score, participants, url)
        self.findAndSaveQuota(book, "X2", country, league, season, date, current_date_str, current_date_unix, score, participants, url)
        self.findAndSaveQuota(book, "12", country, league, season, date, current_date_str, current_date_unix, score, participants, url)


    def scrape_url(self, url):
        """
        Scrape the data for every match on a given URL and insert each into the
        database.

        Args:
            url (str): URL to scrape data from.
        """
        try:
            self.browser.get(url)
            tbl_html = self.browser.find_element_by_id("col-content").get_attribute("innerHTML")
            tbl_match = BeautifulSoup(tbl_html, "html.parser")

            country= self.getCountry(url)
            league = self.getLeague(url)
            season = self.getSeason(url)

            current_date_str = self.get_date(tbl_match).replace('  ',' ')
            date = datetime.strptime(current_date_str[current_date_str.find(',')+1:], " %d %b %Y, %H:%M")
            current_date_unix = calendar.timegm(date.utctimetuple())

            participants = self.get_participants(tbl_match)
            score=self.getScore(tbl_match)

            bookmakers = self.getBookmakers(tbl_match)
            for book in bookmakers:
                #Surebet
                self.saveQuote1X2(url, country, league, season, current_date_str, date, current_date_unix, participants, score, book)
                self.findDropOdds(book, country, league, season, date, current_date_str, current_date_unix, score, participants,url)
            try:
                self.browser.find_element_by_id('tab-sport-others').click()
                data = self.browser.find_elements_by_xpath("//*[contains(text(),'Double Chance')]")[0]
            except:
                try:
                    data = self.browser.find_elements_by_xpath('//*[@title="Double Chance"]')[0]
                except:
                    data = None
            finally:
                if(data!=None):
                    data.click()
                    # E' importante aspettare che la formazione della pagina sia completa
                    # e cercare nuovamente la tabella: altrimenti trova i book delle quote 1,2 e X
                    # e non quelle delle doppie chances
                    WebDriverWait(self.browser, 20).until(
                        EC.element_to_be_clickable((By.XPATH,  "//*[@class='name2'][1]")))
                    tbl_html = self.browser.find_element_by_id("col-content").get_attribute("innerHTML")
                    tbl = BeautifulSoup(tbl_html, "html.parser")
                    bookmakers = self.getBookmakers(tbl)
                    for book in bookmakers:
                        #Surebet
                        self.saveQuoteDC(url, country, league, season, current_date_str, date, current_date_unix, participants, score, book)
                else:
                    print('[DEBUG] Unable to find double chances...')

        except Exception as e:
            print(e)
        finally:
            self.browser.close()


    def get_date(self, tag):
        """
        Extract the date from an HTML tag for a date row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (str) Extracted date string.
        """

        this_date = tag.find(class_="datet").string
        if "Today" in this_date:
            return "Today"
        elif this_date.endswith(" - Play Offs"):
            this_date = this_date[:-12]
        return this_date

    def get_time(self, tag):
        """
        Extract the time from an HTML tag for a soccer match row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (str) Extracted time.
        """

        return tag.find(class_="datet").string

    def get_participants(self, tag):
        """
        Extract the match's participants from an HTML tag for a soccer match
        row.

        Args:
            tag (obj): HTML tag object from BeautifulSoup.

        Returns:
            (list of str) Extracted match participants.
        """
        parsed_strings = tag.findChildren()[0].text.split(" - ")
        participants = []
        participants.append(parsed_strings[0])
        participants.append(parsed_strings[-1])
        return participants

    def get_urlMatch(self, tag):
        """
        return match url
        """

        with open('matches/urls', 'a') as outfile:
            outfile.write('http://www.oddsportal.com'+tag.find_all("a")[0]['href']+'\n')


scraper = Scraper(True)
scraper.scrape_url("http://www.oddsportal.com/soccer/ecuador/serie-a/independiente-del-valle-dep-cuenca-KW7lI2H9/")
