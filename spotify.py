import base64
import requests

client_id = "18428bbaf90943a2b3cea8f3bebc4cb2" 
client_secret = "1aaf0fe8f47e4293881c92d8962436dc"

def get_spotify_access_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode("utf-8"),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        raise Exception("Error getting access token from Spotify")
