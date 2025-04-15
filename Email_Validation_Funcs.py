import requests
import os
from validate_email import validate_email as validate_with_smtp
from dotenv import load_dotenv
env_path = 'Config.env'
load_dotenv(dotenv_path=env_path)

HUNTER_API_KEY=os.getenv('HUNTER_API_KEY')
MAILBOXLAYER_KEY =os.getenv('MAILBOXLAYER_KEY')
ABSTRACT_KEY = os.getenv('ABSTRACT_KEY')

def check_hunter(email):
    try:
        url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={HUNTER_API_KEY}"
        response = requests.get(url).json()
        if 'errors' in response:
            print("Hunter API error:", response['errors'][0]['details'])
            return None  # Quota exceeded or other issues
        return response.get("data", {}).get("status") == "valid"
    except Exception as e:
        print(f"Hunter API exception: {e}")
        return None
    
def generate_possible_emails(first, last, domain):
    first, last = first.lower(), last.lower()
    return [
        f"{first}.{last}{domain}",
        f"{first}{last}{domain}",
        f"{first[0]}.{last}{domain}",
        f"{last[0]}.{first}{domain}",
        f"{last}.{first}{domain}",
        f"{last}.{first[0]}{domain}"
    ]


def check_mailboxlayer(email):
    try:
        url = f"http://apilayer.net/api/check?access_key={MAILBOXLAYER_KEY}&email={email}&smtp=1&format=1"
        response = requests.get(url).json()
        if 'error' in response:
            print("Mailboxlayer API error:", response['error'].get("info", "Unknown error"))
            return None
        return response.get("format_valid") and response.get("smtp_check")
    except Exception as e:
        print(f"Mailboxlayer API exception: {e}")
        return None

def check_abstract(email):
    try:
        url = f"https://emailvalidation.abstractapi.com/v1/?api_key={ABSTRACT_KEY}&email={email}"
        response = requests.get(url).json()
        if 'error' in response:
            print("Abstract API error:", response['error'].get("message", "Unknown error"))
            return None
        return response.get("deliverability") == "DELIVERABLE"
    except Exception as e:
        print(f"Abstract API exception: {e}")
        return None

def check_smtp_dns(email):
    """Fallback method using SMTP and DNS MX record check."""
    try:
        return validate_with_smtp(
            email_address=email,
            check_format=True,
            check_blacklist=False,
            check_dns=True,
            check_smtp=True,
            smtp_timeout=10
        )
    except Exception as e:
        print(f"SMTP/DNS check failed: {e}")
        return False

def is_email_valid(email):
    """Validates email using layered fallback strategy based on service availability."""
    
    # Try Hunter
    result = check_hunter(email)
    if result is not None:
        return result

    # Fallback to Mailboxlayer
    result = check_mailboxlayer(email)
    if result is not None:
        return result

    # Fallback to Abstract API
    result = check_abstract(email)
    if result is not None:
        return result

    # Fallback to SMTP/DNS Check
    return check_smtp_dns(email)