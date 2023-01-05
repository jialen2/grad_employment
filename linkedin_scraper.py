#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, getopt
import os 
import time
import random
from selenium import webdriver
SwitchAccuntThrehold = 20

class AccountIterator:
    def __init__(self, accounts):
        self.accounts = accounts
        self.currIdx = 0
    def empty(self):
        return len(self.accounts) == 0
    def size(self):
        return len(self.accounts)
    def curr(self):
        return self.accounts[self.currIdx]
    def remove_curr(self):
        self.accounts.pop(self.currIdx)
    def next(self):
        self.currIdx = (self.currIdx + 1) % len(self.accounts)
        return self.accounts[self.currIdx]

class LinkedinScraper:
    def __init__(self, visible=False):
        self.visible = visible

    def setupWebDriver(self):
        chromedriver_path = "./chromedriver"
        option = webdriver.ChromeOptions()
        if not self.visible:
            option.add_argument(' — incognito')
            option.add_argument('--no - sandbox')
            option.add_argument('--window - size = 1420, 1080')
            option.add_argument('--headless')
            option.add_argument('--disable - gpu')
            option.add_argument('Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664S.45 Safari/537.36')
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=option)

    def login(self, account, password):
        self.driver.get('https://www.linkedin.com/')
        time.sleep(2)
        inputElement = self.driver.find_element('id', 'session_key')
        for i in account:
            inputElement.send_keys(i)
            # time.sleep(random.uniform(0.2, 0.5))
        inputElement = self.driver.find_element('id', 'session_password')
        for i in password:
            inputElement.send_keys(i)
            # time.sleep(random.uniform(0.2, 0.5))
        submit_button = self.driver.find_elements('xpath', '/html/body/main/section[1]/div/div/form/button')[0]
        submit_button.click()
        time.sleep(2)

    def readAccountFromFile(self):
        accounts = []
        with open("fake_accounts.txt", "r") as input:
            for line in input:
                account, password = line.replace("\n", "").split(",")
                accounts.append((account, password))
        return accounts

    # Set up the web driver and login to the first account
    def start(self):
        self.chromeDriverPath = "./chromedriver"
        self.setupWebDriver()
        accounts = self.readAccountFromFile()
        self.accountIterator = AccountIterator(accounts)
        account, password = self.accountIterator.curr()
        self.login(account, password)
        self.countNumScrape = 0
        with open("problematic_accounts.txt", "w") as output:
            output.write("")
    
    # Scrape the url and return the html as string. If no remaining accounts to scrape or switch to (see below), return ""
    # To avoid scraping too frequently, switch account when reach SwitchAccuntThrehold limit.
    def scrape(self, url):
        if self.accountIterator.empty():
            return False, "No remaining account"
        if self.countNumScrape % SwitchAccuntThrehold == 0 and self.countNumScrape > 0:
            print("current num of scraped urls:", self.countNumScrape)
            if self.accountIterator.size() < 2:
                return False, "No accounts to switch to"
            account, password = self.accountIterator.next()
            self.login(account, password)
            print("switched to account", account)
        self.driver.get(url)
        time.sleep(2)
        return True, str(self.driver.page_source)
    
    # If fail to scrape, then probably the current account has been banned. Delete the current account and switch to the next account and login if any.
    # Also, save the problematic accounts so that the problem can be referred back and solved later.
    def reportFailure(self, page_source):
        with open("debug/problematic_accounts.txt", "w") as output:
            account, password = self.accountIterator.curr()
            output.write(account+","+password+"\n")
        self.accountIterator.remove_curr()
        if not self.accountIterator.empty():
            account, password = self.accountIterator.next()
            self.setupWebDriver()
            self.login(account, password)
        with open("debug/" + account + ".html", "w") as output:
            output.write(page_source)
    
    def get_curr_account(self):
        return self.accountIterator.curr()
        
