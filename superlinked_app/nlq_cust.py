import json
from openai import OpenAI  # Use OpenAI's official client for local endpoints

from superlinked_app.config import settings
from superlinked import framework as sl
#from openai import AsyncOpenAI


openai_config = OpenAI(
    base_url=settings.open_ai_base_url,
    api_key=settings.openai_api_key.get_secret_value(),
)



MODEL_NAME=settings.openai_model

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
    "'Category' refers to the type of recipe, such as 'Dessert', 'Main course', 'Appetizer', or 'snack'."
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


# Compose system prompt with descriptions and explicit JSON output instruction
system_prompt = (
    "Extract search parameters from the user's natural language query about recipes.\n"
    "Descriptions:\n"
    f"{name_description}\n"
    f"{ingredients_description}\n"
    f"{instructions_description}\n"
    f"{category_description}\n"
    f"{cuisine_description}\n"
    f"{rating_description}\n"
    f"{prep_time_description}\n"
    f"{cook_time_description}\n"
    f"{nutrition_description}\n"
    "Guidelines:\n"
    "- Identify 'include' and 'exclude' attributes for ingredients, categories, and cuisines.\n"
    "- Extract numeric preferences such as rating, preparation time, and cooking time.\n"
    "- Consider nutrition preferences like 'low calorie', 'high protein', or dietary restrictions.\n"
    "- If no preference is specified for a parameter, use None.\n"
    "- Examples:\n"
    "  1. User query: 'Quick vegan desserts with high rating' -> category: 'dessert', cuisine: None, ingredients include 'vegan', max prep time low, min rating high.\n"
    "  2. User query: 'Gluten-free Italian main courses' -> cuisine: 'Italian', category: 'main course', exclude ingredients containing gluten.\n"
    "  3. User query: 'Easy chicken recipes under 30 minutes' -> ingredients include 'chicken', max prep + cook time 30 mins.\n"
    "\n"
    "Please respond ONLY with a JSON object containing the following keys (use null if not specified):\n"
    "{\n"
    '  "name_query": string or null,\n'
    '  "ingredients_query": string or null,\n'
    '  "instructions_query": string or null,\n'
    '  "min_rating": number or null,\n'
    '  "max_rating": number or null,\n'
    '  "min_prep_time": number or null,\n'
    '  "max_prep_time": number or null,\n'
    '  "min_cook_time": number or null,\n'
    '  "max_cook_time": number or null,\n'
    '  "max_calories": number or null,\n'
    '  "categories_include_all": list of strings or null,\n'
    '  "categories_include_any": list of strings or null,\n'
    '  "categories_exclude": list of strings or null,\n'
    '  "cuisines_include_all": list of strings or null,\n'
    '  "cuisines_include_any": list of strings or null,\n'
    '  "cuisines_exclude": list of strings or null,\n'
    '  "limit": number\n'
    "}\n"
)


def extract_search_params(natural_query: str) -> dict:
    """
    Send the system prompt and user natural query to the OpenAI-compatible client,
    and parse the JSON response into a dictionary of search parameters.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": natural_query},
    ]

    response = openai_config.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.2,
        max_tokens=1024,
    )

    content = response.choices[0].message.content

    try:
        params = json.loads(content)
    except json.JSONDecodeError:
        print("Warning: Failed to parse JSON from model response:")
        print(content)
        params = {}

    return params
