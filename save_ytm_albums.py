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


# Function to get saved albums
def get_saved_albums():
    albums = ytmusic.get_library_albums(limit=300)
    return albums


# Function to extract album details
def extract_album_details(albums):
    album_list = []
    for album in albums:
        album_info = {
            "album_name": album["title"],
            "album_thumbnail": album["thumbnails"][0]["url"],
            "artist_name": album["artists"][0]["name"],
            "url": f"https://music.youtube.com/browse/{album['browseId']}",
            "year": album.get("year", "Unknown"),  # Add year field
        }
        album_list.append(album_info)
    return album_list


# Function to save album details to JSON file
def save_to_json(album_list, filename="albums.json"):
    with open(filename, "w") as json_file:
        json.dump(album_list, json_file, indent=4, ensure_ascii=False)
    print(f"Album details saved to {filename}")


def main():
    albums = get_saved_albums()
    if albums:
        album_list = extract_album_details(albums)
        save_to_json(album_list)


if __name__ == "__main__":
    main()
