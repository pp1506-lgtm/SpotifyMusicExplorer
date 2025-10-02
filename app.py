import streamlit as st
import pandas as pd
from utils.data_processing import load_all_data, get_most_popular_songs, get_top_artists, get_most_popular_song_by_year, compare_artists, get_songs_by_vibe
from utils.visualization_functions import plot_top_artists_interactive
import plotly.express as px

# Set Streamlit page config
st.set_page_config(
    page_title="Spotify Music Explorer 🎶",
    page_icon=":musical_note:",
    layout="wide"
)

st.title('🎵 Spotify Data Explorer')
st.markdown("Dive into the world of music data (merged dataset).")

# Sidebar for navigation
st.sidebar.header('Dashboard Options')
selected_section = st.sidebar.radio(
    'Choose a section:',
    ['Top Charts', 'Vibe Explorer', 'Music Insights']
)

# Load the single aggregated dataset at the start
all_data_df = load_all_data()

# If dataset failed to load, show clear message and stop further UI usage
if all_data_df is None or all_data_df.empty:
    st.error("Dataset not loaded or empty. Place 'spotify_tracks.csv' or 'best-songs-on-spotify-for-every-year-2000-2023.csv' in the data/ folder.")
    st.stop()

# --- Top Charts Section ---
# --- Top Charts Section ---
if selected_section == 'Top Charts':
    st.header('📈 Top Charts by Year')

    if "year" in all_data_df.columns and not all_data_df["year"].isna().all():
        # Drop NA, keep unique, sort in reverse
        years = sorted(all_data_df["year"].dropna().unique().tolist(), reverse=True)
    else:
        years = []

    if not years:
        st.warning("No 'year' column or valid year values available in dataset.")
    else:
        selected_year = st.selectbox("Select a Year:", years)

        yearly_top_artists = get_top_artists(all_data_df, selected_year)
        st.subheader(f"Top Artists for {selected_year}")

        if yearly_top_artists is not None and not yearly_top_artists.empty:
            plot_top_artists_interactive(yearly_top_artists)
        else:
            st.info("No artist popularity data available for this year.")

        st.subheader(f"Most Popular Songs for {selected_year}")
        top_songs = get_most_popular_songs(all_data_df, selected_year).head(20)
        if not top_songs.empty and {"title", "artist", "popularity"}.issubset(top_songs.columns):
            st.dataframe(top_songs[["title", "artist", "popularity"]])
        else:
            st.info("Song-level popularity data is not available for this year.")

    
# --- Vibe Explorer Section ---
elif selected_section == 'Vibe Explorer':
    st.header('🔮 Vibe Explorer & Playlist Generator')
    st.write("Discover songs based on their mood and generate a random playlist.")
    
    # Check presence of audio features
    feature_cols = {'danceability', 'energy', 'valence', 'acousticness'}
    has_features = feature_cols.issubset(set(all_data_df.columns))
    if not has_features:
        st.warning("Audio feature columns (danceability, energy, valence, acousticness) are not fully available. Vibe Explorer will be limited or disabled.")
    
    vibe_choice = st.selectbox('Choose a vibe:', ['chill', 'energetic', 'gloomy', 'party', 'sporty'])
    num_songs = st.slider('Number of songs to include:', min_value=5, max_value=50, value=15)
    
    if st.button('Generate Playlist'):
        songs = get_songs_by_vibe(all_data_df, vibe_choice, num_songs)
        
        st.subheader(f'Your {vibe_choice.capitalize()} Playlist')
        if not songs.empty and set(['title', 'artist', 'popularity']).issubset(songs.columns):
            st.dataframe(songs[['title', 'artist', 'popularity']])
        else:
            st.warning("No songs found for that vibe (or audio feature data missing).")
    
# --- Music Insights Section ---
elif selected_section == 'Music Insights':
    st.header('✨ Music Insights & Games')
    st.write("Fun facts and comparisons about music data.")
    
    years = []
    if 'year' in all_data_df.columns:
        try:
            years = sorted([int(y) for y in all_data_df['year'].dropna().unique().tolist()])
        except Exception:
            years = []
    if not years:
        st.warning("No year data available.")
        st.stop()
    
    st.subheader("What was the most popular song in your birth year?")
    birth_year = st.slider('Select your birth year:', min_value=min(years), max_value=max(years), value=min(years))
    top_song, popularity = get_most_popular_song_by_year(all_data_df, birth_year)
    
    if top_song:
        st.info(f"The most popular song in {birth_year} was **'{top_song}'** with a popularity score of {int(popularity)}!")
    else:
        st.warning(f"No data available for {birth_year}.")
            
    st.markdown("---")
        
    st.subheader("Compare two artists")
    artists_list = sorted(all_data_df['artist'].dropna().unique().tolist())
    
    col1, col2 = st.columns(2)
    with col1:
        artist1 = st.selectbox('Select Artist 1:', artists_list)
    with col2:
        artist2 = st.selectbox('Select Artist 2:', artists_list)
            
    if st.button('Compare'):
        comparison_df = compare_artists(all_data_df, artist1, artist2)
        if not comparison_df.empty:
            fig = px.bar(comparison_df, x='year', y='popularity', color='artist', 
                         barmode='group', title=f'Popularity Comparison: {artist1} vs. {artist2}')
            st.plotly_chart(fig)
        else:
            st.warning("One or both artists not found in the data.")
