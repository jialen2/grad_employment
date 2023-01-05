import os
import json
import sys
from find_grad_from_institution import find_grad_from_institution
from collect_grad_profile import collect_grad_profile
root_dir = os.getcwd()
def enter_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    os.chdir(dir)

def read_profile_from_file(institution, major, visited_names):
    major = major.replace(" ", "_")
    profile_file = root_dir+"/alumni_profile/"+institution+"/"+major+".csv"
    if not os.path.exists(profile_file):
        return {}
    with open(profile_file, "r") as input:
        data = json.load(input)
    for name in data:
        if name not in visited_names:
            visited_names[name] = True
    return data

def convert_month_str_to_int(month_str):
    with open(root_dir+"/month_info.txt") as input:
        for line in input:
            infos = line.split(",")
            if month_str == infos[0]:
                return int(infos[1])

def split_dash(s):
    if "–" in s:
        return s.split("–")
    if "-" in s:
        return s.split("-")
    if "―" in s:
        return s.split("―")
    if "‐" in s:
        return s.split("‐")
    return [s]

def parse_experience(profile):
    experience_lst = []
    valid = True
    for experience in profile["Experience"]:
        # An experience info is in the form of [(start_year, start_month), company_name, end_year, "w"] (the last field represent the experience type; "w" means working experience)
        experience_info = [(sys.maxsize, sys.maxsize), "", -sys.maxsize, "w"]
        for i in range(len(experience)):
            info = experience[i]
            # if the current company is not on the list, skip
            if isinstance(info, list) and info[0] == "Company Name":
                experience_info[1] = info[1]
            # Find the earliest start time and latest end time of an experience. An experience may contain multiple positions, thus multiple time range.
            if isinstance(info, list) and info[0] == "Dates Employed":
                # A time range will be like (year, month)
                start_time_range = split_dash(info[1])[0].strip().split(" ")
                curr_start_time = (int(start_time_range[1]), convert_month_str_to_int(start_time_range[0]))
                experience_info[0] = min(curr_start_time, experience_info[0])
                curr_end_year = split_dash(info[1])[1].strip().split(" ")[1]
                experience_info[2] = max(int(curr_end_year), experience_info[2])
        if experience_info[1] != "" and experience_info[0] != (sys.maxsize, sys.maxsize):
            if experience_info not in experience_lst:
                experience_lst.append(experience_info)
    print(experience_lst)
    for education in profile["Education"]:
        # An education info is in the form of [(start_year, start_month), company_name, end_year, "w"] (the last field represent the experience type; "e" means education)
        # Since the start month of an education is generally not provided, we use June(6) as default.
        education_info = [(sys.maxsize, 6), "", -sys.maxsize, "e"]
        education_info[1] = education[0]
        for i in range(1,len(education)):
            info = education[i]
            # Get the start time of an education
            if isinstance(info, list) and len(info) > 1 and info[0] == "Dates attended or expected graduation":
                peroid = info[1]
                time_range = split_dash(peroid)
                if len(time_range) < 2:
                    valid = False
                    break
                for i, time in enumerate(time_range):
                    time_range[i] = time.strip()
                # Usually time ranges for education are provided as "2019 - 2023", but some time ranges may provided as "Feb 2019 - Aug 2023", so I used " " to detect whether it's the second case.
                if " " in time_range[0]:
                    start_year = int(time_range[0].split(" ")[1])
                else:
                    start_year = int(time_range[0].strip())
                if " " in time_range[1]:
                    end_year = int(time_range[1].split(" ")[1])
                else:
                    end_year = int(time_range[1].strip())
                education_info[0] = (start_year, 6)
                education_info[2] = end_year
            # If no valid start time provided, skip
            if education_info[0][0] != sys.maxsize:
                if education_info not in experience_lst:
                    experience_lst.append(education_info)
    print(experience_lst)
    # Sort the experience list by start time.
    experience_lst = sorted(experience_lst)
    print(experience_lst)
    # Change the elements in the experience list to the format of [instituion name, duration(in year), experience type("w" or "e")]
    for i, experience in enumerate(experience_lst):
        duration = experience[2] - experience[0][0]
        experience_lst[i] = [experience[1], duration, experience[3]]
    print(experience_lst)
    if valid:
        return experience_lst
    return []
    

