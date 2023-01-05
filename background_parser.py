from errno import EDQUOT
import re
import os
import math
from curses.ascii import isalpha, isdigit
from datetime import datetime
current_directory = os.path.dirname(os.path.realpath(__file__))
# extract experience from the parsed html
def get_experience_with_tags(html):
    res = []
    tag_stack = []
    education_area = False
    cur_education = []
    hidden = ''
    for line in html:
        # sign of experience field
        if 'pv-entity__position-group-pager pv-profile-section__list-item ember-view' in line:
            education_area = True
        # if education_area:
        #     print("Found Experience")
        if education_area:
            if line[:4] == '<img' or line[:3] == '<br' or line[:2] == '<!':
                continue
            if len(line) > 2 and line[:2] == '</':
                tag_stack.pop()
                if not tag_stack:
                    res.append(cur_education)
                    cur_education = []
                    education_area = False
            elif len(line) > 2 and line[:1] == '<' and line[1] != '!':
                if 'visually-hidden' in line:
                    tag_stack.append('<span class="visually-hidden">')
                else:
                    tag_stack.append(line.split()[0] + '>')
            else:
                tmp = line.strip()
                if not tmp or line[:2] == '<!' or 'visually-hidden' in tag_stack[-1]:
                    if 'visually-hidden' in tag_stack[-1]:
                        hidden = tmp
                    continue
                if hidden:
                    cur_education.append([hidden, line.strip()])
                    hidden = ''
                else:
                    cur_education.append(line.strip())
    return res

def get_education_with_tags(html):
    res = []
    tag_stack = []
    education_area = False
    cur_education = []
    hidden = ''
    dates = False
    for line in html:
        if 'pv-profile-section__list-item pv-education-entity pv-profile-section__card-item ember-view' in line:
            education_area = True
        # if education_area:
        #     print("Found Education")
        if education_area:
            if line[:4] == '<img' or line[:3] == '<br' or line[:2] == '<!':
                continue
            if len(line) > 2 and line[:2] == '</':
                tag_stack.pop()
                if not tag_stack:
                    res.append(cur_education)
                    cur_education = []
                    education_area = False
            elif len(line) > 2 and line[:1] == '<' and line[1] != '!':
                if 'visually-hidden' in line:
                    tag_stack.append('<span class="visually-hidden">')
                else:
                    tag_stack.append(line.split()[0] + '>')
            else:
                tmp = line.strip()
                if not tmp or line[:2] == '<!' or 'visually-hidden' in tag_stack[-1]:
                    if 'visually-hidden' in tag_stack[-1]:
                        hidden = tmp
                    continue
                if hidden:
                    cur_education.append([hidden, line.strip()])
                    hidden = ''
                else:
                    line = line.strip()
                    if line == '–':
                        cur_education[-1][-1] += ' – '
                        dates = True
                    elif dates:
                        cur_education[-1][-1] += line
                        dates = False
                    else:
                        line = line.replace('–', '–')
                        cur_education.append(line)
    return res

# Given "Sep 2019 - Feb 2021" Return ["Sep", "Feb"]
def extractWords(dateStr):
    wordList = []
    word = ""
    for char in dateStr:
        if isalpha(""+char):
            word += char
        elif word != "":
            wordList.append(word)
            word = ""
    return wordList

def checkIfValidMonth(dateStr):
    wordList = extractWords(dateStr)
    monthsMap = read_month_info_from_file()
    validWords = []
    for key in monthsMap.keys():
        validWords.append(key)
    validWords.append("Present")
    for word in wordList:
        isValid = False
        for key in monthsMap.keys():
            if key == word or key.lower() == word:
                isValid = True
                break
        if not isValid:
            return False
    return True
                

def isValidDate(dateStr):
    # Maximum possible string: "Sep 2019 - Oct 2021"
    if len(dateStr) > 19:
        return False

    # Given String like "Developed Quickshift, 2008", should return False
    if not checkIfValidMonth(dateStr):
        return False
    
    found = False
    for i in range(3,len(dateStr)):
        numStr = dateStr[i-3:i+1]
        numStart = numStr[0:2]
        if (numStart == "19" or numStart == "20") and isdigit(numStr[2]) and isdigit(numStr[3]):
            found = True
    return found

