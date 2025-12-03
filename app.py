import streamlit as st
import os
from PIL import Image
import pandas as pd
from modules.ingredient_detector import IngredientDetector
from modules.recipe_finder import RecipeFinder
from modules.shopping_list import ShoppingList
import tempfile
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="AI Cook Assistant",
    page_icon="🍳",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        color: #4ECDC4;
        font-size: 1.5rem;
        margin-top: 1.5rem;
    }
    .recipe-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    .stButton>button {
        background-color: #FF6B6B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize modules
@st.cache_resource
def load_models():
    return IngredientDetector()

detector = load_models()
recipe_finder = RecipeFinder()
shopping_list = ShoppingList()

# App header
st.markdown('<h1 class="main-header">🥘 AI Personal Cook Assistant</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Manual ingredient input
    st.subheader("Add Ingredients Manually")
    manual_ingredients = st.text_input(
        "Enter ingredients (comma-separated)",
        placeholder="e.g., tomato, onion, chicken"
    )
    
    if manual_ingredients:
        manual_list = [i.strip() for i in manual_ingredients.split(',')]
        if 'ingredients' in st.session_state:
            st.session_state.ingredients.extend(manual_list)
        else:
            st.session_state.ingredients = manual_list
    
    # Dietary preferences
    st.subheader("Dietary Preferences")
    diet = st.selectbox(
        "Select diet",
        ["Any", "Vegetarian", "Vegan", "Gluten Free", "Dairy Free"]
    )
    
    # Max prep time
    max_time = st.slider("Max Preparation Time (minutes)", 10, 120, 30)

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📸 Upload Image", "🍽️ Recipe Suggestions", "🛒 Shopping List"])

with tab1:
    st.markdown('<h2 class="sub-header">Upload Your Fridge/Ingredients Photo</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear picture of your ingredients"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            # Display image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Detect ingredients button
            if st.button("🔍 Detect Ingredients", type="primary"):
                with st.spinner("Detecting ingredients..."):
                    # Detect ingredients
                    detections = detector.detect_from_image(tmp_path)
                    
                    if detections:
                        # Store in session state
                        detected_items = list(set([d['ingredient'] for d in detections]))
                        if 'ingredients' in st.session_state:
                            st.session_state.ingredients.extend(detected_items)
                            # Remove duplicates
                            st.session_state.ingredients = list(set(st.session_state.ingredients))
                        else:
                            st.session_state.ingredients = detected_items
                        
                        st.success(f"Detected {len(detected_items)} ingredients!")
                        
                        # Show detection results
                        st.subheader("Detection Results")
                        for item in detected_items:
                            st.write(f"✅ {item}")
                        
                        # Show image with bounding boxes
                        img_with_boxes = detector.draw_detections(tmp_path, detections)
                        st.image(img_with_boxes, caption="Detected Ingredients", use_column_width=True)
                    else:
                        st.warning("No ingredients detected. Try adding manually.")
            
            # Clean up
            os.unlink(tmp_path)
    
    with col2:
        st.subheader("Current Ingredients")
        if 'ingredients' in st.session_state and st.session_state.ingredients:
            ingredients_df = pd.DataFrame({
                'Ingredient': st.session_state.ingredients,
                'Action': ['Remove'] * len(st.session_state.ingredients)
            })
            
            # Display as editable table
            edited_df = st.data_editor(
                ingredients_df,
                column_config={
                    "Action": st.column_config.SelectboxColumn(
                        "Action",
                        options=["Keep", "Remove"],
                        required=True,
                    )
                },
                use_container_width=True
            )
            
            # Update ingredients based on user selection
            if st.button("Update Ingredients"):
                keep_items = edited_df[edited_df['Action'] == 'Keep']['Ingredient'].tolist()
                st.session_state.ingredients = keep_items
                st.rerun()
            
            # Clear all button
            if st.button("Clear All Ingredients"):
                st.session_state.ingredients = []
                st.rerun()
        else:
            st.info("No ingredients added yet. Upload an image or add manually.")

with tab2:
    st.markdown('<h2 class="sub-header">Recipe Suggestions</h2>', unsafe_allow_html=True)
    
    if 'ingredients' in st.session_state and st.session_state.ingredients:
        st.write(f"**Available Ingredients:** {', '.join(st.session_state.ingredients)}")
        
        if st.button("Find Recipes", type="primary"):
            with st.spinner("Finding recipes..."):
                # Find recipes
                recipes = recipe_finder.find_recipes_by_ingredients(
                    st.session_state.ingredients,
                    number=5
                )
                
                if recipes:
                    st.session_state.recipes = recipes
                    
                    # Display recipes
                    for i, recipe in enumerate(recipes):
                        with st.expander(f"🍲 {recipe.get('title', 'Recipe')}", expanded=i==0):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                # Recipe info
                                st.write(f"**Used Ingredients:** {recipe.get('usedIngredientCount', 'N/A')}")
                                st.write(f"**Missing Ingredients:** {recipe.get('missedIngredientCount', 'N/A')}")
                                
                                # Get detailed info
                                if 'id' in recipe:
                                    details = recipe_finder.get_recipe_details(recipe['id'])
                                    if details:
                                        if 'summary' in details:
                                            st.markdown(details['summary'].split('.')[0] + "...")
                                        if 'readyInMinutes' in details:
                                            st.write(f"⏱️ **Ready in:** {details['readyInMinutes']} minutes")
                                        if 'servings' in details:
                                            st.write(f"👥 **Servings:** {details['servings']}")
                            
                            with col2:
                                # Recipe image
                                if 'image' in recipe:
                                    st.image(recipe['image'], width=150)
                                
                                # Select button
                                if st.button(f"Select Recipe {i+1}", key=f"select_{i}"):
                                    st.session_state.selected_recipe = recipe
                                    st.success("Recipe selected! Check Shopping List tab.")
                else:
                    st.warning("No recipes found. Try different ingredients.")
    else:
        st.info("Add ingredients first to find recipes.")

with tab3:
    st.markdown('<h2 class="sub-header">Shopping List</h2>', unsafe_allow_html=True)
    
    if 'selected_recipe' in st.session_state and 'ingredients' in st.session_state:
        recipe = st.session_state.selected_recipe
        available = st.session_state.ingredients
        
        # Generate shopping list
        missing_items = shopping_list.generate_shopping_list(recipe, available)
        
        if missing_items:
            st.write("### 🛍️ Items to Buy")
            
            # Categorize items
            categorized = shopping_list._categorize_items(missing_items)
            
            for category, items in categorized.items():
                if items:
                    with st.expander(f"{category} ({len(items)} items)"):
                        for item in items:
                            st.write(f"☐ {item}")
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                # Text export
                list_text = "\n".join(missing_items)
                st.download_button(
                    label="📥 Download as Text",
                    data=list_text,
                    file_name="shopping_list.txt",
                    mime="text/plain"
                )
            with col2:
                # Markdown export
                st.download_button(
                    label="📥 Download as Markdown",
                    data="# Shopping List\n\n" + "\n".join([f"- [ ] {item}" for item in missing_items]),
                    file_name="shopping_list.md",
                    mime="text/markdown"
                )
        else:
            st.success("🎉 You have all ingredients needed!")
    else:
        st.info("Select a recipe first to generate shopping list.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>🍳 AI Cook Assistant | Made with Streamlit & Spoonacular API</p>
    <p>Note: This is a demo. Ingredient detection accuracy may vary.</p>
</div>
""", unsafe_allow_html=True)