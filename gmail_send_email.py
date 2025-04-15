import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from Gemini_API_Reponse import gemini_reponse
from input import job_title,job_description,Company_Name
from email.mime.base import MIMEBase
from Email_Validation_Funcs import is_email_valid,generate_possible_emails
from helper_funcs import move_csv_file,rename_csv_with_list_name, read_df, generate_personalized_email, send_email
from email import encoders
#import google.generativeai as genai
import pandas as pd
import os
import shutil
import fnmatch
from datetime import datetime
import markdown2
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment
import base64
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
env_path = 'Config.env'
load_dotenv(dotenv_path=env_path)


Role_Name=os.getenv('ROLE_NAME')
Resume_path= os.getenv('RESUME_PATH')
email_body_path=os.getenv('EMAIL_BODY_PATH')


EMAIL = os.getenv('GMAIL_EMAIL')
PASSWORD = os.getenv('GMAIL_PASSWORD')
gemini_api_key=os.getenv('GEMINI_API_KEY')
sendgrid_api_key=os.getenv('SENDGRID_API_KEY')
downloads_folder = r"C:\Users\hrith.DESKTOP-75K32P0\Downloads"
target_folder = r"C:\Outlook_Email_Generator\Apollo_CSV_Extracts"
scheduler = BackgroundScheduler()
scheduler.start()
est = pytz.timezone("US/Eastern")
schedule_time = None

def main():

    tgt_fp= move_csv_file(downloads_folder, target_folder, file_pattern='*apollo-contacts-export*.csv')
    print("Target filepath is:", tgt_fp)
    tgt_fp=rename_csv_with_list_name(tgt_fp)
    recipients,domain=read_df(tgt_fp)
    recipients['Email_Sent']=False
    recipients['Email_Sent_Time_EST)']=None

    #recipients=['hrithiksarda1999@gmail.com']
    for index,recipient in recipients.iterrows():
        
        first_name=recipient['First_Name'].title()
        last_name= recipient['Last_Name'].title()
        company_name= recipient['Company'].title()
        if (company_name) =='' or (company_name is None):
            subject="Exploring Opportunities in Data Engineering & Machine Learning!"
            #subject="Master’s Grad Eager to Contribute – Data Engineering Role at {}"
        else:
            subject=f"Master’s Grad Eager to Contribute – {Role_Name} Role at {company_name}"
        if (recipient['Email_Status'] == 'Verified'):
            email = recipient['Email']
            body=generate_personalized_email(company_name, first_name, last_name)
            send_email(email, subject, body, attachment_path=Resume_path,schedule_time=schedule_time)
            current_time_est = datetime.now(est)
            recipients.at[index, 'Email_Sent'] = True
            recipients.at[index, 'Email_Sent_Time_EST'] = current_time_est
        else:
            email = recipient['Email'].strip()
            if is_email_valid(email):
                body=generate_personalized_email(company_name, first_name, last_name)
                send_email(email, subject, body, attachment_path=Resume_path,schedule_time=schedule_time)
                current_time_est = datetime.now(est)
                recipients.at[index, 'Email_Sent'] = True
                recipients.at[index, 'Email_Sent_Time_EST'] = current_time_est
            else:
                gen_emails=generate_possible_emails(first_name,last_name,domain)
                #email_sent=False
                for candidate_email in gen_emails:
                    if is_email_valid(candidate_email):
                        recipients["Updated_Email"] = None 
                        recipients.at[index, 'Updated_Email'] = candidate_email
                        #recipients.at[index, 'Email_Status'] = 'Verified'
                        body=generate_personalized_email(company_name, first_name, last_name)
                        send_email(candidate_email, subject, body, attachment_path=Resume_path,schedule_time=schedule_time)
                        current_time_est = datetime.now(est)
                        recipients.at[index, 'Email_Sent'] = True
                        recipients.at[index, 'Email_Sent_Time_EST'] = current_time_est                        
                        break
                if not recipients["Email_Sent"]:
                    print(f"Email not sent for {first_name} {last_name}{domain} as email and its various versions are invalid")
    
    recipients.to_csv(tgt_fp, index=False)               
                

if __name__ == "__main__":
    # Pre-execution checklist
    print("Before running the script, please confirm the following checks are completed:")
    checklist = [
        "Ensure the correct resume file path is set.",
        "Verify the correct .html file path for the email body based on the role. VERIFY COMPANY NAME",
        "Update the HTML file if needed (e.g., Job Link and Job ID).",
        "Download the latest CSV from Apollo into the Downloads folder.",
        "Update the company name in the email subject line."
    ]

    # Display checklist
    for idx, item in enumerate(checklist, start=1):
        print(f"{idx}. {item}")

    # User confirmation
    choice = input("\nHave you completed all the required steps?\n"
                   "Enter:\n"
                   "  1 - Yes (Proceed with execution)\n"
                   "  2 - No (Make necessary changes and rerun the script)\n"
                   "Your choice: ")

    if choice.strip() == "1":
        main()
    else:
        print("Please complete the required changes and rerun the script.")