def read_month_info_from_file():
    months = {}
    with open(current_directory+"/month_info.txt", "r") as input:
        for line in input:
            month, num = line.split(",")
            months[month] = int(num)
    return months

# given a string in the form of "Jan 2019", return its (year, month) formatted result like (2019, 1)
def parse_time_string(timeStr):
    timeStr = timeStr.strip()
    splittedTime = timeStr.split(" ")
    year = -1
    month = -1
    present = "Present"
    # if we got two part in the timeStr, try to find month in each part.
    if len(splittedTime) == 2:
        months = read_month_info_from_file()
        for timeInfo in splittedTime:
            num = -1
            for m in months:
                if m in timeInfo or m.lower() in timeInfo:
                    num = months[m]
            if num == -1:
                year = int(timeInfo)
            else:
                month = num
    elif len(splittedTime) == 1:
        if present in timeStr or present.lower() in timeStr:
            year = datetime.now().year
            month = datetime.now().month
        else:
            year = int(timeStr)
    else:
        print("Find malformed Data")
    # If we don't find month info, we assume month is June
    if month == -1:
        return (year, 6)
    else:
        return (year, month)

# Sample input: "Feb 2019 - Dec 2020"
# Return: [(2019, 2), (2020, 12)]
# Sample input: "Feb 2019"
# Return: [(2019, 2), (2022, 3)] -> current time
def trim_time(time):
    slashes = ["–", "-", "―", "‐"]
    for slash in slashes:
        if slash in time:
            startTime = time.split(slash)[0]
            endTime = time.split(slash)[1]
            startTime = parse_time_string(startTime)
            endTime = parse_time_string(endTime)
            return [startTime, endTime]
    time = parse_time_string(time)
    currentTime = (datetime.now().year, datetime.now().month)
    return [time, currentTime]

# Return 1 if firstInterval is before the second one
# Return -1 if firstInterval is after the second one
# Return 0 if they are the same
def compare_time(firstTime, secondTime):
    if firstTime[0] < secondTime[0]:
        return 1
    elif firstTime[0] > secondTime[0]:
        return -1
    elif firstTime[1] < secondTime[0]:
        return 1
    elif firstTime[1] > secondTime[0]:
        return -1
    else:
        return 0

# Given [[(2019, 2), (2020, 12)], [(2020, 8), (2021, 3)], [(2018, 2), (2018, 7)]], return "Feb 2018 - Mar 2021"
def merge_time_interval(timeIntervals):
    startTime = (math.inf, math.inf)
    endTime = (-math.inf, -math.inf)
    for interval in timeIntervals:
        result = compare_time(interval[0], startTime)
        if result == 1:
            startTime = interval[0]
        result = compare_time(interval[1], endTime)
        if result == -1:
            endTime = interval[1]
    return [startTime, endTime]

# Given 1, return Jan
def convertMonthNumToStr(num):
    monthsMap = read_month_info_from_file()
    for key, val in monthsMap.items():
        if val == num:
            return key
    return None

# Given [(2019, 2), (2020, 12)], return "Feb 2019 - Dec 2020"
def convertIntervalFromNumToStr(numInterval):
    startTime = convertMonthNumToStr(numInterval[0][1]) + " " + str(numInterval[0][0])
    endTime = convertMonthNumToStr(numInterval[1][1]) + " " + str(numInterval[1][0])
    return startTime + " - " + endTime

