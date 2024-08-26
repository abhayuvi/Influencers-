import pandas as pd
import requests

def fetch_influencer_data(access_token, user_id):
    """
    Fetches data for a given influencer from Instagram Graph API.
    """
    # Define API endpoint and parameters
    url = f"https://graph.instagram.com/{user_id}"
    params = {
        'fields': 'id,username,followers_count,media_count',
        'access_token': access_token
    }
    
    # Make request to the API
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Fetch media data to calculate engagement
        media_url = f"https://graph.instagram.com/{user_id}/media"
        media_params = {
            'fields': 'id,like_count,comments_count',
            'access_token': access_token
        }
        media_response = requests.get(media_url, params=media_params)
        media_data = media_response.json()
        
        # Calculate engagement rate
        if 'data' in media_data:
            total_interactions = sum(
                item['like_count'] + item['comments_count'] for item in media_data['data']
            )
            engagement_rate = (total_interactions / data['followers_count']) * 100
        else:
            engagement_rate = 0 
        
        return {
            'id': data['id'],
            'username': data['username'],
            'followers_count': data['followers_count'],
            'media_count': data['media_count'],
            'engagement_rate': engagement_rate
        }
    else:
        print(f"Error fetching data for user {user_id}: {response.status_code}, {response.text}")
        return None

def save_data_to_excel(influencers_data, filename):
    """
    Saves the influencer data to an Excel file.
    """
    df = pd.DataFrame(influencers_data)
    df.to_excel(filename, index=False)
    print(f"Data successfully saved to {filename}")

def filter_and_save_influencers(input_filename, output_filename, access_token, max_followers=100000):
    """
    Filters influencers based on follower count and saves their data to an Excel file.
    """
    # Load the list of influencers from the input file
    if input_filename.endswith('.csv'):
        df = pd.read_csv(input_filename)
    elif input_filename.endswith('.xlsx'):
        df = pd.read_excel(input_filename)
    elif input_filename.endswith('.txt'):
        df = pd.read_csv(input_filename, delimiter='\t')  # Assuming tab-separated for .txt
    else:
        raise ValueError("Unsupported file format. Please use .txt, .csv, or .xlsx")
    
    influencer_data_list = []
    
    # Iterate through each influencer and fetch their data
    for index, row in df.iterrows():
        user_id = row['user_id']  # Ensure this matches the column name in your file
        data = fetch_influencer_data(access_token, user_id)
        if data and data['followers_count'] <= max_followers:
            influencer_data_list.append(data)
    
    # Save the filtered influencer data to an Excel file
    save_data_to_excel(influencer_data_list, output_filename)

# Example usage
input_filename = 'influencers_list.csv'  # Replace with your actual file
output_filename = 'filtered_micro_nano_influencers.xlsx'
access_token = 'YOUR_ACCESS_TOKEN' #Instagram Graph Api Access token

filter_and_save_influencers(input_filename, output_filename, access_token)

"""
'fetch_influencer_data' Function: Retrieves influencer data and calculates the engagement rate.
'save_data_to_excel' Function: Saves the collected data to an Excel file.
'filter_and_save_influencers' Function: Loads influencer data from a file, filters based on follower count, and saves the filtered data.

"""

