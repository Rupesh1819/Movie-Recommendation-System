import pickle
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
TMDB_API_KEY = "8f332911d3bcb63bd010326c4fa8cad4"


def load_movies() -> pd.DataFrame:
    movie_dict_path = BASE_DIR / "movie_dict.pkl"
    movies_path = BASE_DIR / "movies.pkl"

    if movie_dict_path.exists():
        with open(movie_dict_path, "rb") as f:
            movie_dict = pickle.load(f)
        return pd.DataFrame(movie_dict)

    if movies_path.exists():
        with open(movies_path, "rb") as f:
            movies_df = pickle.load(f)
        if isinstance(movies_df, pd.DataFrame):
            return movies_df
        return pd.DataFrame(movies_df)

    raise FileNotFoundError("Neither movie_dict.pkl nor movies.pkl was found.")


def load_similarity():
    similarity_path = BASE_DIR / "similarity.pkl"
    if not similarity_path.exists():
        raise FileNotFoundError("similarity.pkl was not found.")
    with open(similarity_path, "rb") as f:
        return pickle.load(f)


def fetch_poster(movie_id):
    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={TMDB_API_KEY}&language=en-US"
    )
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if not poster_path:
            return None
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    except requests.RequestException:
        return None
    except Exception:
        return None


def recommend(movie, movies_df, similarity, top_k=5):
    selected_rows = movies_df[movies_df["title"] == movie]
    if selected_rows.empty:
        return [], []

    index = selected_rows.index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1],
    )

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1 : top_k + 1]:
        movie_id = int(movies_df.iloc[i[0]].movie_id)
        recommended_movie_names.append(movies_df.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters


def main():
    st.set_page_config(page_title="Movie Recommender")
    st.header("Movie Recommender System")

    try:
        movies_df = load_movies()
        similarity = load_similarity()
    except Exception as e:
        st.error(f"Startup error: {e}")
        return

    movie_list = movies_df["title"].values
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list,
    )

    if st.button("Show Recommendation"):
        names, posters = recommend(selected_movie, movies_df, similarity)
        if not names:
            st.warning("No recommendations found for the selected movie.")
            return

        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if idx < len(names):
                with col:
                    st.text(names[idx])
                    if posters[idx]:
                        st.image(posters[idx], use_container_width=True)
                    else:
                        st.caption("Poster unavailable (network/API timeout).")


if __name__ == "__main__":
    main()