def add_tag_to_experience_list(curr_experience):
    new_experience_list = []
    timeIntervals = []
    for i in range(len(curr_experience)):
        curr_info = curr_experience[i]
        time = curr_info.split("·")[0].strip()
        if isValidDate(time):
            timeInterval = trim_time(time)
            timeIntervals.append(timeInterval)
    companyName = ""
    position = ""
    if len(timeIntervals) > 1:
        companyName = curr_experience[0].strip()
    else:
        position = curr_experience[0]
        companyName = curr_experience[1].split('·')[0].strip()
    if position != "":
        new_experience_list.append(position)
    new_experience_list.append(["Company Name", companyName])
    finalTimeInterval = merge_time_interval(timeIntervals)
    if finalTimeInterval[0] != (math.inf, math.inf) and finalTimeInterval[1] != (-math.inf, -math.inf):
        intervalStr = convertIntervalFromNumToStr(finalTimeInterval)
        new_experience_list.append(["Dates Employed", intervalStr])
    if len(timeIntervals) == 1:
        if len(curr_experience) >= 4:
            new_experience_list.append(["Location", curr_experience[3]])
        if len(curr_experience) >= 5:
            new_experience_list.append(["More Info", curr_experience[4]])          
    return new_experience_list

def get_experience_without_tags(html):
    to_ret = []
    experience_area = False
    curr_experience = []
    countIndex = 0
    dataArea = False
    for line in html:
        if 'id="experience"' in line:
            experience_area = True
        # if experience_area:
        #     print("Found Experience")
        if experience_area:
            if 'experience_company_logo' in line:
                if curr_experience and countIndex != 0:
                    new_experience_list = add_tag_to_experience_list(curr_experience)
                    to_ret.append(new_experience_list)
                curr_experience = []
                countIndex += 1
            if 'aria-hidden="true"' in line:
                dataArea = True
            line = line.strip()
            if "logo" in line:
                continue
            if len(line) > 0 and line[0] != '<' and dataArea:
                curr_experience.append(line)
                dataArea = False
            if "</section>" in line:
                if curr_experience and countIndex != 0:
                    new_experience_list = add_tag_to_experience_list(curr_experience)
                    to_ret.append(new_experience_list)
                return to_ret, experience_area                  
    return [], experience_area

def add_tag_to_education_list(curr_education):
    new_education_list = []
    for i in range(len(curr_education)):
        curr_info = curr_education[i]
        if i == 0:
            new_education_list.append(curr_info)
        if i == 1:
            degree_infos = curr_info.split(",",1)
            new_education_list.append(["Degree Name", degree_infos[0]])
            if len(degree_infos) > 1:
                new_education_list.append(["Field Of Study", degree_infos[1]])
        elif i == 2:
            new_education_list.append(["Dates attended or expected graduation", curr_info])
        elif i == 3:
            new_education_list.append(["More Info", curr_info])
    return new_education_list

def get_education_without_tags(html):
    to_ret = []
    education_area = False
    curr_education = []
    for line in html:
        if 'id="education"' in line:
            education_area = True
        # if experience_area:
        #     print("Found Education")
        if education_area:
            regex_for_indicator = re.search(r'alt=(.*?)logo', line)
            if regex_for_indicator:
                if curr_education:
                    new_experience_list = add_tag_to_education_list(curr_education)
                    to_ret.append(new_experience_list)
                    curr_education = []
            line = line.strip()
            if len(line) > 0 and line[0] != '<' and line not in curr_education:
                curr_education.append(line)
            # if 'aria-hidden="true"' in line and 'class="visually-hidden"' in line:
            #     # mo = re.search(r"[<.*?>]*?(.+?)[<.*?>]*?", line)
            #     regex_for_info = re.search(r"!---->(.+?)<", line)
            #     curr_education.append(regex_for_info.group(1))
            if "</section>" in line:
                new_experience_list = add_tag_to_education_list(curr_education)
                to_ret.append(new_experience_list)
                return to_ret[1:], education_area                    
    return [], education_area

def parse_background_info(html):
    education, found_education = get_education_without_tags(html)
    if len(education) == 0:
        education = get_education_with_tags(html)
    experience, found_experience = get_experience_without_tags(html)
    if len(experience) == 0:
        experience = get_education_with_tags(html)
    return (education, found_education), (experience, found_experience)