from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
import json
import random
import sys
import atexit
from get_background import get_background_info

from bs4 import BeautifulSoup

current_directory = os.path.dirname(os.path.realpath(__file__))

driver = None

url = None

sys.path.insert(1, current_directory+'/../helper')

account_num = {}

# sys.path.insert(1, '../helper')

from get_html import parse_html_string, get_links_on_google


# name_list: a list of names
# university: university of faculty members
# linkedin_email: email address used to log in a linkedin account
# linkedin_password: password used to log in a linkedin account
# this function first log in with linkedin_email and linkedin_password so we can get access to full profiles on linkedin
#
# return: {
#   faculty1: {'education': [...], 'experience': [...]},
#   faculty2: {'education': [...], 'experience': [...]},
#   ...
# }
def readLinkedInAccountFromFile(filePath):
    accounts = []
    with open(filePath, "r") as input:
        for line in input:
            accounts.append(line.replace("\n", "").strip())
    return accounts
    
def writeAccountNumToFile():
    with open("account_num.txt", "w") as output:
        for key in account_num.keys():
            output.write(key+","+str(account_num[key])+"\n")
    
def exit_handler():
    writeAccountNumToFile()

atexit.register(exit_handler)
def add_invisiable_argument(option):
    option.add_argument(' — incognito')
    option.add_argument('--no - sandbox')
    option.add_argument('--window - size = 1420, 1080')
    option.add_argument('--headless')
    option.add_argument('--disable - gpu')
    option.add_argument('Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664S.45 Safari/537.36')

def setupWebDriver(chromedriver_path, test):
    global driver
    if driver:
        driver.quit()
        time.sleep(30)
    option = webdriver.ChromeOptions()
    if not test:
        option.add_argument(' — incognito')
        option.add_argument('--no - sandbox')
        option.add_argument('--window - size = 1420, 1080')
        option.add_argument('--headless')
        option.add_argument('--disable - gpu')
        option.add_argument('Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664S.45 Safari/537.36')
    driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=option)

def login(linkedin_email, linkedin_password, test):
    driver.get('https://www.linkedin.com/')
    # with open("helper/login_page.html", "w") as output:
    #     output.write(BeautifulSoup(driver.page_source, 'html.parser').prettify())
    # exit()
    time.sleep(2)
    inputElement = driver.find_element_by_id('session_key')
    for i in linkedin_email:
        inputElement.send_keys(i)
        time.sleep(random.uniform(0.2, 0.5))
    inputElement = driver.find_element_by_id('session_password')
    for i in linkedin_password:
        inputElement.send_keys(i)
        time.sleep(random.uniform(0.2, 0.5))
    submit_button = driver.find_elements_by_xpath('/html/body/main/section[1]/div/div/form/button')[0]
    submit_button.click()
    if test:
        time.sleep(90)
    else:
        time.sleep(2)

# When the number we switch reach the threhold, we switch account.
SwitchAccuntThrehold = 20

# List of useable linked Account for scraping.
linkedInAccountFilePath = current_directory + "/../../linkedin_account.txt"
linkedInAccounts = readLinkedInAccountFromFile(linkedInAccountFilePath)

def long_sleep_if_needed(countNumScrape):
    if countNumScrape % 26 == 0:
        print("###############long sleep#################")
        time.sleep(random.randint(120, 150))
def readAccountNum():
    with open("account_num.txt", "r") as input:
        for line in input:
            account, num = line.split(",")
            account_num[account] = int(num)
    return account_num

def deleteLineAfterScraping(filePath, lineToDelete):
    lineToDelete = lineToDelete.replace("\n", "")
    allLine = []
    with open(filePath, "r") as input:
        for line in input:
            if line.replace("\n", "") != lineToDelete:
                allLine.append(line)
    index = 0
    with open(filePath, "w") as output:
        for line in allLine:
            line = line.replace("\n","").strip()
            output.write(line)
            if index != len(allLine)-1:
                output.write("\n")
            index += 1
    if len(allLine) == 0:
        os.remove(filePath)
        with open("success_file", "a") as output:
            output.write(filePath+'\n')
    
