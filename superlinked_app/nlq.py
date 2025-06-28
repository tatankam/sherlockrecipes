import json

from superlinked import framework as sl

from superlinked_app.config import settings

openai_config = sl.OpenAIClientConfig(
    api_key=settings.openai_api_key.get_secret_value(),
    model=settings.openai_model,
    base_url=settings.open_ai_base_url,
)



def get_cat_options() -> dict[list[str]]:
    """
    Loads categorical options for filters such as Category and Cuisine from a local JSON file.
    The JSON should map category names to lists of valid options.
    """
    with open(settings.path_categories, "r", encoding="utf-8") as f:
        return json.load(f)

# Descriptions for natural language parameter extraction and filtering

name_description = (
    "'Name' is the title of the recipe. "
    "It should capture the main dish or recipe name, e.g. 'Spaghetti Carbonara', 'Vegan Chocolate Cake'."
)

ingredients_description = (
    "'Ingredients' are the list of items required to prepare the recipe. "
    "Mention key ingredients or dietary preferences, e.g. 'chicken', 'gluten-free', 'nuts'."
)

instructions_description = (
    "'Instructions' describe the cooking or preparation steps. "
    "Include any specific techniques or important steps, e.g. 'bake at 180C', 'slow cook', 'stir fry'."
)

category_description = (
    "'Category' refers to the type of recipe, such as 'dessert', 'main course', 'appetizer', or 'snack'."
)

cuisine_description = (
    "'Cuisine' refers to the regional or cultural style of the recipe, e.g. 'Italian', 'Mexican', 'Indian'."
)

rating_description = (
    "Weight of the rating. "
    "Higher value means better rated recipes, "
    "lower value means lower rated. "
    "For example: "
    "positive weight: 'high rating', 'top-rated', 'best'; "
    "negative weight: 'low rating', 'poor', 'not recommended'; "
    "0 if no preference."
)

prep_time_description = (
    "Weight for preparation time. "
    "Lower value means shorter prep time is preferred, "
    "higher value means longer prep time is acceptable. "
    "For example: "
    "'quick', 'fast' imply low prep time; "
    "'elaborate', 'time-consuming' imply higher prep time."
)

cook_time_description = (
    "Weight for cooking time. "
    "Lower value means shorter cooking time is preferred, "
    "higher value means longer cooking time is acceptable."
)

nutrition_description = (
    "Nutrition preferences or restrictions, e.g. 'low calorie', 'high protein', 'vegan', 'gluten-free'. "
    "Use these to filter recipes based on nutrition facts."
)

url_description = (
    "URL of the recipe source or webpage."
)

system_prompt = (
    "Extract search parameters from the user's natural language query about recipes.\n"
    "Guidelines:\n"
    "- Identify 'include' and 'exclude' attributes for ingredients, categories, and cuisines.\n"
    "- Extract numeric preferences such as rating, preparation time, and cooking time.\n"
    "- Consider nutrition preferences like 'low calorie', 'high protein', or dietary restrictions.\n"
    "- If no preference is specified for a parameter, use None.\n"
    "- Examples:\n"
    "  1. User query: 'Quick vegan desserts with high rating' -> category: 'dessert', cuisine: None, ingredients include 'vegan', max prep time low, min rating high.\n"
    "  2. User query: 'Gluten-free Italian main courses' -> cuisine: 'Italian', category: 'main course', exclude ingredients containing gluten.\n"
    "  3. User query: 'Easy chicken recipes under 30 minutes' -> ingredients include 'chicken', max prep + cook time 30 mins.\n"
)