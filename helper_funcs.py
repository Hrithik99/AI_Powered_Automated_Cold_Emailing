from dotenv import load_dotenv
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from Gemini_API_Reponse import gemini_reponse
from input import job_title,job_description,Company_Name
from email.mime.base import MIMEBase
from Email_Validation_Funcs import is_email_valid,generate_possible_emails
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
env_path = 'Config.env'
load_dotenv(dotenv_path=env_path)

Role_Name=os.getenv('ROLE_NAME')
EMAIL = os.getenv('GMAIL_EMAIL')
PASSWORD = os.getenv('GMAIL_PASSWORD')
Resume_path= Resume_path= os.getenv('RESUME_PATH')
email_body_path=os.getenv('EMAIL_BODY_PATH')
gemini_api_key=os.getenv('GEMINI_API_KEY')
sendgrid_api_key=os.getenv('SENDGRID_API_KEY')
downloads_folder = r"C:\Users\hrith.DESKTOP-75K32P0\Downloads"
target_folder = r"C:\Outlook_Email_Generator\Apollo_CSV_Extracts"
scheduler = BackgroundScheduler()
scheduler.start()
est = pytz.timezone("US/Eastern")
schedule_time = None
def send_email(to_email, subject, body, attachment_path=None,schedule_time=None):

    if schedule_time:

        scheduler.add_job(send_email_task, 'date', run_date=schedule_time, args=[to_email, subject, body, attachment_path])
        print(f"Email scheduled for {schedule_time} to {to_email}")
    else:
        send_email_task(to_email, subject, body, attachment_path)


def send_email_task(to_email, subject, body, attachment_path=None):
    # Set your name in the 'From' field
    from_name = "Hrithik Sarda"
    from_email = EMAIL
    full_from = f"{from_name} <{from_email}>"
    
    # Create the email headers
    msg = MIMEMultipart()
    msg['From'] = full_from
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Attach the email body
    msg.attach(MIMEText(body, 'html'))
    
    # Attach a PDF file if provided
    if attachment_path:
        attachment_name = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as attachment_file:
            attachment = MIMEBase('application', 'pdf')  # Specify 'pdf' content type
            attachment.set_payload(attachment_file.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename={attachment_name}'
        )
        msg.attach(attachment)
    
    # Connect to Gmail's SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Start TLS encryption
        server.login(EMAIL, PASSWORD)  # Login to your Gmail account
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")
    finally:
        server.quit()  # Close the connection





def get_latest_file(folder_path):
    # Get a list of files in the directory with their full paths
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    # Check if there are any files
    if not files:
        return None
    
    # Get the latest file based on modification time
    latest_file = max(files, key=os.path.getmtime)
    return latest_file


def read_df(target_path):
    if target_path:
        df=pd.read_csv(target_path)
        df_upd=df.drop(columns=['Company Name for Emails','Email Confidence',
        'Primary Email Catch-all Status', 'Primary Email Last Verified At','Departments', 'Contact Owner', 'Work Direct Phone',
        'Home Phone', 'Mobile Phone', 'Corporate Phone', 'Other Phone', 'Stage',
        'Lists', 'Last Contacted', 'Account Owner', '# Employees', 'Industry',
        'Keywords', 'Person Linkedin Url', 'Website', 'Company Linkedin Url',
        'Facebook Url', 'Twitter Url','Company Address', 'Company City', 'Company State', 'Company Country',
        'Company Phone', 'SEO Description', 'Technologies', 'Annual Revenue',
        'Total Funding', 'Latest Funding', 'Latest Funding Amount',
        'Last Raised At', 'Email Sent', 'Email Open', 'Email Bounced',
        'Replied', 'Demoed', 'Number of Retail Locations', 'Apollo Contact Id',
        'Apollo Account Id', 'Secondary Email', 'Secondary Email Source',
        'Tertiary Email', 'Tertiary Email Source'])
        df_upd.columns = [col.replace(" ", "_") for col in df_upd.columns]
        df_upd=df_upd.dropna(subset='Email')
        new_row = {
            'First_Name': 'Hrithik',
            'Last_Name': 'Sarda',
            'Title': None,
            'Company': 'Bright Horizons',
            'Email': 'hrithiksarda1999@gmail.com',
            'Email_Status': None,
            'Primary_Email_Source': None,
            'Seniority': None,
            'City': None,
            'State': None,
            'Country': None
        }

# Insert the new row
        df_upd.loc[len(df_upd)] = new_row
        df_upd = df_upd.drop_duplicates()

        verified_emails = df_upd[df_upd['Email_Status'] == 'Verified']['Email'].dropna()
        if verified_emails.empty:
            raise ValueError("No verified email found in the dataset.")
        domains = verified_emails.str.split('@').str[-1].str.strip()
        most_common_domain = domains.mode()[0]
        domain = "@" + most_common_domain 
        return df_upd,domain
    else:
        print('No target path provided to read contacts')
        return None

def move_csv_file(downloads_folder, target_folder, file_pattern='*apollo-contacts-export*.csv'):

    try:
        # Check for files that match the pattern in the downloads folder
        matching_files = fnmatch.filter(os.listdir(downloads_folder), file_pattern)

        if matching_files:
            # Get the full path of the first matching file
            source_file_path = os.path.join(downloads_folder, matching_files[0])
            
            # Get the current timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create a new filename with the timestamp
            new_filename = f"{os.path.splitext(matching_files[0])[0]}_{timestamp}.csv"
            
            # Define the target file path
            target_file_path = os.path.join(target_folder, new_filename)
            
            # Move the file to the target folder with the new name
            shutil.move(source_file_path, target_file_path)
            print("Transfered the latest one from the downloads folder to Apollo CSV Extracts Folder")

            
            return target_file_path
        else:
            print("No new CSV found in Downloads folder. Returning the latest one from the Apollo CSV Extracts Folder")
            return None
    
    except Exception as e:
        return f"An error occurred: {str(e)}"
    

def generate_personalized_email(company_name, first_name, last_name):
    # Read the email template
    with open(email_body_path, "r", encoding="utf-8") as file:
        email_body = file.read()

    # Determine the salutation based on available fields
    if first_name:
        greeting = f"Hello {first_name},"  
    else:
        greeting = "Hello,"

    email_body = email_body.replace("Dear [Hiring Manager's Name],", greeting)
    email_body = email_body.replace("company_name", company_name)
    
    return email_body


def rename_csv_with_list_name(file_path):
    # Get the base filename from the file path
    base_filename = os.path.basename(file_path)

    # Check if the file exists
    if os.path.exists(file_path):
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Ensure "Lists" column exists
        if "Lists" in df.columns:
            # Drop NaN values and get the most common list name
            list_name = df["Lists"].dropna().mode()[0]  # mode() returns the most frequent value

            # Extract the timestamp from the original file name
            timestamp = base_filename.split("_")[1].split(".")[0]

            # Create the new file name
            new_file_name = f"{timestamp}_{list_name}.csv"

            # Get the directory of the original file
            directory = os.path.dirname(file_path)

            # Construct the full path for the new file name
            new_file_path = os.path.join(directory, new_file_name)

            # Rename the file
            os.rename(file_path, new_file_path)

            print(f"File renamed to: {new_file_path}")
            return(new_file_path)
        else:
            print("Error: 'Lists' column not found in the CSV file.")
    else:
        print("Error: File does not exist.")