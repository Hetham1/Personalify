# Personalify

Personalify is a web application designed to help you showcase your unique music taste. It intelligently samples songs from across your entire Spotify library—including all your playlists and liked songs—to generate a fresh playlist that acts as a snapshot of what you love to listen to. It's the perfect tool for creating a shareable mix that truly represents your musical identity.

## Features

-   **Showcase Your Taste:** Automatically generate a playlist that represents your unique musical identity, perfect for sharing with friends or for rediscovering forgotten favorites.
-   **Secure Spotify Login:** Authenticates directly with your Spotify account using OAuth.
-   **Flexible Song Sourcing:** Choose songs from specific playlists, your entire Liked Songs collection, or a random selection of your playlists.
-   **Customizable Output:** Select the exact number of songs you want in your new mix.
-   **Smart Exclusions:** Prevents recently added songs and playlists from being chosen again, guaranteeing fresh content.
-   **Create or Update Playlists:** Add the new mix to an existing playlist or have Personalify create a new one for you automatically.
-   **Sleek, Responsive UI:** A modern interface with a Spotify-inspired dark theme that guides you through the process step-by-step.

---

## How to use

1.  Click "Login with Spotify" and authorize the application.
2.  Follow the on-screen, step-by-step instructions to select your source playlists, target playlist, and other options.
3.  Click "Generate My Playlist" and enjoy your fresh mix on Spotify!

---

## Instructions for Developers (Running Locally)

If you want to clone this repository and run the application on your local machine, follow these steps.

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/personalify.git
cd personalify
```

### Step 2: Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# For Windows
python -m venv venv
venv\\Scripts\\activate

# For macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

Install all required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Spotify API Credentials

1.  Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and create a new application.
2.  Once your app is created, copy the **Client ID** and **Client Secret**.
3.  Click "Edit Settings" on your Spotify app. Add a **Redirect URI** for local development. This must be exactly: `http://127.0.0.1:8888/callback`
4.  Save the settings.

### Step 5: Create the Environment File

1.  In the root of the project directory, create a file named `.env`.
2.  Add the following key-value pairs to the file, pasting your own credentials where indicated. The `FLASK_SECRET_KEY` can be any long, random string.

    ```env
    SPOTIPY_CLIENT_ID="YOUR_CLIENT_ID"
    SPOTIPY_CLIENT_SECRET="YOUR_CLIENT_SECRET"
    SPOTIPY_REDIRECT_URI="http://127.0.0.1:8888/callback"
    FLASK_SECRET_KEY="a-very-long-and-random-string-for-flask-sessions"
    ```

### Step 6: Run the Application

You are now ready to run the Flask development server.

```bash
python app.py
```

Open your web browser and navigate to `http://127.0.0.1:8888` to see the application in action.

---

## How It Works

Personalify is a Python-based web application built with the Flask microframework. Here's a breakdown of its architecture:

### 1. Frontend

-   The user interface is built with standard HTML and styled using the **Bootstrap** framework combined with custom CSS for the Spotify-inspired dark theme.
-   It uses a multi-step "wizard" interface powered by JavaScript to guide the user through the playlist creation process in a clear, sequential manner.
-   All UI is rendered server-side by Flask using **Jinja2** templates.

### 2. Backend (Flask)

-   The server is written in Python using **Flask**. It handles user sessions, authentication, and form submissions.
-   It communicates with the core logic in `personalify.py` to perform the main Spotify operations.
-   User authentication is managed via Flask sessions, which securely store the Spotify OAuth tokens after a user logs in.

### 3. Spotify API Integration

-   Interaction with the Spotify Web API is handled by the excellent **`spotipy`** library.
-   The application uses the **OAuth 2.0 Authorization Code Flow** to get permission from the user to read their library and create/modify playlists. The required scopes are requested upon the initial login.

### 4. Core Logic (`personalify.py`)

The playlist generation follows these steps:

1.  **Source Selection:** Gathers a list of source playlists based on the user's choice (manual selection, random selection, and/or their Liked Songs).
2.  **Exclusion Management:** To keep generated playlists fresh, the app maintains two exclusion lists stored as JSON files:
    -   `excluded_songs.json`: A flat list of track IDs that have been recently added to a playlist. This list operates as a sliding window to ensure songs aren't repeated for a set number of runs.
    -   `excluded_playlists.json`: For the "random" mode, this stores a list of *lists*, where each inner list represents a set of playlists used in a single run. This ensures entire playlists aren't repeatedly chosen.
3.  **Song Aggregation:** Fetches all track IDs from the chosen source playlists.
4.  **Filtering:** Removes any track IDs that are present in `excluded_songs.json` from the master list of songs.
5.  **Shuffling & Playlist Update:** Randomly shuffles the remaining available songs, takes the specified number from the top, and uses the Spotify API to either create a new playlist or replace the contents of an existing one with the new mix.
6.  **Updating Exclusions:** Appends the newly added song and playlist IDs to their respective exclusion files for the next run.

### 5. Deployment

The application is configured for production deployment on cloud platforms that support Python web apps (like Render, PythonAnywhere, or Heroku).
-   **`gunicorn`** is used as the production-ready WSGI web server.
-   A **`Procfile`** tells the hosting service the exact command needed to start the Gunicorn server.
