import os
from os.path import exists
import shutil
from linkedin_scraper import LinkedinScraper
from google_search import get_links_on_google
from html_parser import parse_html_string
from background_parser import parse_background_info
import json

root_dir = os.getcwd()
def enter_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    os.chdir(dir)

# # If not exist, create a file copy for the name list for a major under an institution.
# # The temp files are used to record the scraping process (after done scraping a person, the name will be deleted) 
# # The temp files will be stored as temp/[institution]/[major]
# def create_temp_file_if_not_exist(institution, major):
#     # Get into the directory for all alumni name list data. If not exist, create one.
#     temp_dir_path = root_dir + "/temp"
#     enter_dir(temp_dir_path)
#     # Get into the directory for the institution. If not exist, create one.
#     temp_institution_path = temp_dir_path + "/" + institution
#     enter_dir(temp_institution_path)
#     major = major.replace(" ", "_")
#     if not exists(major+".txt"):
#         src_dir = root_dir + "/alumni_name_lst/" + institution + "/" + major + ".txt"
#         dest_dir = root_dir + "/temp/" + institution + "/" + major + ".txt"
#         shutil.copy(src_dir, dest_dir)
#     enter_dir(root_dir)

def enter_storage_dir(institution, major):
    # Get into the directory for all alumni profile data. If not exist, create one.
    profile_dir_path = root_dir + "/alumni_profile"
    enter_dir(profile_dir_path)
    # Get into the directory for the institution. If not exist, create one.
    profile_institution_path = profile_dir_path + "/" + institution
    enter_dir(profile_institution_path)
    # Create the file for the major if the file does not exist
    major = major.replace(" ", "_")
    profile_major_file = major + ".csv"
    if not exists(profile_major_file):
        with open(profile_major_file, "w") as output:
            output.write("")   

def store_profile_in_file(alumni_name, education, experience, institution, major):
    enter_storage_dir(institution, major)
    profile_file = major.replace(" ", "_") + ".csv"
    if os.path.getsize(profile_file) == 0:
        profile_data = {}
    else:
        file_d = open(profile_file, "r")
        profile_data = json.load(file_d)
        file_d.close()
    with open(profile_file, "w") as output:
        profile_data[alumni_name] = {'Education': education, 'Experience': experience}
        json.dump(profile_data, output, indent=4,ensure_ascii=False)
    enter_dir(root_dir)

def delete_line_after_scraping(filePath, lineToDelete):
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
    # if len(allLine) == 0:
    #     os.remove(filePath)
    #     with open("success_file", "a") as output:
    #         output.write(filePath+'\n')

# Scrape the career history about alumni in the files under alumni_name_lst directory in Linkedin. 
def collect_grad_profile(institution, major, visited_names):
    scraper = LinkedinScraper(True)
    scraper.start()
    alumni_lst = []
    major = major.replace(" ", "_")
    alumni_file_dir = os.getcwd() + "/alumni_name_lst/" + institution + "/" + major + ".txt"
    with open(alumni_file_dir,"r") as input:
        for alumni_name in input:
            alumni_lst.append(alumni_name)
    for alumni_name in alumni_lst:
        original_line = alumni_name
        alumni_name = alumni_name.replace("\n","").strip()
        visited_names[alumni_name] = True
        try:
            query = alumni_name + " " + institution + " linkedin"
            print("query:", query)
            url = get_links_on_google(query)[0]
        except:
            print("Unable to search on Google. Check Internet.")
            exit(0)
        # Scrape the profile for the current alumni
        success, content = scraper.scrape(url)
        if not success:
            print(content)
            exit(0)
        html = parse_html_string(content)
        (education, found_education), (experience, found_experience) = parse_background_info(html)
        if (education == [] and experience == []) and (not found_experience and not found_education):
            print("found failure at " + scraper.get_curr_account()[0] + " " + alumni_name)
            scraper.reportFailure(content)
        else:
            store_profile_in_file(alumni_name, education, experience, institution, major)
        delete_line_after_scraping(alumni_file_dir, original_line)            

# collect_grad_profile("Heritage Institute of Technology", "Electronics and Communication Engineering")