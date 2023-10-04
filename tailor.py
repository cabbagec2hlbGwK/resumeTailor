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
    "elementType": "Experience",
    "sample": """Servers by installing required software and patching Established network specifications and analyzed workflow,
access, information, and security requirements.
Hardened all servers by implementing security measures such as firewalls, SSL/TLS certificates, and IAM.
Migrating some parts of the system to AWS.
Configured backup and RAID storage for disaster recovery Provided technical support to end-users for
 hardware and software issues.""",
}
sampleJobPostingURL = "https://www.linkedin.com/jobs/view/3728600846/?eBP=JOB_SEARCH_ORGANIC&refId=XZ3KUIbL9dDmxjbn%2BFunHA%3D%3D&trackingId=%2BMf8IZi%2FPoQ0ZkmuyyodMw%3D%3D"


def main():
    print(tailor(sampleJobPostingURL))


def tailor(url):
    data = getJob(url)
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


def getJob(url):
    match url:
        case url if "indeed" in url:
            return indeedHandeler(url)
        case url if "linkedin" in url:
            return linkedinHandeler(url)
        case _:
            print("job board is not supported")
            sys.quit("1")


def experiencePrompt(jobPosting, resumeElement):
    messages = [
        {
            "role": "system",
            "content": "just give the answer directedly no unrelated information,and reply in MD format only.",
        },
        {
            "role": "user",
            "content": f"I am going to send you a job posting. and I want your help in getting this position. To do so, I am going to modify my resume to include the tools and skills needed by this job posting. So for this, let's start with modifying the experience section. So I have experience as a {resumeElement['jobExperience']}, and I want to show that I have more than enough experience to perform the role the job posting is asking for.\nAlso, only give me the answer, nothing extra and don't start with based on, etc.",
        },
        {
            "role": "assistant",
            "content": "Sure, please provide the job posting and details of your system administrator experience, and I will help you modify your resume accordingly.",
        },
        {"role": "user", "content": jobPosting["jobDiscription"]},
    ]
    return messages


def openAi(jobPosting, resumeElemet):
    openai.api_key = os.getenv("gpt")
    with open("prompts/jobExperiencePrompt.txt") as f:
        systemPrompt = f.read()
    message = []
    elementType = resumeElemet.get("elementType")
    match elementType:
        case elementType if "Summary" == elementType:
            pass
        case elementType if "Experience" == elementType:
            message = experiencePrompt(
                jobPosting=jobPosting, resumeElement=resumeElemet
            )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message,
        temperature=1,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    print(response.choices[0].get("message").get("content"))


if "__main__" == __name__:
    main()
