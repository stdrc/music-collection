from ytmusicapi import OAuthCredentials, YTMusic
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize YTMusic
ytmusic = YTMusic(
    "oauth.json",
    oauth_credentials=OAuthCredentials(
        client_id=os.getenv("YTM_CLIENT_ID", ""),
        client_secret=os.getenv("YTM_CLIENT_SECRET", ""),
    ),
)


# Function to get playlists
def get_playlists():
    playlists = ytmusic.get_library_playlists()
    return playlists


# Function to extract playlist details
def extract_playlist_details(playlists):
    playlist_list = []
    for playlist in playlists:
        playlist_info = {
            "playlist_name": playlist["title"],
            "playlist_id": playlist["playlistId"],
        }
        playlist_list.append(playlist_info)
    return playlist_list


# Function to save playlist details to JSON file
def save_to_json(playlist_list, filename="playlists.json"):
    with open(filename, "w") as json_file:
        json.dump(playlist_list, json_file, indent=4, ensure_ascii=False)
    print(f"Playlist details saved to {filename}")


def main():
    playlists = get_playlists()
    if playlists:
        playlist_list = extract_playlist_details(playlists)
        save_to_json(playlist_list)


if __name__ == "__main__":
    main()
