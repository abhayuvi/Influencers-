import requests
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_email, subject, body, from_email, password):
    """
    Sends an email using SMTP.
    """
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def get_influencer_data(access_token, user_id):
    """
    Fetches data for a given influencer from Instagram.
    """
    url = f"https://graph.instagram.com/{user_id}"
    params = {'fields': 'id,username,followers_count,media_count', 'access_token': access_token}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        media_url = f"https://graph.instagram.com/{user_id}/media"
        media_params = {'fields': 'id,like_count,comments_count', 'access_token': access_token}
        media_response = requests.get(media_url, params=media_params)
        media_response.raise_for_status()
        media_data = media_response.json()

        total_interactions = sum(
            item['like_count'] + item['comments_count'] for item in media_data.get('data', [])
        )
        engagement_rate = (total_interactions / data['followers_count']) * 100 if data['followers_count'] else 0

        return {
            'id': data['id'],
            'username': data['username'],
            'followers_count': data['followers_count'],
            'media_count': data['media_count'],
            'engagement_rate': engagement_rate
        }
    except Exception as e:
        print(f"Error fetching data for user {user_id}: {e}")
        return None

def store_data_to_excel(influencer_data, filename):
    """
    Saves influencer data to an Excel file.
    """
    df = pd.DataFrame(influencer_data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

def batch_process_influencers(input_filename, access_token, email_subject, email_body_template, from_email, email_password, output_filename='influencer_campaign_data.xlsx', batch_size=500, max_followers=100000):
    """
    Processes influencers in batches: fetches data, sends emails, and saves to Excel.
    """
    # Load influencer data from the input file
    if input_filename.endswith('.csv'):
        df = pd.read_csv(input_filename)
    elif input_filename.endswith('.xlsx'):
        df = pd.read_excel(input_filename)
    elif input_filename.endswith('.txt'):
        df = pd.read_csv(input_filename, delimiter='\t')
    else:
        raise ValueError("Unsupported file format. Please use .txt, .csv, or .xlsx")

    influencer_data_list = []
    total_influencers = len(df)

    for index, row in df.iterrows():
        user_id = row['user_id']
        email = row.get('email')
        
        if not email:
            print(f"No email address provided for user {user_id}")
            continue

        data = get_influencer_data(access_token, user_id)
        if data and data['followers_count'] <= max_followers:
            influencer_data_list.append(data)
            
            # Send an email to the influencer
            email_body = email_body_template.format(username=data['username'])
            send_email(email, email_subject, email_body, from_email, email_password)

        # Save data periodically
        if (index + 1) % batch_size == 0 or (index + 1) == total_influencers:
            store_data_to_excel(influencer_data_list, output_filename)
            influencer_data_list = []  # Clear data for the next batch
            print(f"Processed {index + 1}/{total_influencers} influencers")

# Example usage
input_filename = 'influencers_list.csv'
output_filename = 'influencer_campaign_data.xlsx'
access_token = 'YOUR_ACCESS_TOKEN'
from_email = 'your_email@example.com'
email_password = 'your_email_password'
email_subject = 'Collaboration Opportunity'
email_body_template = 'Hi {username},\n\nWe are interested in collaborating with you for an upcoming campaign. Let us know if you’re interested!'

batch_process_influencers(input_filename, access_token, email_subject, email_body_template, from_email, email_password, output_filename)


"""
'send_email' Function: Sends an email to a specified address.
'get_influencer_data' Function: Retrieves data from Instagram for a given user ID.
'store_data_to_excel' Function: Saves collected influencer data to an Excel file.
'batch_process_influencers' Function: Manages the workflow for processing influencers, including fetching data, sending emails, and saving results.

Usage:
Input File: The file should contain columns for user_id and email.
Parameters: Adjust file names, access tokens, email credentials, and templates as needed.
Batch Size: Controls how many influencers are processed before saving the data to Excel.

"""
