#!/bin/python3
import openai
from selenium import webdriver
from bs4 import BeautifulSoup
import os, sys
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# from docx import Document
import json


sampleExperience = {
    "jobExperience": "SYSTEM ADMINISTRATOR L1",
    "sample": """Servers by installing required software and patching Established network specifications and analyzed workflow,
access, information, and security requirements.
Hardened all servers by implementing security measures such as firewalls, SSL/TLS certificates, and IAM.
Migrating some parts of the system to AWS.
Configured backup and RAID storage for disaster recovery Provided technical support to end-users for
 hardware and software issues.""",
}
sampleJobPostingURL = "https://www.linkedin.com/jobs/view/member-support-representative-at-elo-health-3725732265?refId=NnwWNRddShZ2X4lAzz5Q4w%3D%3D&trackingId=ykCB3RI7TqF8pLpa1RCBtw%3D%3D&trk=public_jobs_topcard-title"


def main():
    tailor(sampleJobPostingURL)


def tailor(url):
    data = jobBoardHandeler(url)
    openAi(data, sampleExperience)


def getJobPosting(url):
    fireFoxOptions = webdriver.FirefoxOptions()
    # fireFoxOptions.headless = True
    driverPath = GeckoDriverManager().install()
    brower = webdriver.Firefox(
        options=fireFoxOptions,
        service=Service(executable_path=driverPath),
    )
    brower.get(url)
    pageSource = brower.page_source
    brower.quit()
    return pageSource


def indeedHandeler(url):
    rawData = getJobPosting(url)
    data = {}
    soup = BeautifulSoup(rawData, "html5lib")
    data["jobTitle"] = (
        soup.find("h1", {"class": "jobsearch-JobInfoHeader-title"}).find("span").text
    )
    data["company"] = (
        soup.find("div", {"data-testid": "inlineHeader-companyName"}).find("a").text
    )
    data["jobDiscription"] = soup.find("div", {"id": "jobDescriptionText"}).text
    return data


def linkedinHandeler(url):
    rawData = getJobPosting(url)
    data = {}
    soup = BeautifulSoup(rawData, "html5lib")
    data["jobTitle"] = soup.find("h1", {"class": "top-card-layout__title"}).text
    data["company"] = soup.find("a", {"class": "topcard__org-name-link"}).text.strip()
    data["jobDiscription"] = soup.find(
        "div", {"class": "show-more-less-html__markup"}
    ).text
    return data


def jobBoardHandeler(url):
    match url:
        case url if "indeed" in url:
            return indeedHandeler(url)
        case url if "linkedin" in url:
            return linkedinHandeler(url)
        case _:
            print("job board is not supported")
            sys.quit("1")


def openAi(jobPosting, resumeElemet):
    print(jobPosting)
    openai.api_key = os.getenv("gpt")
    with open("prompts/jobExperiencePrompt.txt") as f:
        systemPrompt = f.read()
    data = {}
    data["jobPosting"] = jobPosting["jobDiscription"]
    data["jobExperience"] = resumeElemet["jobExperience"]
    data["sample"] = resumeElemet["sample"]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{systemPrompt}"},
            {"role": "user", "content": f"{json.dumps(data)}"},
        ],
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    print(data)
    # print(response)


if "__main__" == __name__:
    main()
