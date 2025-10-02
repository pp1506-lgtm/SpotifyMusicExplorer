import pandas as pd


def load_all_data():
    """
    Loads and merges tracks.csv and spotify_tracks.csv into a single DataFrame.
    Normalizes column names so both datasets align, and ensures a 'year' column exists.
    """
    # Load datasets
    tracks_df = pd.read_csv("data/tracks.csv")
    spotify_df = pd.read_csv("data/spotify_tracks.csv")

    # --- Normalize column names ---
    # tracks.csv
    if "name" in tracks_df.columns:
        tracks_df = tracks_df.rename(columns={"name": "title"})
    if "artists" in tracks_df.columns:
        tracks_df = tracks_df.rename(columns={"artists": "artist"})

    # spotify_tracks.csv
    if "track_name" in spotify_df.columns:
        spotify_df = spotify_df.rename(columns={"track_name": "title"})
    if "artists" in spotify_df.columns:
        spotify_df = spotify_df.rename(columns={"artists": "artist"})

    # Ensure both have a 'year' column (take from tracks.csv if missing in spotify_df)
    if "year" in tracks_df.columns and "year" not in spotify_df.columns:
        spotify_df["year"] = None  # placeholder

    # --- Merge logic ---
    if "id" in tracks_df.columns and "track_id" in spotify_df.columns:
        merged = pd.merge(
            tracks_df,
            spotify_df,
            left_on="id",
            right_on="track_id",
            how="left",
            suffixes=("", "_spotify"),
        )
    else:
        merge_keys = [col for col in ["title", "artist"] if col in tracks_df.columns and col in spotify_df.columns]
        if not merge_keys:
            raise KeyError("No common merge keys found between datasets (expected 'id' or ['title','artist']).")
        merged = pd.merge(
            tracks_df,
            spotify_df,
            on=merge_keys,
            how="left",
            suffixes=("", "_spotify"),
        )

    # Guarantee consistent 'year'
    if "year" not in merged.columns and "year" in tracks_df.columns:
        merged["year"] = tracks_df["year"]

    return merged


def get_top_artists(df: pd.DataFrame, year: int, top_n: int = 10):
    """Returns top N artists by popularity for a given year."""
    if "year" not in df.columns or "artist" not in df.columns:
        return pd.DataFrame()

    year_df = df[df["year"] == year]
    if "popularity" not in year_df.columns:
        return pd.DataFrame()

    top_artists = (
        year_df.groupby("artist")["popularity"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    return top_artists


def get_most_popular_songs(df: pd.DataFrame, year: int, top_n: int = 20):
    """Returns the most popular songs for a given year."""
    if "year" not in df.columns or "title" not in df.columns or "artist" not in df.columns:
        return pd.DataFrame()

    year_df = df[df["year"] == year]
    if "popularity" not in year_df.columns:
        return pd.DataFrame()

    top_songs = (
        year_df.sort_values("popularity", ascending=False)
        .head(top_n)[["title", "artist", "popularity"]]
        .reset_index(drop=True)
    )
    return top_songs


def get_most_popular_song_by_year(df: pd.DataFrame, year: int):
    """Returns the single most popular song in a given year."""
    if "year" not in df.columns or "title" not in df.columns or "artist" not in df.columns:
        return None, None

    year_df = df[df["year"] == year]
    if "popularity" not in year_df.columns or year_df.empty:
        return None, None

    most_popular = year_df.sort_values("popularity", ascending=False).iloc[0]
    return most_popular["title"], most_popular["popularity"]


def compare_artists(df: pd.DataFrame, artist1: str, artist2: str):
    """Compares popularity of two artists over years."""
    if "artist" not in df.columns or "year" not in df.columns:
        return pd.DataFrame()

    comp_df = df[df["artist"].isin([artist1, artist2])]
    if "popularity" not in comp_df.columns:
        return pd.DataFrame()

    return comp_df.groupby(["year", "artist"])["popularity"].mean().reset_index()


def get_songs_by_vibe(df: pd.DataFrame, vibe: str, num_songs: int = 20):
    """Filters songs by vibe using energy, valence, danceability, etc."""
    if df.empty:
        return pd.DataFrame()

    if vibe == "chill":
        filtered = df[(df.get("energy", 1) < 0.4) & (df.get("acousticness", 0) > 0.6)]
    elif vibe == "energetic":
        filtered = df[(df.get("energy", 0) > 0.8) & (df.get("acousticness", 1) < 0.2)]
    elif vibe == "gloomy":
        filtered = df[(df.get("valence", 1) < 0.3) & (df.get("energy", 1) < 0.4)]
    elif vibe == "party":
        filtered = df[(df.get("danceability", 0) > 0.8) & (df.get("energy", 0) > 0.7)]
    elif vibe == "sporty":
        if "tempo" in df.columns:
            filtered = df[(df["tempo"] > 120) & (df.get("energy", 0) > 0.8)]
        else:
            filtered = df[(df.get("energy", 0) > 0.8)]
    else:
        return pd.DataFrame()

    if filtered.empty:
        return pd.DataFrame()

    return filtered.sample(n=min(num_songs, len(filtered)))
