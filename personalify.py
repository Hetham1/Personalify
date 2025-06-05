import os
import random
import json
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables from .env file
load_dotenv()

# Constants
EXCLUDED_SONGS_FILE = 'excluded_songs.json'
EXCLUDED_PLAYLISTS_FILE = 'excluded_playlists.json'
SONG_EXCLUSION_WINDOW = 4
PLAYLIST_EXCLUSION_RUNS = 5 # A playlist will be excluded for 5 runs of the 'random' option

def get_spotify_client(scope, username=None):
    """Initializes and returns a Spotipy client."""
    cache_path = f".cache-{username}" if username else ".cache"
    auth_manager = SpotifyOAuth(
        scope=scope,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        username=username,
        cache_path=cache_path,
        show_dialog=True
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def _load_json_file(filename):
    """Loads data from a JSON file, returning empty list if not found."""
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)

def _save_json_file(filename, data):
    """Saves data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f)

def get_excluded_playlist_runs():
    """
    Returns the list of excluded playlist ID runs.
    Handles migration from old flat list format.
    """
    data = _load_json_file(EXCLUDED_PLAYLISTS_FILE)
    if not data:
        return []
    
    # Migration check: if the first element is a string, it's the old flat-list format.
    if isinstance(data[0], str):
        # Old format detected. Wrap the entire flat list into a single run.
        print("Old 'excluded_playlists.json' format detected. Migrating to new format.")
        migrated_data = [data] 
        _save_json_file(EXCLUDED_PLAYLISTS_FILE, migrated_data)
        return migrated_data
    
    # If it's not a string, we assume it's the new list-of-lists format.
    return data

def remove_playlist_from_exclusion(playlist_id_to_remove):
    """Removes a specific playlist from all runs in the exclusion list."""
    excluded_runs = get_excluded_playlist_runs()
    updated_runs = []
    for run in excluded_runs:
        updated_run = [pid for pid in run if pid != playlist_id_to_remove]
        if updated_run: # Only keep run if it's not empty
            updated_runs.append(updated_run)
    _save_json_file(EXCLUDED_PLAYLISTS_FILE, updated_runs)

def clear_playlist_exclusions():
    """Clears the entire playlist exclusion list."""
    _save_json_file(EXCLUDED_PLAYLISTS_FILE, [])

def fetch_all_songs(sp, source_playlist_ids, include_liked_songs=False):
    """Fetches all songs from a given list of playlists."""
    all_track_ids = set()
    print(f"Fetching songs from {len(source_playlist_ids)} playlists...")
    for playlist_id in source_playlist_ids:
        tracks = sp.playlist_tracks(playlist_id)
        while tracks:
            for item in tracks['items']:
                if item['track'] and item['track']['id']:
                    all_track_ids.add(item['track']['id'])
            tracks = sp.next(tracks) if tracks['next'] else None

    # Also include user's liked songs if requested
    if include_liked_songs:
        print("Fetching liked songs...")
        liked_tracks = sp.current_user_saved_tracks(limit=50)
        while liked_tracks:
            for item in liked_tracks['items']:
                if item['track'] and item['track']['id']:
                    all_track_ids.add(item['track']['id'])
            liked_tracks = sp.next(liked_tracks) if liked_tracks['next'] else None
    
    print(f"Found {len(all_track_ids)} unique songs.")
    return list(all_track_ids)

def run_spotify_shuffle(
    sp,
    user_id,
    num_songs,
    include_liked_songs=False,
    target_playlist_id=None,
    create_new_playlist_name=None,
    source_playlist_ids=None,
    num_random_playlists=None
):
    """
    The main engine for fetching, shuffling, and adding songs to a playlist.
    """
    # 1. Determine the target playlist
    if create_new_playlist_name:
        new_playlist = sp.user_playlist_create(user_id, create_new_playlist_name, public=False)
        final_target_playlist_id = new_playlist['id']
    else:
        final_target_playlist_id = target_playlist_id

    if not final_target_playlist_id:
        return "No target playlist specified. Please select an existing playlist or provide a name for a new one."

    # 2. Determine the source playlists for songs
    final_source_playlist_ids = []
    if num_random_playlists and num_random_playlists > 0:
        excluded_runs = _load_json_file(EXCLUDED_PLAYLISTS_FILE)
        # Flatten the list of lists to get all unique excluded IDs
        excluded_playlists = {pid for run in excluded_runs for pid in run}
        
        all_user_playlists = []
        playlists = sp.current_user_playlists(limit=50)
        while playlists:
            all_user_playlists.extend(p['id'] for p in playlists['items'] if p['owner']['id'] != 'spotify')
            playlists = sp.next(playlists) if playlists['next'] else None
        
        available_playlists = [p for p in all_user_playlists if p not in excluded_playlists]
        if len(available_playlists) < num_random_playlists:
            return f"Not enough new playlists to choose from. Only {len(available_playlists)} available."
        
        final_source_playlist_ids = random.sample(available_playlists, num_random_playlists)
        
        # Add the new run and trim the list to the window size
        excluded_runs.append(final_source_playlist_ids)
        updated_excluded_runs = excluded_runs[-PLAYLIST_EXCLUSION_RUNS:]
        _save_json_file(EXCLUDED_PLAYLISTS_FILE, updated_excluded_runs)
    else:
        final_source_playlist_ids = source_playlist_ids

    if not final_source_playlist_ids and not include_liked_songs:
        return "No source playlists selected and 'Include Liked Songs' is unchecked. Please select a source."

    # 3. Fetch all songs from the determined source playlists
    all_songs = fetch_all_songs(sp, final_source_playlist_ids, include_liked_songs)

    # 4. Filter out songs that have been added recently
    excluded_songs = _load_json_file(EXCLUDED_SONGS_FILE)
    available_songs = [song for song in all_songs if song not in excluded_songs]

    if len(available_songs) < num_songs:
        return f"Not enough available songs to select {num_songs}. Only found {len(available_songs)}."

    # 5. Shuffle, select, and add songs to the target playlist
    random.shuffle(available_songs)
    songs_to_add = available_songs[:num_songs]
    sp.playlist_replace_items(final_target_playlist_id, songs_to_add)

    # 6. Update the song exclusion list
    new_excluded_songs = excluded_songs + songs_to_add
    songs_to_keep = num_songs * SONG_EXCLUSION_WINDOW
    _save_json_file(EXCLUDED_SONGS_FILE, new_excluded_songs[-songs_to_keep:])
    
    return f"Success! Added {len(songs_to_add)} new songs to your playlist." 