import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# OAuth setup
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Authenticate with Gmail API and return the service object."""
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

def list_gmail_categories(service):
    """List all Gmail categories/labels and email counts."""
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    
    print("Your Gmail labels/categories:")
    for label in labels:
        # Get the count of messages with this label
        label_info = service.users().labels().get(userId='me', id=label['id']).execute()
        msg_count = label_info.get('messagesTotal', 0)
        print(f"- {label['name']} ({msg_count} emails)")
    
    return labels

def analyze_emails_by_sender(service, max_emails=20):
    """Analyze recent emails grouped by sender."""
    print("\nAnalyzing recent emails by sender...")
    
    # Get recent emails
    results = service.users().messages().list(userId='me', maxResults=max_emails).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("No emails found in your account.")
        return
    
    senders = {}
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        
        # Get labels for this message
        labels = msg.get('labelIds', [])
        
        # Extract sender
        sender = "Unknown"
        subject = "No subject"
        for header in msg['payload'].get('headers', []):
            if header['name'] == 'From':
                sender = header['value']
            elif header['name'] == 'Subject':
                subject = header['value']
        
        if sender not in senders:
            senders[sender] = {'count': 0, 'labels': set(), 'subjects': []}
        
        senders[sender]['count'] += 1
        senders[sender]['labels'].update(labels)
        senders[sender]['subjects'].append(subject)
    
    print("\nRecent emails by sender:")
    for sender, data in sorted(senders.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"\nSender: {sender}")
        print(f"Count: {data['count']} emails")
        print(f"Categories: {', '.join(data['labels'])}")
        print(f"Recent subjects: {data['subjects'][0:2]}")
    
    return senders

def main():
    service = authenticate_gmail()
    
    # First, list all Gmail categories and their counts
    labels = list_gmail_categories(service)
    
    # Then analyze recent emails by sender
    senders = analyze_emails_by_sender(service)
    
    print("\nBased on this analysis, you can create a targeted cleanup script.")
    print("Look for patterns in sender names and which categories they appear in.")
    print("Then update your script to target specific senders in specific categories.")

if __name__ == '__main__':
    main()