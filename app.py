import pickle
import streamlit as st
import pandas as pd
import requests
from spotify import get_spotify_access_token

# Custom CSS for theme
st.markdown("""
    <style>
        body {
            background-color: #2c2c54;
            color: #dcdde1;
        }
        .stButton>button {
            background-color: #44bd32;
            color: white;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #4cd137;
        }
        .stSelectbox>div {
            background-color: #2f3640;
            color: white;
            border-radius: 8px;
            padding: 5px;
        }
        .stCaption {
            color: #f5f6fa;
        }
        img {
            border-radius: 15px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #00a8ff;
        }
    </style>
""", unsafe_allow_html=True)

def get_song_album_cover_url(track_id, access_token):
    try:
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            track = response.json()
            title = track["name"]
            artist = ", ".join([artist["name"] for artist in track["artists"]])
            cover_url = track["album"]["images"][0]["url"]
            return title, artist, cover_url
        else:
            return None, None, None
    except Exception as e:
        st.error(f"Error fetching song details: {e}")
        return None, None, None

def recommend(song, song_list, similarity, n_recommendations=5):
    try:
        # Get the index of the selected song based on 'track_name'
        index = song_list[song_list['track_name'] == song].index[0]

        # Get similarity scores for the selected song and sort by relevance
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:]

        # Initialize lists to store recommended songs and track IDs
        recommended_music_names = []
        recommended_music_track_ids = []
        recommended_indices = set()  # To keep track of already recommended songs

        for i in distances:
            song_index = i[0]
            if song_index not in recommended_indices:  # Only recommend if not already recommended
                recommended_music_names.append(song_list.iloc[song_index]['track_name'])  # Correct column name
                recommended_music_track_ids.append(song_list.iloc[song_index]['track_id'])  # Correct column name
                recommended_indices.add(song_index)
                if len(recommended_music_names) >= n_recommendations:  # Limit to n recommendations
                    break

        return recommended_music_names, recommended_music_track_ids
    except IndexError:
        st.error("Selected song is not in the dataset. Please try another song.")
        return [], []

# Load data
try:
    song_list = pickle.load(open('songs.pkl', 'rb'))
    similarity = pd.read_csv('song_recommendations.csv', header=None).values
    music_list = song_list['track_name'].values
except FileNotFoundError as e:
    st.error(f"Error loading data files: {e}")
    st.stop()

# Access Token (Replace with environment variable for security)
access_token = get_spotify_access_token()

# UI Design
st.title("🎵 Song Recommendation System")
st.write("Find similar songs to your favorites!")

selected_song = st.selectbox("Type or select a song you like:", music_list)

if st.button('Recommend Songs'):
    with st.spinner('Fetching recommendations...'):
        recommended_music_names, recommended_music_track_ids = recommend(selected_song, song_list, similarity)
        
        if recommended_music_names:
            st.subheader("Recommended Songs")
            cols = st.columns(len(recommended_music_names))
            
            for i, col in enumerate(cols):
                with col:
                    title, artist, cover_url = get_song_album_cover_url(recommended_music_track_ids[i], access_token)
                    if cover_url:
                        st.image(cover_url, use_container_width=True)
                        st.caption(f"{title} - {artist}")
                    else:
                        st.warning(f"Details not available for: {recommended_music_names[i]}")
        else:
            st.warning("No recommendations found.")