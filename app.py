from flask import Flask, render_template, redirect, url_for, flash, session, request
from dotenv import load_dotenv
import os
import time
import personalify

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-for-dev")

# Define the scopes needed for the application
SCOPE = "playlist-read-private playlist-read-collaborative user-library-read playlist-modify-private playlist-modify-public"

@app.route('/')
def index():
    # Check if we have a token in the session
    if 'token_info' not in session:
        return render_template('login.html')

    # Check if token is expired
    now = int(time.time())
    if session['token_info']['expires_at'] - now < 60:
        return redirect(url_for('login'))

    try:
        sp = personalify.get_spotify_client(scope=SCOPE, username=session.get('user_id'))
        
        # Get user playlists for the forms
        user_playlists = []
        playlists = sp.current_user_playlists(limit=50)
        while playlists:
            user_playlists.extend(playlists['items'])
            playlists = sp.next(playlists) if playlists['next'] else None

        # Get excluded playlists to display them, now with remaining run counts
        excluded_playlist_runs = personalify.get_excluded_playlist_runs()
        excluded_playlists_with_runs = []
        if excluded_playlist_runs:
            # Using a set to avoid fetching details for the same playlist multiple times
            all_excluded_ids = {pid for run in excluded_playlist_runs for pid in run}
            fetched_playlists = {}
            for p_id in all_excluded_ids:
                try:
                    fetched_playlists[p_id] = sp.playlist(p_id)
                except Exception:
                    fetched_playlists[p_id] = None # Handle deleted playlists

            for i, run in enumerate(excluded_playlist_runs):
                runs_ago = len(excluded_playlist_runs) - 1 - i
                runs_remaining = personalify.PLAYLIST_EXCLUSION_RUNS - runs_ago
                for p_id in run:
                    playlist_details = fetched_playlists.get(p_id)
                    if playlist_details:
                        excluded_playlists_with_runs.append({
                            "details": playlist_details,
                            "runs_remaining": runs_remaining
                        })
        
        return render_template('index.html', playlists=user_playlists, excluded_playlists=excluded_playlists_with_runs)
    except Exception as e:
        flash(f"An error occurred: {e}", 'danger')
        return render_template('login.html')


@app.route('/login')
def login():
    # Create an auth_manager and get the authorization URL
    auth_manager = personalify.get_spotify_client(scope=SCOPE).auth_manager
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    # Exchange the authorization code for an access token
    auth_manager = personalify.get_spotify_client(scope=SCOPE).auth_manager
    auth_manager.get_access_token(request.args.get('code'))
    
    # Get the user's profile information
    sp = personalify.get_spotify_client(scope=SCOPE)
    user_info = sp.current_user()

    # Store token info and user ID in session
    session['token_info'] = auth_manager.get_cached_token()
    session['user_id'] = user_info['id']
    
    flash("Successfully logged in!", "success")
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    # Also remove the cache file
    if os.path.exists(".cache"):
        os.remove(".cache")
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


@app.route('/manage-exclusions', methods=['POST'])
def manage_exclusions():
    if 'token_info' not in session:
        return redirect(url_for('login'))

    if 'clear_all' in request.form:
        personalify.clear_playlist_exclusions()
        flash("Playlist exclusion list has been cleared.", "success")
    elif 'remove_playlist_id' in request.form:
        playlist_id = request.form.get('remove_playlist_id')
        personalify.remove_playlist_from_exclusion(playlist_id)
        flash("Playlist removed from exclusion list.", "success")
        
    return redirect(url_for('index'))


@app.route('/run', methods=['POST'])
def run_script():
    if 'token_info' not in session:
        flash("You must be logged in to run the script.", 'warning')
        return redirect(url_for('login'))

    try:
        sp = personalify.get_spotify_client(scope=SCOPE, username=session.get('user_id'))
        
        # --- Gather all form data ---
        num_songs = int(request.form.get('num_songs', 20))
        include_liked_songs = 'include_liked_songs' in request.form
        
        # Target playlist logic
        target_playlist_id = request.form.get('target_playlist')
        create_new_playlist_name = request.form.get('new_playlist_name')
        if create_new_playlist_name: # If user provided a name for a new playlist, prioritize it
            target_playlist_id = None
        
        # Source playlist logic
        source_method = request.form.get('source_method')
        source_playlist_ids = None
        num_random_playlists = None
        if source_method == 'random':
            num_random_playlists = int(request.form.get('num_random_playlists', 5))
        else: # 'manual'
            source_playlist_ids = request.form.getlist('source_playlists')

        message = personalify.run_spotify_shuffle(
            sp=sp,
            user_id=session['user_id'],
            num_songs=num_songs,
            include_liked_songs=include_liked_songs,
            target_playlist_id=target_playlist_id,
            create_new_playlist_name=create_new_playlist_name,
            source_playlist_ids=source_playlist_ids,
            num_random_playlists=num_random_playlists
        )
        flash(message, 'success')
    except Exception as e:
        flash(f"An error occurred: {e}", 'danger')
        
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=8888) 