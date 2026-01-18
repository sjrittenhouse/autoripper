import os
import sys
import subprocess
import shutil
# --- 1. AUTO-INSTALL MISSING LIBRARIES ---
required_libraries = ['requests', 'tmdbv3api']

for lib in required_libraries:
    try:
        __import__(lib)
    except ImportError:
        print(f"Installing missing library: {lib}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

from tmdbv3api import TMDb, Movie
import requests

# --- CONFIGURATION ---
# Get your free API key at https://www.themoviedb.org/settings/api
TMDB_API_KEY = "6e0c6e8d"
OUTPUT_DIR = "./CompletedMovies" # Where your Handbrake files are

tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
movie_api = Movie()

def process_metadata(file_path):
    filename = os.path.basename(file_path)
    # Strip extension to get the search term
    search_term = os.path.splitext(filename)[0]
    
    print(f"Searching TMDb for: {search_term}...")
    search = movie_api.search(search_term)
    
    if not search:
        print(f"No results found for {search_term}")
        return

    # Take the first result
    best_match = search[0]
    title = best_match.title.replace(":", "-") # Windows doesn't like colons
    year = best_match.release_date.split("-")[0]
    
    # 1. Create Jellyfin Folder: "Movie Name (Year)"
    folder_name = f"{title} ({year})"
    new_dir = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(new_dir, exist_ok=True)

    # 2. Move/Rename Video File
    extension = os.path.splitext(file_path)[1]
    new_video_path = os.path.join(new_dir, f"{folder_name}{extension}")
    shutil.move(file_path, new_video_path)
    print(f"[✓] Moved to: {new_video_path}")

    # 3. Download Poster
    if best_match.poster_path:
        poster_url = f"https://image.tmdb.org/t/p/original{best_match.poster_path}"
        poster_data = requests.get(poster_url).content
        with open(os.path.join(new_dir, "poster.jpg"), "wb") as f:
            f.write(poster_data)
        print("[✓] Poster downloaded.")

def run_organizer():
    # Only look for common video formats
    extensions = ('.mp4', '.mkv', '.avi')
    files = [f for f in os.listdir(".") if f.lower().endswith(extensions)]
    
    for f in files:
        process_metadata(os.path.abspath(f))

if __name__ == "__main__":
    run_organizer()