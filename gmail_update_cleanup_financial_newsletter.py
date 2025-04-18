import os
import pickle
import requests
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# OAuth setup
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def identify_financial_email(subject, body, sender):
    """
    Identify if an email is related to banking or payments using TinyLlama API.
    """
    # Quick check for specific financial institutions (more reliable than the API)
    critical_financial_terms = [
        'bank of america', 'chase', 'citi', 'discover', 'paypal',
        'mastercard', 'visa', 'billpay', 'payment confirmation'
    ]
    
    for term in critical_financial_terms:
        if term in sender.lower() or term in subject.lower():
            print(f"Critical financial term detected: {term}")
            return True
    
    # Dollar rental receipts are financial
    if "dollar" in sender.lower() and "receipt" in subject.lower():
        print(f"Rental receipt detected")
        return True
            
    # Use TinyLlama for classification with a very specific prompt
    prompt = f"""
You are analyzing an email to determine if it's about personal finance.

An email is about PERSONAL FINANCE if it contains:
- Bank statements or payment confirmations
- Credit card statements or transactions
- Receipts for purchases
- Bills or invoices
- Financial account information

An email is NOT about personal finance if it's:
- News articles about financial topics
- Newsletters from real estate sites like Zillow
- General news or updates
- Community information

Subject: {subject}
From: {sender}
Body: {body[:300]}

Respond with EXACTLY ONE WORD: either YES if it's personal finance or NO if it's not.
"""

    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'tinyllama',
        'prompt': prompt,
        'stream': False
    })
    
    try:
        result = response.json()
        response_text = result.get('response', '').lower().strip()
        is_financial = response_text == 'yes'
        
        if is_financial:
            print(f"LLM identified as financial: \"{subject}\"")
        else:
            print(f"LLM identified as NOT financial: \"{subject}\"")
        
        return is_financial
    except requests.exceptions.JSONDecodeError:
        text_response = response.text
        print(f"Warning: JSON parsing error: {text_response[:100]}...")
        return False

def is_newsletter(subject, body, sender):
    """
    Identify if an email is a newsletter or promotional digest using TinyLlama API.
    """
    # Quick check for obvious newsletter sources
    if 'dailyvoice.com' in sender.lower() or 'newsbreak' in sender.lower():
        print(f"Known newsletter source detected: {sender}")
        return True
    
    # Use TinyLlama for classification
    prompt = f"""
You are analyzing an email to determine if it's a newsletter.

A NEWSLETTER email typically:
- Contains multiple news stories or articles
- Is sent to many subscribers
- Has content about news, community events, or general updates
- Often comes from media sources, news sites, or update services
- Examples include Daily Voice updates, Zillow reports, community alerts

A NON-NEWSLETTER email typically:
- Contains personal information specific to the recipient
- Financial statements or transactions
- Receipts or confirmations of purchases
- Account security notifications

Subject: {subject}
From: {sender}
Body: {body[:300]}

Respond with EXACTLY ONE WORD: either YES if it's a newsletter or NO if it's not.
"""

    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'tinyllama',
        'prompt': prompt,
        'stream': False
    })
    
    try:
        result = response.json()
        response_text = result.get('response', '').lower().strip()
        is_newsletter = response_text == 'yes'
        
        if is_newsletter:
            print(f"LLM identified as newsletter: \"{subject}\"")
        else:
            print(f"LLM identified as NOT newsletter: \"{subject}\"")
        
        return is_newsletter
    except requests.exceptions.JSONDecodeError:
        text_response = response.text
        print(f"Warning: JSON parsing error: {text_response[:100]}...")
        return False

def identify_customer_service_email(subject, body, sender):
    """
    Identify if an email is customer service related using TinyLlama API.
    """
    # Hard-coded special cases - more reliable than API
    if 'CADS:' in subject:
        print(f"CADS customer service email detected")
        return True
    
    # Use TinyLlama for classification
    prompt = f"""
You are analyzing an email to determine if it's customer service related.

A CUSTOMER SERVICE email typically:
- Responds to customer inquiries
- Provides order confirmations or shipping updates
- Gives product support or technical assistance
- Contains account or service updates
- Addresses user problems or questions

A NON-CUSTOMER SERVICE email typically:
- Contains news articles or stories
- Community announcements or alerts
- General newsletters or updates
- Marketing or promotional content

Subject: {subject}
From: {sender}
Body: {body[:300]}

Respond with EXACTLY ONE WORD: either YES if it's customer service related or NO if it's not.
"""

    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'tinyllama',
        'prompt': prompt,
        'stream': False
    })
    
    try:
        result = response.json()
        response_text = result.get('response', '').lower().strip()
        is_customer_service = response_text == 'yes'
        
        if is_customer_service:
            print(f"LLM identified as customer service: \"{subject}\"")
        else:
            print(f"LLM identified as NOT customer service: \"{subject}\"")
        
        return is_customer_service
    except requests.exceptions.JSONDecodeError:
        text_response = response.text
        print(f"Warning: JSON parsing error: {text_response[:100]}...")
        return False