def enter_storage_dir(storage_dir, institution, major):
    # Get into the directory for all alumni profile data. If not exist, create one.
    profile_dir_path = root_dir + "/" + storage_dir
    enter_dir(profile_dir_path)
    # Get into the directory for the institution. If not exist, create one.
    institution = institution.replace(" ", "_")
    profile_institution_path = profile_dir_path + "/" + institution
    enter_dir(profile_institution_path)
    # Create the file for the major if the file does not exist.
    major = major.replace(" ", "_")
    profile_major_file = major + ".csv"
    if not os.path.exists(profile_major_file):
        with open(profile_major_file, "w") as output:
            output.write("")   

def prepare_profile_data(institution, major, num_people, num_year, visited_names):
    valid_profiles = []
    while len(valid_profiles) < num_people:
        collect_grad_profile(institution, major, visited_names)
        profile_data = read_profile_from_file(institution, major, visited_names)
        for alumni_name in profile_data:
            experience_lst = parse_experience(profile_data[alumni_name])
            # If the experience list only contains 1 element, then probably it only contains the experience about the instituion in the input, so we need to skip it.
            if len(experience_lst) < 2:
                continue
            valid_profiles.append(experience_lst)
        valid_profiles = valid_profiles[:num_people]
        print("num profiles collected:", len(valid_profiles))
        # find_grad_from_institution(institution, major, num_year, num_people-len(valid_profiles), visited_names)
    return valid_profiles

def analyze_grad_current_institution(institution, major, alumni_profiles):
    enter_storage_dir("grad_current_institution", institution, major)
    major = major.replace(" ", "_")
    curr_status = {}
    for profile in alumni_profiles:
        curr_instituion = profile[-1][0]
        curr_status[curr_instituion] = curr_status.get(curr_instituion, 0) + 1
    data = curr_status.items()
    data = sorted(data, key=lambda x:x[1], reverse=True)
    with open(major + ".csv", "w") as output:
        for institution, num_people in data:
            institution = '"' + institution + '"'
            output.write(institution + "," + str(num_people) + "\n")
    enter_dir(root_dir)

def analyze_grad_history(institution, major, alumni_profiles):
    enter_storage_dir("grad_history", institution, major)
    print(os.getcwd())
    major = major.replace(" ", "_")
    print(major)
    with open(major + ".csv", "w") as output:
        for profile in alumni_profiles:
            for experience in profile:
                instituion_name = '"' + experience[0] + '"'
                duration = experience[1]
                experience_type = experience[2]
                info = "-".join([instituion_name, str(duration), experience_type])
                output.write(info+",")
            output.write("\n")
    enter_dir(root_dir)
                

def analyze_grad_profile(institution, majors, num_people=50, num_year=10):
    alumni_profiles = []
    visited_names = {}
    for major in majors:
        alumni_profiles += prepare_profile_data(institution, major, num_people, num_year, visited_names)
    if len(majors) > 1:
        major_name = "combined"
    else:
        major_name = majors[0]
    analyze_grad_current_institution(institution, major_name, alumni_profiles)
    analyze_grad_history(institution, major_name, alumni_profiles)

analyze_grad_profile("Heritage Institute of Technology", ["Computer Science"], 100)

analyze_grad_profile("Heritage Institute of Technology", ["Computer Science", "Electronics and Communication Engineering", "Electrical Engineering"])

analyze_grad_profile("Heritage Institute of Technology", ["Electronics and Communication Engineering"])

analyze_grad_profile("Heritage Institute of Technology", ["Electrical Engineering"])