import requests

# Configuration
RADARR_URL = "http://your-radarr-url"
RADARR_API_KEY = "your-radarr-api-key"
TRAKT_CLIENT_ID = "d76bbb7cedd07a34b257e5406535f345964369c50637543398775495e97434b6"
TRAKT_CLIENT_SECRET = "164e836833bfc2418978ce7e229f72407b3808a4d92444054b08f7526d148057"
TRAKT_REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

# Function to get Trakt access token
def get_trakt_access_token():
    print("Visit the following URL to authorize the app:")
    print(f"https://trakt.tv/oauth/authorize?response_type=code&client_id={TRAKT_CLIENT_ID}&redirect_uri={TRAKT_REDIRECT_URI}")
    
    code = input("Enter the code from the URL: ").strip()
    
    url = "https://api.trakt.tv/oauth/token"
    payload = {
        "code": code,
        "client_id": TRAKT_CLIENT_ID,
        "client_secret": TRAKT_CLIENT_SECRET,
        "redirect_uri": TRAKT_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        token_data = response.json()
        print("Access token obtained successfully!")
        print("Save the following tokens for future use:")
        print(f"Access Token: {token_data['access_token']}")
        print(f"Refresh Token: {token_data['refresh_token']}")
        return token_data["access_token"]
    else:
        print(f"Error getting access token: {response.status_code} {response.text}")
        return None

# Headers for Trakt API
def get_trakt_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "trakt-api-version": "2",
        "Content-Type": "application/json",
    }

# Saved tokens (replace with your tokens after the first run)
ACCESS_TOKEN = "your-access-token"

# Replace headers with OAuth-based headers
trakt_headers = get_trakt_headers(ACCESS_TOKEN)

# List of Trakt lists with tags
TRAKT_LISTS = [
    {"url": "https://api.trakt.tv/users/linaspurinis/lists/top-watched-movies-of-the-week-60/items", "tag_name": "topmoviesweek", "expired_tag_name": "delete"},
]

# Function to get or create a Radarr tag
def get_or_create_radarr_tag(tag_name):
    radarr_tags_url = f"{RADARR_URL}/api/v3/tag"
    radarr_headers = {"X-Api-Key": RADARR_API_KEY}

    try:
        response = requests.get(radarr_tags_url, headers=radarr_headers)
        response.raise_for_status()
        tags = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Radarr tags: {e}")
        return None

    for tag in tags:
        if tag['label'].lower() == tag_name.lower():
            return tag['id']

    try:
        create_response = requests.post(radarr_tags_url, json={"label": tag_name}, headers=radarr_headers)
        create_response.raise_for_status()
        new_tag = create_response.json()
        return new_tag['id']
    except requests.exceptions.RequestException as e:
        print(f"Error creating Radarr tag '{tag_name}': {e}")
        return None

# Function to fetch all movies with a specific tag from Radarr
def get_movies_by_tag(tag_id):
    radarr_movies_url = f"{RADARR_URL}/api/v3/movie"
    radarr_headers = {"X-Api-Key": RADARR_API_KEY}

    try:
        response = requests.get(radarr_movies_url, headers=radarr_headers)
        response.raise_for_status()
        all_movies = response.json()
        return [movie for movie in all_movies if tag_id in movie.get('tags', [])]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movies from Radarr: {e}")
        return []

# Process each Trakt list
for trakt_list in TRAKT_LISTS:
    trakt_url = trakt_list["url"]
    tag_name = trakt_list["tag_name"]
    expired_tag_name = trakt_list.get("expired_tag_name")

    tag_id = get_or_create_radarr_tag(tag_name)
    if tag_id is None:
        print(f"Skipping list {trakt_url} due to tag creation error.")
        continue

    expired_tag_id = None
    if expired_tag_name:
        expired_tag_id = get_or_create_radarr_tag(expired_tag_name)

    try:
        trakt_response = requests.get(trakt_url, headers=trakt_headers)
        trakt_response.raise_for_status()
        trakt_items = trakt_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Trakt list {trakt_url}: {e}")
        continue

    tagged_movies = get_movies_by_tag(tag_id)

    trakt_tmdb_ids = {
        item['movie']['ids']['tmdb'] for item in trakt_items if item['type'] == 'movie' and 'tmdb' in item['movie']['ids']
    }

    for movie in tagged_movies:
        tmdb_id = movie['tmdbId']
        radarr_movie_id = movie['id']

        if tmdb_id not in trakt_tmdb_ids:
            print(f"Movie '{movie['title']}' ({movie['year']}) is no longer in the Trakt list.")
            movie['tags'].remove(tag_id)
            if expired_tag_id:
                movie['tags'].append(expired_tag_id)

            radarr_movie_url = f"{RADARR_URL}/api/v3/movie/{radarr_movie_id}"
            try:
                update_response = requests.put(radarr_movie_url, json=movie, headers={"X-Api-Key": RADARR_API_KEY})
                update_response.raise_for_status()
                print(f"Updated tags for '{movie['title']}' ({movie['year']}).")
            except requests.exceptions.RequestException as e:
                print(f"Error updating Radarr tags for '{movie['title']}' ({movie['year']}): {e}")

    for item in trakt_items:
        if item['type'] == 'movie':
            movie = item['movie']
            title = movie['title']
            year = movie['year']
            tmdb_id = movie['ids'].get('tmdb')

            if not tmdb_id:
                print(f"Skipping movie '{title}' ({year}) - TMDb ID not available.")
                continue

            radarr_search_url = f"{RADARR_URL}/api/v3/movie/lookup?term=tmdb:{tmdb_id}"
            try:
                radarr_search_response = requests.get(radarr_search_url, headers={"X-Api-Key": RADARR_API_KEY})
                radarr_search_response.raise_for_status()
                radarr_movies = radarr_search_response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error searching Radarr for '{title}' ({year}): {e}")
                continue

            if radarr_movies:
                radarr_movie = radarr_movies[0]
                radarr_movie_id = radarr_movie['id']

                radarr_movie_url = f"{RADARR_URL}/api/v3/movie/{radarr_movie_id}"
                try:
                    radarr_movie_response = requests.get(radarr_movie_url, headers={"X-Api-Key": RADARR_API_KEY})
                    radarr_movie_response.raise_for_status()
                    radarr_movie_data = radarr_movie_response.json()
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching Radarr movie details for '{title}' ({year}): {e}")
                    continue

                tags = radarr_movie_data.get('tags', [])
                if tag_id not in tags:
                    tags.append(tag_id)
                    radarr_movie_data['tags'] = tags

                    try:
                        update_response = requests.put(radarr_movie_url, json=radarr_movie_data, headers={"X-Api-Key": RADARR_API_KEY})
                        update_response.raise_for_status()
                        print(f"Updated tags for '{title}' ({year}) in list {trakt_url}.")
                    except requests.exceptions.RequestException as e:
                        print(f"Error updating Radarr tags for '{title}' ({year}): {e}")
            else:
                print(f"Movie '{title}' ({year}) not found in Radarr.")
        else:
            print(f"Skipping non-movie item of type '{item['type']}' in list {trakt_url}.")
