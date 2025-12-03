import streamlit as st
import os
from PIL import Image
import pandas as pd
import sys
import tempfile
import matplotlib.pyplot as plt

# ============================================
# ADD ERROR HANDLING AND IMPORT FIXES FIRST
# ============================================
import warnings

# Try to import torch with error handling
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("Torch not available, using fallback detection")

# ============================================
# DEFINE INGREDIENT DETECTOR CLASS HERE
# ============================================
class IngredientDetector:
    def __init__(self):
        self.model = None
        self.ingredient_classes = self._get_food_classes()
        
        # Try to load YOLO if torch is available
        if TORCH_AVAILABLE:
            try:
                # Use ultralytics YOLO (more reliable)
                from ultralytics import YOLO
                # Use the smallest model for faster loading
                self.model = YOLO('yolov8n.pt')
                print("✅ YOLO model loaded successfully")
            except Exception as e:
                print(f"⚠️ Failed to load YOLO model: {e}")
                self.model = None
        else:
            print("ℹ️ Torch not available, using fallback methods only")
    
    def _get_food_classes(self):
        """Map COCO classes to food ingredients"""
        food_mapping = {
            'apple': 'apple',
            'banana': 'banana',
            'orange': 'orange',
            'broccoli': 'broccoli',
            'carrot': 'carrot',
            'hot dog': 'sausage',
            'pizza': 'pizza',
            'donut': 'donut',
            'cake': 'cake',
            'sandwich': 'sandwich',
            'bowl': 'bowl',
            'bottle': 'bottle',
            'wine glass': 'wine',
            'cup': 'cup',
        }
        return food_mapping
    
    def detect_from_image(self, image_path):
        """Detect ingredients from image"""
        detections = []
        
        # Try YOLO detection first
        if self.model is not None:
            try:
                results = self.model(image_path, verbose=False)
                
                for result in results:
                    if result.boxes is not None:
                        for box in result.boxes:
                            cls = int(box.cls[0])
                            conf = float(box.conf[0])
                            class_name = result.names[cls]
                            
                            # Filter to only food-related items
                            if class_name in self.ingredient_classes:
                                ingredient = self.ingredient_classes[class_name]
                                detections.append({
                                    'ingredient': ingredient,
                                    'confidence': conf,
                                    'bbox': box.xyxy[0].tolist()
                                })
                
                if detections:
                    print(f"✅ YOLO detected {len(detections)} items")
                    return detections
                    
            except Exception as e:
                print(f"❌ YOLO detection error: {e}")
        
        # Fallback: simple color-based detection
        return self._detect_fallback(image_path)
    
    def _detect_fallback(self, image_path):
        """Simple fallback when YOLO fails"""
        try:
            import cv2
            import numpy as np
            
            image = cv2.imread(image_path)
            if image is None:
                return []
                
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            detections = []
            
            # Check for various colors
            color_ranges = [
                ('tomato', [0, 100, 100], [10, 255, 255]),  # Red
                ('vegetable', [35, 100, 100], [85, 255, 255]),  # Green
                ('lemon', [20, 100, 100], [30, 255, 255]),  # Yellow
                ('orange', [10, 100, 100], [20, 255, 255]),  # Orange
            ]
            
            for name, lower, upper in color_ranges:
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                if cv2.countNonZero(mask) > 100:
                    detections.append({
                        'ingredient': name,
                        'confidence': 0.5,
                        'bbox': [0, 0, 100, 100]
                    })
            
            return detections
            
        except Exception as e:
            print(f"❌ Fallback detection error: {e}")
            return []
    
    def draw_detections(self, image_path, detections):
        """Draw bounding boxes on image"""
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is None:
                return None
                
            for det in detections:
                if 'bbox' in det and len(det['bbox']) >= 4:
                    x1, y1, x2, y2 = map(int, det['bbox'][:4])
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{det['ingredient']} ({det['confidence']:.2f})"
                    cv2.putText(img, label, (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            return img
        except:
            return None

# ============================================
# NOW IMPORT THE OTHER MODULES
# ============================================
try:
    from modules.recipe_finder import RecipeFinder
    from modules.shopping_list import ShoppingList
except ImportError:
    # Define fallback classes if modules not found
    print("⚠️ Could not import modules, using fallback classes")
    
    class RecipeFinder:
        def __init__(self):
            self.api_key = os.getenv('SPOONACULAR_API_KEY', st.secrets.get("SPOONACULAR_API_KEY", ""))
        
        def find_recipes_by_ingredients(self, ingredients, number=5):
            import requests
            url = "https://api.spoonacular.com/recipes/findByIngredients"
            params = {
                'ingredients': ','.join(ingredients),
                'number': number,
                'apiKey': self.api_key
            }
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else []
    
    class ShoppingList:
        def generate_shopping_list(self, recipe, available_ingredients):
            return recipe.get('missedIngredients', [])
        
        def _categorize_items(self, items):
            return {'All Items': items}

# ============================================
# PAGE CONFIGURATION
# ============================================
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

# ============================================
# INITIALIZE MODULES WITH ERROR HANDLING
# ============================================
@st.cache_resource
def load_models():
    try:
        detector = IngredientDetector()
        return detector
    except Exception as e:
        st.warning(f"⚠️ Model loading had issues: {e}")
        # Return a basic detector
        class BasicDetector:
            def detect_from_image(self, image_path):
                return []
            def draw_detections(self, image_path, detections):
                return None
        return BasicDetector()

detector = load_models()
recipe_finder = RecipeFinder()
shopping_list = ShoppingList()

# ============================================
# APP HEADER
# ============================================
st.markdown('<h1 class="main-header">🥘 AI Personal Cook Assistant</h1>', unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Check if API key is available
    api_key = os.getenv('SPOONACULAR_API_KEY', st.secrets.get("SPOONACULAR_API_KEY", ""))
    if not api_key:
        st.error("⚠️ SPOONACULAR_API_KEY not found!")
        st.info("Add it to Streamlit secrets: Settings → Secrets")
    
    # Manual ingredient input
    st.subheader("Add Ingredients Manually")
    manual_ingredients = st.text_input(
        "Enter ingredients (comma-separated)",
        placeholder="e.g., tomato, onion, chicken"
    )
    
    if manual_ingredients and st.button("Add Ingredients"):
        manual_list = [i.strip() for i in manual_ingredients.split(',')]
        if 'ingredients' in st.session_state:
            st.session_state.ingredients.extend(manual_list)
            # Remove duplicates
            st.session_state.ingredients = list(set(st.session_state.ingredients))
        else:
            st.session_state.ingredients = manual_list
        st.success(f"Added {len(manual_list)} ingredients!")
        st.rerun()
    
    # Dietary preferences
    st.subheader("Dietary Preferences")
    diet = st.selectbox(
        "Select diet",
        ["Any", "Vegetarian", "Vegan", "Gluten Free", "Dairy Free"]
    )
    
    # Max prep time
    max_time = st.slider("Max Preparation Time (minutes)", 10, 120, 30)
    
    # Clear all button in sidebar too
    if st.button("Clear All Ingredients"):
        if 'ingredients' in st.session_state:
            st.session_state.ingredients = []
            st.success("All ingredients cleared!")
            st.rerun()

# ============================================
# MAIN CONTENT TABS
# ============================================
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
                        
                        # Show image with bounding boxes if available
                        img_with_boxes = detector.draw_detections(tmp_path, detections)
                        if img_with_boxes is not None:
                            st.image(img_with_boxes, caption="Detected Ingredients", use_column_width=True)
                    else:
                        st.warning("No ingredients detected. Try adding manually.")
            
            # Clean up
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    with col2:
        st.subheader("Current Ingredients")
        if 'ingredients' in st.session_state and st.session_state.ingredients:
            st.write(f"**You have {len(st.session_state.ingredients)} ingredients:**")
            
            # Display as list with remove buttons
            for idx, ingredient in enumerate(st.session_state.ingredients):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"• {ingredient}")
                with col_b:
                    if st.button("🗑️", key=f"remove_{idx}"):
                        st.session_state.ingredients.pop(idx)
                        st.rerun()
            
            # Clear all button
            if st.button("Clear All Ingredients", key="clear_all_tab1"):
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
                
                if recipes and len(recipes) > 0:
                    st.session_state.recipes = recipes
                    
                    # Display recipes
                    for i, recipe in enumerate(recipes):
                        with st.expander(f"🍲 {recipe.get('title', 'Recipe')}", expanded=i==0):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                # Recipe info
                                st.write(f"**Used Ingredients:** {recipe.get('usedIngredientCount', 'N/A')}")
                                st.write(f"**Missing Ingredients:** {recipe.get('missedIngredientCount', 'N/A')}")
                                
                                # Show missed ingredients
                                if 'missedIngredients' in recipe:
                                    missed = [ing['name'] if isinstance(ing, dict) else ing 
                                             for ing in recipe['missedIngredients']]
                                    if missed:
                                        st.write("**You need:**")
                                        for item in missed[:3]:
                                            st.write(f"- {item}")
                            
                            with col2:
                                # Recipe image
                                if 'image' in recipe:
                                    st.image(recipe['image'], width=150)
                                
                                # Select button
                                if st.button(f"Select Recipe {i+1}", key=f"select_{i}"):
                                    st.session_state.selected_recipe = recipe
                                    st.success("✅ Recipe selected! Check Shopping List tab.")
                                    st.rerun()
                else:
                    st.warning("No recipes found. Try different ingredients.")
    else:
        st.info("Add ingredients first to find recipes.")

with tab3:
    st.markdown('<h2 class="sub-header">Shopping List</h2>', unsafe_allow_html=True)
    
    if 'selected_recipe' in st.session_state and 'ingredients' in st.session_state:
        recipe = st.session_state.selected_recipe
        available = st.session_state.ingredients
        
        st.write(f"**Selected Recipe:** {recipe.get('title', 'Unknown Recipe')}")
        
        # Generate shopping list
        missing_items = shopping_list.generate_shopping_list(recipe, available)
        
        if isinstance(missing_items, list) and missing_items:
            st.write("### 🛍️ Items to Buy")
            
            # Categorize items
            try:
                categorized = shopping_list._categorize_items(missing_items)
                for category, items in categorized.items():
                    if items:
                        with st.expander(f"{category} ({len(items)} items)"):
                            for item in items:
                                st.write(f"☐ {item}")
            except:
                # Simple list if categorization fails
                for item in missing_items:
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

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>🍳 AI Cook Assistant | Made with Streamlit & Spoonacular API</p>
    <p>Note: This is a demo. Ingredient detection accuracy may vary.</p>
</div>
""", unsafe_allow_html=True)