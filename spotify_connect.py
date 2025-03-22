# Spotify API Connection with SSL Fix
# This script handles authentication and basic artist lookup using .env for credentials

import base64
import requests
import json
import os
from dotenv import load_dotenv
import urllib3
import ssl
import streamlit as st

# -------- LOAD ENVIRONMENT VARIABLES --------
# Load variables from .env file
load_dotenv()

# -------- SPOTIFY API CONFIGURATION --------
# Get credentials from environment variables
# Read API credentials from Streamlit secrets
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1/"

# -------- SSL FIX OPTIONS --------
# Option 1: Disable SSL verification (only use for testing!)
DISABLE_SSL_VERIFY = False  # Set to True to disable SSL verification (less secure)

# Option 2: Use custom SSL context
def get_custom_ssl_context():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

# -------- SPOTIFY AUTH FUNCTION --------
def get_spotify_token():
    """
    Get an access token from Spotify using client credentials flow
    """
    # Check if environment variables are set
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("Error: Spotify credentials not found in .env file")
        return None
        
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}
    
    try:
        if DISABLE_SSL_VERIFY:
            # Option 1: Disable SSL verification (less secure)
            response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data, verify=False)
        else:
            # Standard request
            response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
        
        json_result = response.json()
        
        if "access_token" in json_result:
            return json_result["access_token"]
        else:
            print(f"Error getting token: {json_result}")
            return None
    except requests.exceptions.SSLError as e:
        print(f"SSL Error when connecting to Spotify: {e}")
        print("Try setting DISABLE_SSL_VERIFY to True if you're just testing")
        return None
    except Exception as e:
        print(f"Error connecting to Spotify: {e}")
        return None

# -------- SPOTIFY API FUNCTIONS --------
def get_headers(token):
    """
    Create headers with the access token for Spotify API requests
    """
    return {"Authorization": f"Bearer {token}"}

def search_artist(token, artist_name):
    """
    Search for an artist by name and return their information
    """
    headers = get_headers(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = SPOTIFY_API_BASE_URL + "search" + query
    
    try:
        if DISABLE_SSL_VERIFY:
            # Option 1: Disable SSL verification (less secure)
            response = requests.get(query_url, headers=headers, verify=False)
        else:
            # Standard request
            response = requests.get(query_url, headers=headers)
            
        json_result = response.json()
        
        if "artists" in json_result and json_result["artists"]["items"]:
            return json_result["artists"]["items"][0]
        else:
            print(f"Artist '{artist_name}' not found")
            return None
    except requests.exceptions.SSLError as e:
        print(f"SSL Error when searching for artist: {e}")
        print("Try setting DISABLE_SSL_VERIFY to True if you're just testing")
        return None
    except Exception as e:
        print(f"Error searching for artist: {e}")
        return None

# -------- TEST CONNECTION --------
def test_spotify_connection(artist_name):
    """
    Test the Spotify API connection by looking up an artist
    """
    print("Testing Spotify API connection...")
    
    # Disable SSL warnings if verification is disabled
    if DISABLE_SSL_VERIFY:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("Warning: SSL verification is disabled!")
    
    # Get access token
    token = get_spotify_token()
    if not token:
        return "Failed to authenticate with Spotify API"
    
    print("✓ Successfully obtained Spotify access token")
    
    # Search for artist
    artist = search_artist(token, artist_name)
    if not artist:
        return f"Could not find artist: {artist_name}"
    
    # Print artist info
    print(f"✓ Successfully found artist: {artist['name']}")
    print(f"  Artist ID: {artist['id']}")
    print(f"  Popularity: {artist['popularity']}/100")
    print(f"  Genres: {', '.join(artist['genres'])}")
    print(f"  Followers: {artist['followers']['total']:,}")
    
    return {
        "artist_name": artist['name'],
        "artist_id": artist['id'],
        "success": True
    }

# -------- EXAMPLE USAGE --------
if __name__ == "__main__":
    # Replace with your desired artist
    test_artist = "Doechii"
    results = test_spotify_connection(test_artist)
    
    if isinstance(results, dict) and results["success"]:
        print("\nConnection test successful!")
    else:
        print("\nConnection test failed:", results)