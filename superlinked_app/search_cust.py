import json
from superlinked_app.nlq_cust import openai_config, MODEL_NAME, system_prompt, get_cat_options
from superlinked_app.index import (
    index,
    recipe_schema,
    name_space,
    ingredients_space,
    instructions_space,
    rating_space,
    prep_time_space,
    cook_time_space,
)
from superlinked import framework as sl

def extract_search_params(natural_query: str) -> dict:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": natural_query},
    ]
    response = openai_config.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.2,
        max_tokens=512,
    )
    content = response.choices[0].message.content
    try:
        params = json.loads(content)
    except json.JSONDecodeError:
        print("Warning: Failed to parse JSON from model response:")
        print(content)
        params = {}
    return params

def build_query_from_params(params: dict) -> sl.Query:
    cat_options = get_cat_options()

    def normalize_categories(extracted_list, valid_options):
        if not extracted_list:
            return []
        valid_lower_map = {opt.lower(): opt for opt in valid_options}
        return [valid_lower_map[item.lower()] for item in extracted_list if item.lower() in valid_lower_map]

    # Initialize the query with weights and schema
    query = sl.Query(
        index,
        weights={
            name_space: params.get("name_weight", 1.0),
            ingredients_space: params.get("ingredients_weight", 1.0),
            instructions_space: params.get("instructions_weight", 1.0),
            rating_space: params.get("rating_weight", 1.0),
            prep_time_space: params.get("prep_time_weight", 1.0),
            cook_time_space: params.get("cook_time_weight", 1.0),
        },
    ).find(recipe_schema)

    # Add similarity search conditions if present
    if params.get("name_query"):
        query = query.similar(
            name_space.text,
            params["name_query"],
            weight=params.get("similar_name_weight", 1.0),
        )
    if params.get("ingredients_query"):
        query = query.similar(
            ingredients_space.text,
            params["ingredients_query"],
            weight=params.get("similar_ingredients_weight", 1.0),
        )
    if params.get("instructions_query"):
        query = query.similar(
            instructions_space.text,
            params["instructions_query"],
            weight=params.get("similar_instructions_weight", 1.0),
        )

    # Numerical filters — apply only if values are not None
    if params.get("min_rating") is not None:
        query = query.filter(recipe_schema.Rating_Value >= params["min_rating"])
    if params.get("max_rating") is not None:
        query = query.filter(recipe_schema.Rating_Value <= params["max_rating"])
    if params.get("min_prep_time") is not None:
        query = query.filter(recipe_schema.Preparation_Time >= params["min_prep_time"])
    if params.get("max_prep_time") is not None:
        query = query.filter(recipe_schema.Preparation_Time <= params["max_prep_time"])
    if params.get("min_cook_time") is not None:
        query = query.filter(recipe_schema.Cooking_Time >= params["min_cook_time"])
    if params.get("max_cook_time") is not None:
        query = query.filter(recipe_schema.Cooking_Time <= params["max_cook_time"])
    if params.get("max_calories") is not None:
        query = query.filter(recipe_schema.Calories <= params["max_calories"])

    # Helper to apply categorical filters safely
    def apply_cat_filter(operator, param_name, category_name):
        values = params.get(param_name)
        if values:
            valid_options = cat_options.get(category_name, [])
            normalized_values = normalize_categories(values, valid_options)
            if normalized_values:
                nonlocal query
                query = query.filter(operator(normalized_values))

    # Apply category and cuisine filters with normalization
    apply_cat_filter(recipe_schema.Category.contains_all, "categories_include_all", "Category")
    apply_cat_filter(recipe_schema.Category.contains, "categories_include_any", "Category")
    apply_cat_filter(recipe_schema.Category.not_contains, "categories_exclude", "Category")

    apply_cat_filter(recipe_schema.Cuisine.contains_all, "cuisines_include_all", "Cuisine")
    apply_cat_filter(recipe_schema.Cuisine.contains, "cuisines_include_any", "Cuisine")
    apply_cat_filter(recipe_schema.Cuisine.not_contains, "cuisines_exclude", "Cuisine")

    # Set result limit with default fallback
    limit = params.get("limit", 5)
    query = query.limit(limit)

    # Select all fields and include metadata
    query = query.select_all().include_metadata()

    return query

def run_search(natural_query: str, app, limit: int = 5):
    params = extract_search_params(natural_query)
    print("Extracted parameters:", params)
    if not params:
        params = {}
    params["limit"] = limit
    query = build_query_from_params(params)
    results = app.query(query)
    return results