def classify_email_with_llm(subject, body):
    """
    Classify if an email is promotional using TinyLlama API.
    """
    # Use TinyLlama for classification
    prompt = f"""
You are analyzing an email to determine if it's promotional marketing content.

A PROMOTIONAL email typically:
- Advertises products or services
- Contains discounts, deals, or special offers
- Has calls to action like "Buy Now" or "Shop Today"
- Marketing messages promoting products
- Sales announcements

A NON-PROMOTIONAL email typically:
- Contains important personal information
- Account notifications
- Receipts or confirmations
- News or informational content
- Customer service responses

Subject: {subject}
Body: {body[:300]}

Respond with EXACTLY ONE WORD: either YES if it's promotional or NO if it's not.
"""

    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'tinyllama',
        'prompt': prompt,
        'stream': False
    })
    
    try:
        result = response.json()
        response_text = result.get('response', '').lower().strip()
        is_promotional = response_text == 'yes'
        
        if is_promotional:
            print(f"LLM identified as promotional: \"{subject}\"")
        else:
            print(f"LLM identified as NOT promotional: \"{subject}\"")
        
        return is_promotional
    except requests.exceptions.JSONDecodeError:
        text_response = response.text
        print(f"Warning: JSON parsing error: {text_response[:100]}...")
        return False

def get_updates_folder_id(service):
    # Find the ID of the "Updates" folder/label
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    
    # Debug: Print all available labels to help identify the correct one
    print("Available labels in your Gmail account:")
    for label in labels:
        print(f"- {label['name']} (ID: {label['id']})")
    
    # Try various possibilities for the Updates label
    for label in labels:
        # Check for "updates" in different forms
        label_name = label['name'].lower()
        if (label_name == 'updates' or 
            label_name == 'category_updates' or 
            'update' in label_name or
            label_name == 'CATEGORY_UPDATES'.lower()):
            print(f"Found Updates folder with name: {label['name']}")
            return label['id']
    
    # Gmail categories are handled differently - try using the CATEGORY_UPDATES ID directly
    category_updates_id = 'CATEGORY_UPDATES'
    print(f"Updates folder not found by name. Trying default ID: {category_updates_id}")
    
    # Test if the category exists by trying to list messages with this label
    try:
        test_query = service.users().messages().list(
            userId='me', 
            labelIds=[category_updates_id],
            maxResults=1
        ).execute()
        
        # If we get here without error, the category exists
        print(f"Successfully found Updates category using default ID")
        return category_updates_id
    except Exception as e:
        print(f"Error testing default Updates category: {str(e)}")
        print("Updates folder/category not found. Please make sure it exists in your Gmail account.")
        return None

def process_customer_service_emails(service, max_emails=20):
    # Get the Updates folder ID
    updates_label_id = get_updates_folder_id(service)
    if not updates_label_id:
        return 0
    
    # Get emails from the Updates folder
    results = service.users().messages().list(
        userId='me', 
        labelIds=[updates_label_id],
        maxResults=max_emails
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("No messages found in Updates folder.")
        return 0
    
    trashed_count = 0
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        
        # Extract subject, body, and sender
        subject = ''
        body = ''
        sender = ''
        
        payload = msg['payload']
        headers = payload.get('headers', [])
        
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'From':
                sender = header['value']
        
        # Try to get plain text body
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
                    break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')
        
        print(f"\nProcessing email: \"{subject}\" from {sender}")
            
        # Financial email check - should be done first to protect important emails
        if identify_financial_email(subject, body, sender):
            print(f"Kept financial email: {subject}")
            continue
        
        # If not financial, check if it's a newsletter
        if is_newsletter(subject, body, sender):
            service.users().messages().trash(userId='me', id=message['id']).execute()
            trashed_count += 1
            print(f"Trashed newsletter: {subject}")
            continue
        
        # If not financial or newsletter, check if it's customer service
        if identify_customer_service_email(subject, body, sender):
            # Move to trash if customer service related
            service.users().messages().trash(userId='me', id=message['id']).execute()
            trashed_count += 1
            print(f"Trashed customer service email: {subject}")
        else:
            print(f"Kept non-customer service email: {subject}")
    
    return trashed_count

def process_promotional_emails(service, max_emails=10):
    # Get emails from inbox
    results = service.users().messages().list(userId='me', maxResults=max_emails).execute()
    messages = results.get('messages', [])
    
    deleted_count = 0
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        
        # Extract subject and body
        subject = ''
        body = ''
        
        payload = msg['payload']
        headers = payload.get('headers', [])
        
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
        
        # Try to get plain text body
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
                    break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')
        
        # Classify the email
        if classify_email_with_llm(subject, body):
            # Delete if promotional
            service.users().messages().trash(userId='me', id=message['id']).execute()
            deleted_count += 1
            print(f"Deleted promotional email: {subject}")
        else:
            print(f"Kept important email: {subject}")
    
    return deleted_count

def main():
    service = authenticate_gmail()
    
    # Process promotional emails from inbox
    # promo_deleted = process_promotional_emails(service)
    # print(f"Total promotional emails deleted: {promo_deleted}")
    
    # Process customer service emails from Updates folder
    # Skip financial/banking emails, but trash newsletters
    cs_trashed = process_customer_service_emails(service)
    print(f"Total emails trashed from Updates folder: {cs_trashed}")
    print(f"Financial/banking emails were kept safe in your Updates folder")

if __name__ == '__main__':
    main()