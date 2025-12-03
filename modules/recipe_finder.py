import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

class RecipeFinder:
    def __init__(self):
        self.api_key = os.getenv('SPOONACULAR_API_KEY')
        self.base_url = "https://api.spoonacular.com"
        
    def find_recipes_by_ingredients(self, ingredients, number=5):
        """Find recipes based on ingredients"""
        url = f"{self.base_url}/recipes/findByIngredients"
        
        params = {
            'ingredients': ','.join(ingredients),
            'number': number,
            'apiKey': self.api_key,
            'ranking': 2,  # Maximize used ingredients
            'ignorePantry': True
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code}")
                return self._get_fallback_recipes(ingredients)
        except:
            return self._get_fallback_recipes(ingredients)
    
    def get_recipe_details(self, recipe_id):
        """Get detailed recipe information"""
        url = f"{self.base_url}/recipes/{recipe_id}/information"
        
        params = {
            'apiKey': self.api_key,
            'includeNutrition': False
        }
        
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None
    
    def _get_fallback_recipes(self, ingredients):
        """Local fallback recipes if API fails"""
        # Simple local database
        recipes_db = {
            'apple': [
                {
                    'id': 1,
                    'title': 'Apple Salad',
                    'usedIngredientCount': 1,
                    'missedIngredientCount': 3,
                    'missedIngredients': ['lettuce', 'walnuts', 'dressing']
                }
            ],
            'tomato': [
                {
                    'id': 2,
                    'title': 'Tomato Pasta',
                    'usedIngredientCount': 1,
                    'missedIngredientCount': 2,
                    'missedIngredients': ['pasta', 'basil']
                }
            ]
        }
        
        # Combine recipes for all ingredients
        all_recipes = []
        for ingredient in ingredients:
            if ingredient in recipes_db:
                all_recipes.extend(recipes_db[ingredient])
        
        return all_recipes[:5]
    
    def get_recipe_instructions(self, recipe_id):
        """Get step-by-step instructions"""
        url = f"{self.base_url}/recipes/{recipe_id}/analyzedInstructions"
        
        params = {
            'apiKey': self.api_key
        }
        
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else []