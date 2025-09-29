import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import boto3
from datetime import datetime

# ==============================================
# AWS Lambda Function: Spotify Raw Data Extract
# ==============================================
# Purpose:
#   - Connect to Spotify API (using Spotipy client).
#   - Extract tracks from a specific playlist (Global Top 50).
#   - Save raw JSON response into S3 for further processing.
#
# ETL Stage: Extract + Load (Raw Data)
# ==============================================
 

# This code is written for AWS Lambda function.
# Its purpose: extract playlist data from Spotify API and upload raw JSON to S3.

def lambda_handler(event, context):

    # 1. Get Spotify API credentials from Lambda environment variables
    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')

    # 2. Authenticate with Spotify API using Client Credentials Flow
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # 3. (Optional) Get user playlists (not directly used later in this code)
    playlists = sp.user_playlists('spotify')

    # 4. Define which playlist to fetch (Global Top 50 in this case)
    playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=1333723a6eff4b7f"
    playlist_URI = playlist_link.split("/")[-1].split("?")[0]  # Extract playlist ID from URL

    # 5. Call Spotify API to get all tracks in the playlist
    spotify_data = sp.playlist_tracks(playlist_URI)

    # 6. Connect to AWS S3 using boto3
    client = boto3.client('s3')

    # 7. Create a filename with timestamp for uniqueness
    filename = "spotify_raw_" + str(datetime.now()) + ".json"

    # 8. Upload the raw JSON data to S3 (in 'raw_data/to_processed/' folder)
    client.put_object(
        Bucket="spotify-etl-project-tasneem",           # Your S3 bucket name
        Key="raw_data/to_processed/" + filename,        # Folder path + filename
        Body=json.dumps(spotify_data)                   # Convert Python dict to JSON string
    )