def scrape_data_from_linkedin(faculty_file_path, major, chromedriver_path, test):
    global url
    readAccountNum()
    countNumScrape = 0
    currAccount = ""
    linkedInAccountIndex = -1
    university_list = os.listdir(faculty_file_path)
    for university in university_list:
        filePath = faculty_file_path+"/"+university
        faculty_list = []
        if filePath.split("/")[-1] == ".DS_Store":
            continue
        with open(filePath,"r") as input:
            for faculty_name in input:
                faculty_list.append(faculty_name)
        store_file_path = current_directory+"/../../"+major+"/"+university+".json"
        for faculty_name in faculty_list:
            originalLine = faculty_name
            faculty_name = faculty_name.replace("\n","").strip()
            # If already signed in and have only one account available, skip switching account.
            if countNumScrape % SwitchAccuntThrehold == 0 and (currAccount == "" or len(linkedInAccounts) > 1):
                linkedInAccountIndex = (linkedInAccountIndex+1) % len(linkedInAccounts)
                currAccount = linkedInAccounts[linkedInAccountIndex]
                setupWebDriver(chromedriver_path, test)
                login(currAccount, "319133abcd", test)
                print("Switched Account to: ", currAccount)
            countNumScrape += 1
            try:
                get_background_on_linkedin(university, faculty_name, store_file_path)
                account_num[currAccount] = account_num.get(currAccount, 0) + 1
                deleteLineAfterScraping(filePath, originalLine)
            except Exception as e:
                with open("failed_data.txt", "a") as output:
                    output.write('"' + faculty_name + '"'+ " " + '"' + university + '"'+ " " + str(type(e)))
                    output.write("\n")
                    print(str(e))

                # If met some error with the store file, switch a university to scrape.
                if type(e).__name__ == "JSONDecodeError":
                    long_sleep_if_needed(countNumScrape)
                    break

                # If the current account failed to scrape infomation, switch an account.
                elif type(e).__name__ == "AssertionError" or type(e).__name__ == "MaxRetryError":
                    # When an account failed to perform, record the account and the url it fails on.
                    with open("failed_accounts.txt", "a") as output:
                        output.write(linkedInAccounts[linkedInAccountIndex] + " " + url + "\n")
                    del linkedInAccounts[linkedInAccountIndex]
                    if len(linkedInAccounts) == 0:
                        driver.quit()
                        return
                    linkedInAccountIndex = linkedInAccountIndex % len(linkedInAccounts)
                    setupWebDriver(chromedriver_path, test)
                    login(linkedInAccounts[linkedInAccountIndex], "319133abcd", test)
                    print("Switched Account to: ", linkedInAccounts[linkedInAccountIndex])
            long_sleep_if_needed(countNumScrape)
    driver.quit()

def get_background_on_linkedin(university, faculty_name, store_file_path):
    global url
    education = []
    experience = [] 

    def write_to_file(status):
        try:
            with open(store_file_path, "r+") as file:
                if os.path.getsize(store_file_path) == 0:
                    json.dump({}, file, indent=4,ensure_ascii=False)  
        except:
            with open(store_file_path, "a+") as file:
                json.dump({}, file, indent=4,ensure_ascii=False)    
        with open(store_file_path, "r+") as file:
            file_data = json.load(file)
            file_data[faculty_name] = {'status': status, 'Education': education, 'Experience': experience}
            file.seek(0)
            json.dump(file_data, file, indent=4,ensure_ascii=False)

    try:
        query = faculty_name + " " + university + " linkedin"
        print("query:", query)
        url = get_links_on_google(query)[0]
    except:
        write_to_file("fail")
        print('fail to get url for {}'.format(faculty_name))
        return

    print(url)
    if 'linkedin.com' not in url or "pub/dir/" in url or "/in/" not in url:
        write_to_file("fail")
        print('cannot find linkedin page for {}'.format(faculty_name))
        return
    driver.get(url)
    time.sleep(2)
    # print(BeautifulSoup(html_string, 'html.parser').prettify())
    html = parse_html_string(str(driver.page_source))
    (education, found_education), (experience, found_experience) = get_background_info(html)
    print('Education:')
    print(education)
    print('Experience:')
    print(experience)
    if education == [] and experience == []:
        print(found_education, found_experience)
        if found_experience or found_education:
            write_to_file("fail")
            print('cannot find infos about {}'.format(faculty_name))
            return
        with open("problematic.html", "w") as output:
            output.write(BeautifulSoup(driver.page_source, 'html.parser').prettify())
        assert False
    write_to_file("success")
    time.sleep(random.randint(45, 60))


# # example
# # l = '''
# # Tarek Abdelzaher
# # Sarita V. Adve
# # Vikram Adve
# # Gul A. Agha
# # Abdussalam Alawini
# # '''

# l = '''
# Ian Savage
# '''
# # before running this function, please go to LinkedIn and sign in with the following account
# l = l.split('\n')[1:-1]
# print(l)

# faculty_list_dir = current_directory+"/../../faculty_list/economy"
# webdriver_file_path = current_directory + "/../../chromedriver_Linux98"
# # print(l)
# # exit()
# result = scrape_data_from_linkedin(faculty_list_dir, "economy", webdriver_file_path)
# print(json.dumps(result, indent=4))
# setupWebDriver("/Users/jialening/Desktop/Faculty_Movement/scrape/chromedriver_local")
# login("", "")

