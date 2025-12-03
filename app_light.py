# app_light.py - Streamlit app without heavy ML
import streamlit as st
import requests
import os
from PIL import Image
import json

# Simple version without YOLO
st.set_page_config(page_title="Cook Assistant Lite", page_icon="🍳")

st.title("🥘 Cook Assistant Lite")
st.write("Upload an image or enter ingredients manually")

# Manual input only
ingredients = st.text_input(
    "Enter ingredients (comma-separated):",
    "tomato, onion, garlic, chicken"
)

if st.button("Find Recipes"):
    # Use Spoonacular API directly
    api_key = st.secrets.get("SPOONACULAR_API_KEY", "")
    
    if api_key:
        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            'ingredients': ingredients,
            'number': 5,
            'apiKey': api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            recipes = response.json()
            for recipe in recipes:
                st.write(f"### {recipe['title']}")
                if 'image' in recipe:
                    st.image(recipe['image'], width=200)
        else:
            st.error("Failed to fetch recipes")
    else:
        st.warning("Please add SPOONACULAR_API_KEY to Streamlit secrets")