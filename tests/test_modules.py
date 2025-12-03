import sys
sys.path.append('..')

from modules.ingredient_detector import IngredientDetector
from modules.recipe_finder import RecipeFinder

def test_ingredient_detector():
    detector = IngredientDetector()
    # Test with sample image
    results = detector.detect_from_image('static/sample_images/test_fridge.jpg')
    print(f"Detected: {results}")
    return len(results) > 0

def test_recipe_finder():
    finder = RecipeFinder()
    recipes = finder.find_recipes_by_ingredients(['tomato', 'onion'])
    print(f"Found {len(recipes)} recipes")
    return len(recipes) > 0

if __name__ == "__main__":
    print("Testing Ingredient Detector...")
    test1 = test_ingredient_detector()
    
    print("\nTesting Recipe Finder...")
    test2 = test_recipe_finder()
    
    if test1 and test2:
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️ Some tests failed")