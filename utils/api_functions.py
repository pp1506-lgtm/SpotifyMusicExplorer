import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

# --- Load API Credentials ---
load_dotenv()
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# --- Scopes for User Authentication ---
SCOPE = "playlist-modify-public user-read-private"

# ==========================
# Get Spotify Access Token
# ==========================
def get_spotify_access_token():
    """Generates and returns a reliable access token."""
    try:
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = requests.post(
            auth_url,
            data={'grant_type': 'client_credentials'},
            auth=(CLIENT_ID, CLIENT_SECRET)
        )
        auth_response.raise_for_status()
        token = auth_response.json()['access_token']
        return token
    except requests.exceptions.RequestException as e:
        st.error(f"Authentication Error: Could not get access token. Check your .env credentials. {e}")
        return None

# ==========================
# Fetch Playlist Data
# ==========================
def get_live_data(playlist_id):
    """
    Fetches tracks from any public Spotify playlist (handles pagination).
    """
    access_token = get_spotify_access_token()
    if not access_token:
        return None

    headers = {'Authorization': f'Bearer {access_token}'}
    all_tracks = []
    limit = 100
    offset = 0

    try:
        while True:
            api_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}"
            response = requests.get(api_url, headers=headers)

            if response.status_code != 200:
                st.error(f"Spotify API error {response.status_code}: {response.text}")
                return None

            results = response.json()
            items = results.get('items', [])
            if not items:
                break

            for item in items:
                track = item.get('track')
                if track:
                    track_name = track.get('name')
                    artist_names = ', '.join([a['name'] for a in track.get('artists', [])])
                    popularity = track.get('popularity')
                    track_uri = track.get('uri')
                    all_tracks.append([track_name, artist_names, popularity, track_uri])

            offset += limit
            if results.get("next") is None:
                break

        if not all_tracks:
            st.warning("No tracks found. Playlist may be restricted or empty.")
            return None

        return pd.DataFrame(all_tracks, columns=['track_name', 'artists', 'popularity', 'track_uri'])

    except Exception as e:
        st.error(f"Unexpected error fetching playlist: {e}")
        return None

# ==========================
# Alternative Debug Method
# ==========================
def get_live_data_via_search():
    """
    Diagnostic: Fetches a list of tracks via a search query.
    Helps confirm API access is working.
    """
    access_token = get_spotify_access_token()
    if not access_token:
        return None
    
    try:
        api_url = 'https://api.spotify.com/v1/search'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'q': 'Taylor Swift', 'type': 'track', 'limit': 10}
        
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        
        results = response.json()
        tracks_data = []
        for track_item in results['tracks']['items']:
            tracks_data.append([
                track_item['name'],
                ', '.join([a['name'] for a in track_item['artists']]),
                track_item['popularity'],
                track_item['uri']
            ])

        return pd.DataFrame(tracks_data, columns=['track_name', 'artists', 'popularity', 'track_uri'])
    except Exception as e:
        st.error(f"Error fetching data via search: {e}")
        return None

# ==========================
# User Authentication Client
# ==========================
def get_user_auth_client():
    """
    Handles user login and returns an authenticated Spotify client.
    Required for playlist creation.
    """
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=".cache",
        show_dialog=True
    )
    token_info = auth_manager.get_cached_token()
    if not token_info:
        auth_url = auth_manager.get_authorize_url()
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### Spotify Login Required")
        st.sidebar.markdown(f"**To create a playlist, please click [Login to Spotify]({auth_url})**")
        st.stop()

    sp_user = spotipy.Spotify(auth=token_info['access_token'])
    try:
        user_profile = sp_user.current_user()
        st.sidebar.success(f"Logged in as: {user_profile['display_name']}")
        return sp_user
    except Exception:
        if os.path.exists(".cache"):
            os.remove(".cache")
        st.sidebar.error("Session expired. Please re-login.")
        st.experimental_rerun()
        return None

# ==========================
# Playlist Creation
# ==========================
def create_user_playlist(playlist_name, tracks_df):
    """
    Creates a new playlist in the user's Spotify account and adds tracks.
    """
    sp_user = get_user_auth_client()
    if not sp_user:
        return

    user_id = sp_user.current_user()['id']
    track_uris = tracks_df['track_uri'].tolist()

    try:
        playlist = sp_user.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=True,
            description=f"Generated by Streamlit Music Analyzer: Vibe={playlist_name.split(' ')[0]}"
        )
        if track_uris:
            sp_user.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
        st.success(f"Playlist '{playlist_name}' created successfully on your Spotify account!")
        st.markdown(f"**[Open Playlist on Spotify]({playlist['external_urls']['spotify']})**")
    except spotipy.exceptions.SpotifyException as e:
        st.error(f"Failed to create playlist. Error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
import matplotlib.pyplot as plt
import seaborn as sns