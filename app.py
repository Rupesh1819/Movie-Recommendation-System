import streamlit as st   
import pickle   
import pandas as pd 
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movies_list:
        recommended_movies.append(movies.iloc[i[0]].title)

    st.write('Top 5 recommended movies:')
    for rec_movie in recommended_movies:
        st.write(rec_movie)
similarity = pickle.load(open('similarity.pkl','rb'))



movies_dict = pickle.load(open('movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

st.title('Movie Recommender System')
selected_movie_name = st.selectbox(
    'Select a movie you like:',
    movies['title'].values
)
if st.button('Show Recommendations'):
    recommend(selected_movie_name)
    st.write(selected_movie_name)

