import pickle
import streamlit as st
import pandas as pd
import numpy as np
import requests

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
    
    # Ensure that the similarity matrix is a numpy array
    similarity_matrix = similarity.values if isinstance(similarity, pd.DataFrame) else similarity

    # Check if the index is within the valid range of the similarity matrix
    if index >= len(similarity_matrix):
        raise IndexError(f"Index {index} is out of bounds for the similarity matrix.")

    # Get the similarity scores for that song
    distances = similarity_matrix[index]
    
    # Sort the distances and get the top 5 recommendations (excluding the song itself)
    songs = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    # Get the track names of the recommended songs
    recommendation = []
    for i in songs:
        recommendation.append(song_list.iloc[i[0]].track_name)
    return recommendation

# Load the song data and similarity matrix from local files
song_list = pickle.load(open('songs.pkl', 'rb'))  # Ensure this file is saved locally
similarity = pd.read_csv('song_recommendations.csv', header=None)  # Load similarity matrix from CSV

# Ensure the song_list is a DataFrame and contains the 'track_name' and 'track_id' columns
if isinstance(song_list, pd.DataFrame):
    song_names = song_list['track_name'].values
else:
    # If it's not a DataFrame, handle the error
    st.error("The song list is not a DataFrame as expected!")
    song_names = []

# Streamlit UI elements
st.title("Song Recommendation System")
st.subheader("Discover new music based on your favorite tracks!")
selected_song = st.selectbox("Select a song to get recommendations:", song_names)

# Spotify access token (this should be dynamically refreshed in production)
access_token = "BQBEJuD36Q-ZSBmvgfP3agu_S2BcHUMfyRBSYBq9YqYAW7bTyqUYyrhnpCheaclooaP3aiueHAeKIa8WgeoUUyP1z1UnPdVw0oAUFnQaW706fALqq1A"

if st.button('Show Recommendations'):
    # Get the track_id for the selected song
    track_id = song_list[song_list['track_name'] == selected_song].iloc[0]['track_id']
    
    # Call the recommend function
    recommendations = recommend(selected_song, song_list, similarity)
    
    # Show the recommended songs with details
    st.write(f"Recommendations for '{selected_song}':")
    
    # Create a container to hold the images side by side
    col1, col2, col3, col4, col5 = st.columns(5)

    for i, rec_song in enumerate(recommendations):
        # Get the track_id for the recommended song
        rec_track_id = song_list[song_list['track_name'] == rec_song].iloc[0]['track_id']
        
        # Get details for each recommended song using the track_id
        try:
            title, artist, cover_url, track_url = get_song_details(rec_track_id, access_token)
            
            # Display song cover and details in respective columns
            with [col1, col2, col3, col4, col5][i]:
                # Display image with use_container_width=True for proper scaling
                st.image(cover_url, use_container_width=True)
                # Display clickable link for the song
                st.markdown(f"[{title}]({track_url})", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error fetching details for '{rec_song}': {e}")

# Additional customizations for design:
# Adding some padding around elements and customizing background color:
st.markdown("""
    <style>
        .reportview-container {
            background-color: #f0f4f8;
        }
        .stSelectbox, .stButton, .stText {
            font-family: 'Arial', sans-serif;
            font-size: 16px;
            color: #2d2d2d;
        }
        .stButton button {
            background-color: #1db954;
            color: white;
        }
        .stButton button:hover {
            background-color: #1ed760;
        }
    </style>
""", unsafe_allow_html=True)
