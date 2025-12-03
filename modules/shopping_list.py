class ShoppingList:
    def __init__(self):
        self.items = []
    
    def generate_shopping_list(self, recipe, available_ingredients):
        """Generate shopping list for missing ingredients"""
        if 'missedIngredients' in recipe:
            missing = recipe['missedIngredients']
            if isinstance(missing, list):
                return [ing['name'] if isinstance(ing, dict) else ing 
                       for ing in missing]
        
        # Alternative: parse from detailed recipe
        if 'extendedIngredients' in recipe:
            needed = [ing['name'] for ing in recipe['extendedIngredients']]
            return [item for item in needed 
                   if item.lower() not in [a.lower() for a in available_ingredients]]
        
        return []
    
    def optimize_list(self, recipes, available_ingredients):
        """Optimize shopping list across multiple recipes"""
        all_missing = []
        
        for recipe in recipes:
            missing = self.generate_shopping_list(recipe, available_ingredients)
            all_missing.extend(missing)
        
        # Remove duplicates
        unique_items = list(set(all_missing))
        
        # Categorize items
        categorized = self._categorize_items(unique_items)
        
        return categorized
    
    def _categorize_items(self, items):
        """Categorize items for easier shopping"""
        categories = {
            'Vegetables': [],
            'Fruits': [],
            'Dairy': [],
            'Meat': [],
            'Pantry': [],
            'Other': []
        }
        
        veg_keywords = ['tomato', 'lettuce', 'onion', 'garlic', 'potato', 'carrot']
        fruit_keywords = ['apple', 'banana', 'orange', 'berry']
        dairy_keywords = ['milk', 'cheese', 'butter', 'yogurt']
        meat_keywords = ['chicken', 'beef', 'fish', 'pork']
        pantry_keywords = ['flour', 'sugar', 'oil', 'rice', 'pasta']
        
        for item in items:
            item_lower = item.lower()
            
            if any(keyword in item_lower for keyword in veg_keywords):
                categories['Vegetables'].append(item)
            elif any(keyword in item_lower for keyword in fruit_keywords):
                categories['Fruits'].append(item)
            elif any(keyword in item_lower for keyword in dairy_keywords):
                categories['Dairy'].append(item)
            elif any(keyword in item_lower for keyword in meat_keywords):
                categories['Meat'].append(item)
            elif any(keyword in item_lower for keyword in pantry_keywords):
                categories['Pantry'].append(item)
            else:
                categories['Other'].append(item)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}