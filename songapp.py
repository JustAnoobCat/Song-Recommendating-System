import streamlit as st
import requests
import pickle
import pandas as pd
from io import BytesIO

# Function to get song details from Spotify
def get_song_details(track_id, access_token):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        track = response.json()
        title = track["name"]
        artist = ", ".join([artist["name"] for artist in track["artists"]])
        cover_url = track["album"]["images"][0]["url"]  # Album cover URL
        track_url = track["external_urls"]["spotify"]  # Spotify URL for the track
        return title, artist, cover_url, track_url
    else:
        raise Exception(f"Error: {response.status_code}, {response.json()}")

# Function to recommend songs
def recommend(song, song_list, similarity):
    # Get the index of the chosen song
    index = song_list[song_list['track_name'] == song].index[0]
    
    # Get the similarity scores for that song
    distances = similarity[index]
    
    # Sort the distances and get the top 5 recommendations (excluding the song itself)
    songs = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    # Get the track names of the recommended songs
    recommendation = []
    for i in songs:
        recommendation.append(song_list.iloc[i[0]].track_name)
    return recommendation

# Function to load similarity matrix from Google Drive
def load_similarity_from_drive():
    file_url = "https://drive.google.com/uc?export=download&id=1eLQ5bZYp3nduFFWZtm7s8QrCZKHvoUfN"
    response = requests.get(file_url)
    if response.status_code == 200:
        similarity = pickle.load(BytesIO(response.content))
        return similarity
    else:
        raise Exception(f"Error downloading similarity.pkl: {response.status_code}")

# Load the song data and similarity matrix
song_list = pickle.load(open('songs.pkl', 'rb'))  # Assuming songs.pkl is stored locally or uploaded
similarity = load_similarity_from_drive()

# Ensure the song_list is a DataFrame and contains the 'track_name' column
if isinstance(song_list, pd.DataFrame):
    song_names = song_list['track_name'].values
else:
    # If it's not a DataFrame, handle the error
    st.error("The song list is not a DataFrame as expected!")
    song_names = []

# Streamlit UI elements
st.title("Song Recommendation System")
song = st.selectbox("Choose a song", song_names)

# Spotify access token
access_token = "BQBX0Gy643ooRfsQ0nD6zqQEhuFJihbdgZHbJtP6Yh8KXRDFxwqIXuUVtz82TldvCQ6fiTQY_BmXWFdgz_LaUHRdvmtRRYynC3Hr2EsD586Uo78uyYc"

if st.button('Recommend'):
    # Call the recommend function
    recommendations = recommend(song, song_list, similarity)
    
    # Show the recommended songs with details
    st.write(f"Recommendations for '{song}':")
    for rec_song in recommendations:
        # Get details for each recommended song
        try:
            title, artist, cover_url, track_url = get_song_details(rec_song, access_token)
            # Display song cover and details
            st.markdown(f"[![{title}]({cover_url})]({track_url})", unsafe_allow_html=True)
            st.write(f"**{title}** by {artist}")
        except Exception as e:
            st.error(f"Error fetching details for '{rec_song}': {e}")
