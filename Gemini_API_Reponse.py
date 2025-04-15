from langchain.llms import OpenAI
import os
from dotenv import load_dotenv
from pdfminer.high_level import extract_text
import re
import google.generativeai as genai
from pdfminer.high_level import extract_text
from input import job_title,job_description,Company_Name
from langchain import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain import ConversationChain
from langchain.llms import OpenAI  
env_path = 'Config.env'
load_dotenv(dotenv_path=env_path)

Resume_path= "C:/Users/hrith.DESKTOP-75K32P0/OneDrive/Documents/Hrithik_Files_Desktop/FT_Resumes_NEU/Hrithik_Resume_Data_Engineer.pdf"

# Set up OpenAI LLM
openai_api_key = os.getenv('OPENAI_API_KEY')  # Store your API key in environment variable
gemini_api_key=os.getenv('GEMINI_API_KEY')


def remove_date_ranges(text):
    # Regex pattern for date ranges (e.g., "Sep 2021 - Dec 2021" or "Sep 2021 to Dec 2021")
    date_pattern = r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\s*(?:-|to)\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}"
    
    # Remove date ranges
    return re.sub(date_pattern, "", text)

def extract_resume_sections(pdf_path):
    # Extract text from PDF
    full_text = extract_text(pdf_path)

    # Remove date ranges from the text
    full_text = remove_date_ranges(full_text)

    # Use regex patterns to identify sections
    education_pattern = r"(Education\s*[\s\S]+?)(?=(Skills|Work Experience|Projects|$))"
    skills_pattern = r"(Skills\s*[\s\S]+?)(?=(Education|Work Experience|Projects|$))"
    work_experience_pattern = r"(Work Experience\s*[\s\S]+?)(?=(Education|Skills|Projects|$))"
    projects_pattern = r"(Projects\s*[\s\S]+?)(?=(Education|Skills|Work Experience|$))"

    # Find matches using regex
    education = re.search(education_pattern, full_text, re.IGNORECASE)
    skills = re.search(skills_pattern, full_text, re.IGNORECASE)
    work_experience = re.search(work_experience_pattern, full_text, re.IGNORECASE)
    projects = re.search(projects_pattern, full_text, re.IGNORECASE)

    # Extract text if matches are found
    education_text = education.group(1).strip() if education else "Education section not found"
    skills_text = skills.group(1).strip() if skills else "Skills section not found"
    work_experience_text = work_experience.group(1).strip() if work_experience else "Work Experience section not found"
    projects_text = projects.group(1).strip() if projects else "Projects section not found"

    return {
        "Education": education_text,
        "Skills": skills_text,
        "Work Experience": work_experience_text,
        "Projects": projects_text
    }


#resume_sections = extract_resume_sections(Resume_path)
def create_email_prompt(resume_sections,job_title,company_name,job_description):
    
    education = resume_sections["Education"]
    work_experience = resume_sections["Work Experience"]
    projects = resume_sections["Projects"]
    skills = resume_sections["Skills"]

    prompt = (
        f"You are a professional in email writing and technically strong when it comes to writing emails on behalf "
        f"of aspiring Data Engineers, Data Scientists, Data Analysts, and Machine Learning Engineers to Hiring Companies. "
        f"Write a professional and appealing email within a word limit of 200 - 250 for Hiring Managers and Technical Recruiters for my job application. "
        f"The job title I am applying for is {job_title} at {company_name}.\n\n"
        f"The job description is as follows:\n{job_description}\n\n"
        f"My Professional Profile / Resume is divided into 4 sections:\n\n"
        f"My name is Hrithik Sarda, My email address is hrithiksarda4@gmail.com , my phone number is +1 (978)-654-0445"
        f"My Education is as follows: {resume_sections['Education']}.\n\n"
        f"The Work Experience is as follows: {resume_sections['Work Experience']}.\n\n"
        f"My Personal and academic Projects are as follows: {resume_sections['Projects']}.\n\n"
        f"My Skills are as follows: {resume_sections['Skills']}.\n\n"
        f"The email should include a subject line and a body. The email should introduce me. The tone should be polite and professional, "
        f"and the email should request consideration as an eligible candidate, highlighting how my skills and experience align "
        f"with the job requirements. "
        f"VERY IMPORTANT NOTE : Make sure the email is ready to be sent without requiring any further information or editing."
    )

    return prompt


def create_cover_letter(resume_sections, job_title, company_name, job_description):

    education = resume_sections["Education"]
    work_experience = resume_sections["Work Experience"]
    projects = resume_sections["Projects"]
    skills = resume_sections["Skills"]

    prompt = (
        f"You are an expert in writing professional and compelling cover letters for aspiring Data Engineers, Data Scientists, "
        f"and Data Analysts. Write a well-structured cover letter within a word limit of 400 - 500 words that will accompany my job application. "
        f"The position I am applying for is {job_title} at {company_name}.\n\n"
        f"The job description is as follows:\n{job_description}\n\n"
        f"My Professional Profile / Resume is divided into 4 sections and it includes all the domains and departments I have worked and studied in. :\n\n"
        f"My name is Hrithik Sarda. My email address is hrithiksarda4@gmail.com, and my phone number is +1 (978)-654-0445.\n\n"
        f"My Education includes: {education}.\n\n"
        f"My Work Experience includes: {work_experience}.\n\n"
        f"My Personal and Academic Projects include: {projects}.\n\n"
        f"My Skills include: {skills}.\n\n\n"
        f"The cover letter should introduce me, provide an overview of my qualifications/GPA at Bachelors and Masters Level, and explain how my skills and experience align with "
        f"the requirements of the job. It should express my enthusiasm for the position and my eagerness to contribute to {company_name}. "
        f"The tone should be professional, confident, and tailored to the specific role and company. The cover letter should be ready to send "
        f"without requiring any further information or editing."
    )

    return prompt



def gemini_reponse(prompt):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text


