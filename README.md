<h3>Experiment Design and Result</h3>
Check Google drive: https://drive.google.com/drive/folders/12wFaqDHGWyZUVg8tUVCIGG21akuFYYBD?ths=true

<h3>How to Run the Code</h3>
The program starts in analyze_grad_profile.py
Example usage:
    analyze_grad_profile("Heritage Institute of Technology", ["Computer Science"], 100, 20)
will collect profile data about 100 alumni graduated in the last 20 years in Computer Science major at Heritage Institute of Technology
Result will be stored in grad_history and grad_current_institution directory, under the path of "[institution name]/[major].csv"

The program currently will only work if alumni name list about specific institution and major is provided in the directory "alumni_name_list", since the program can not scrape enough names from Linkedin yet (Details in "Alumni Data Collection Report" doc in the google drive above)

Other files: collect_grad_profile.py can scrape the profile record from Linkedin about a person. find_grad_from_institution.py can scrape a name list about alumni from specific institution, major, graduation year. linkedin_scraper.py can setup linkedin accounts and get the html source code about any linkedin pages if valid accounts are provided in the fake_accounts.txt 

<h3>Problem Solving</h3>
If met the problem of "selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version x". Download chromedriver for current version of Chrome browser from https://chromedriver.chromium.org/downloads. The current Chrome browser version is usually listed in the error message.