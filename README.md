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
