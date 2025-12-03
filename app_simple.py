import streamlit as st
import requests

st.title("Simple Recipe Finder")
ingredients = st.text_input("Ingredients", "chicken, rice, vegetables")
api_key = st.secrets["SPOONACULAR_API_KEY"]

if st.button("Find Recipes"):
    url = f"https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients,
        "apiKey": api_key,
        "number": 5
    }
    response = requests.get(url, params=params)
    if response.ok:
        for recipe in response.json():
            st.write(recipe["title"])