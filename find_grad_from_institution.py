from linkedin_scraper import LinkedinScraper
from google_search import get_links_on_google
from selenium.webdriver.common.keys import Keys
import time
import random
import datetime
import os
def change_major(scraper, major):
    inputElement = scraper.driver.find_element('id', 'people-search-keywords')
    for i in major:
        inputElement.send_keys(i)
        time.sleep(random.uniform(0.2, 0.5))
    inputElement.send_keys('\n')
    time.sleep(5)

def change_num_year(scraper, numYear):
    currYear = datetime.date.today().year
    startYear = currYear - numYear + 1
    inputElement = scraper.driver.find_element('id', 'people-search-year-start')
    for i in str(startYear):
        inputElement.send_keys(i)
        time.sleep(random.uniform(0.2, 0.5))
    inputElement.send_keys('\n')
    time.sleep(5)

def enter_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    os.chdir(dir)

def enter_storage_dir(institution):
    curr_path = os.getcwd()
    # Get into the directory for all alumni name list data. If not exist, create one.
    alumni_dir_path = curr_path + "/alumni_name_lst"
    enter_dir(alumni_dir_path)
    # Get into the directory for the institution. If not exist, create one.
    alumni_institution_path = alumni_dir_path + "/" + institution
    enter_dir(alumni_institution_path)
    
def store_alumni_in_file(alumni_lst, institution, major):
    curr_dir = os.getcwd()
    enter_storage_dir(institution)
    major = major.replace(" ", "_")
    with open(major+".txt", "w") as output:
        for alumni in alumni_lst:
            output.write(alumni+"\n")
    os.chdir(curr_dir)

def find_grad_from_institution(institution, major, numYear, numPeople, visited_names):
    if numPeople == 0:
        return
    scraper = LinkedinScraper(True)
    scraper.start()
    scraper.driver.maximize_window()
    query = institution + " alumni linkedin"
    url = get_links_on_google(query)[0]
    scraper.driver.get(url)
    time.sleep(5)
    if major != "":
        change_major(scraper, major)
    if numYear != -1:
        change_num_year(scraper, numYear)
    alumni_lst, visited_names = find_alumni(scraper, numPeople, visited_names)
    store_alumni_in_file(alumni_lst, institution, major)

def read_black_list_from_file():
    black_list = []
    with open("black_list.txt", "r") as input:
        for line in input:
            black_list.append(line.replace("\n", ""))
    return black_list    

def find_alumni(scraper, numPeople, visited_names):
    black_list = read_black_list_from_file()
    alumni_li_path = 'html/body/div[@class="application-outlet"]/div[@class="authentication-outlet"]/div[1]/div[2]/div[1]/div[2]/main/div[2]/div[1]/div[2]/div/div[1]/ul/li'
    alumni_name_path = alumni_li_path + '[{idx}]/div/section/div/div/div[2]/div[1]/a/div'
    alumni_lst = []
    idx = 0
    num_invalid = 0
    while len(alumni_lst) < numPeople:
        alumni_in_page = len(scraper.driver.find_elements("xpath", alumni_li_path))
        while idx < alumni_in_page and len(alumni_lst) < numPeople:
            try:
                curr_alumni = scraper.driver.find_element("xpath", alumni_name_path.format(idx=idx+1)).text
                if curr_alumni in visited_names or curr_alumni in black_list:
                    idx += 1
                    continue
                visited_names[curr_alumni] = True
                alumni_lst.append(curr_alumni)
            except Exception as e:
                num_invalid += 1
            idx += 1
        for i in range(10):
            scraper.driver.find_element("tag name", 'body').send_keys(Keys.END)
            time.sleep(1)
        time.sleep(5)
        print("current name lst length: ", len(alumni_lst))
    print(len(alumni_lst))
    print(alumni_lst)
    return alumni_lst, visited_names

    

# find_grad_from_institution("Heritage Institute of Technology", "computer science", 10)
# find_grad_from_institution("Heritage Institute of Technology", "Electronics and Communication Engineering", 10)