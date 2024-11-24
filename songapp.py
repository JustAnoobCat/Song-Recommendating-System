import streamlit as st
import pickle
import pandas as pd

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

# Load the song data and similarity matrix
song_list = pickle.load(open('songs.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Ensure the song_list is a DataFrame and contains the 'track_name' column
if isinstance(song_list, pd.DataFrame):
    song_names = song_list['track_name'].values
else:
    # If it's not a DataFrame, we should handle it accordingly
    st.error("The song list is not a DataFrame as expected!")
    song_names = []

# Streamlit UI elements
st.title("Song Recommendation System")
song = st.selectbox("Choose a song", song_names)

if st.button('Recommend'):
    # Call the recommend function
    recommendations = recommend(song, song_list, similarity)
    st.write(f"Recommendations for '{song}':")
    for i, rec_song in enumerate(recommendations, 1):
        st.write(f"{i}. {rec_song}")
