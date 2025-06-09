from collections import namedtuple
from superlinked import framework as sl
from superlinked_app.index import (
    index,
    recipe_schema,
    name_space,
    ingredients_space,
    instructions_space,
#    category_space,
#    cuisine_space,
    rating_space,
    prep_time_space,
    cook_time_space,
)
from superlinked_app.nlq import (
    name_description,
    ingredients_description,
    instructions_description,
    rating_description,
    prep_time_description,
    cook_time_description,
    system_prompt,
    openai_config,
    get_cat_options,
)
# Get categorical options for filters
cat_options = get_cat_options()

# Debug query to verify data ingestion
query_debug = sl.Query(index).find(recipe_schema).limit(3).select_all()

# Main query for multi-modal semantic search
query = (
    sl.Query(
        index,
        weights={
            name_space: sl.Param("name_weight", description=name_description),
            ingredients_space: sl.Param("ingredients_weight", description=ingredients_description),
            instructions_space: sl.Param("instructions_weight", description=instructions_description),
            rating_space: sl.Param("rating_weight", description=rating_description),
            prep_time_space: sl.Param("prep_time_weight", description=prep_time_description),
            cook_time_space: sl.Param("cook_time_weight", description=cook_time_description),
        },
    )
    .find(recipe_schema)
    .similar(
        name_space.text,
        sl.Param("name_query", description=name_description),
        weight=sl.Param("similar_name_weight", default=1.0),
    )
    .similar(
        ingredients_space.text,
        sl.Param("ingredients_query", description=ingredients_description),
        weight=sl.Param("similar_ingredients_weight", default=1.0),
    )
    .similar(
        instructions_space.text,
        sl.Param("instructions_query", description=instructions_description),
        weight=sl.Param("similar_instructions_weight", default=1.0),
    )
)

# Set result limit
query = query.limit(sl.Param("limit", default=5))

# We want all fields to be returned
query = query.select_all()

# .. and all the metadata including knn_params and partial_scores
query = query.include_metadata()

# Numerical filters
query = (
    query.filter(recipe_schema.Rating_Value >= sl.Param("min_rating"))
    .filter(recipe_schema.Rating_Value <= sl.Param("max_rating"))
    .filter(recipe_schema.Preparation_Time >= sl.Param("min_prep_time"))
    .filter(recipe_schema.Preparation_Time <= sl.Param("max_prep_time"))
    .filter(recipe_schema.Cooking_Time >= sl.Param("min_cook_time"))
    .filter(recipe_schema.Cooking_Time <= sl.Param("max_cook_time"))
    .filter(recipe_schema.Calories <= sl.Param("max_calories"))
)

# Categorical filters
CategoryFilter = namedtuple(
    "CategoryFilter", ["operator", "param_name", "category_name", "description"]
)

filters = [
    # Category filters
    CategoryFilter(
        operator=recipe_schema.Category.contains_all,
        param_name="categories_include_all",
        category_name="Category",
        description="Recipes must contain all these categories",
    ),
    CategoryFilter(
        operator=recipe_schema.Category.contains,
        param_name="categories_include_any",
        category_name="Category",
        description="Recipes must contain at least one of these categories",
    ),
    CategoryFilter(
        operator=recipe_schema.Category.not_contains,
        param_name="categories_exclude",
        category_name="Category",
        description="Recipes must not contain any of these categories",
    ),
    # Cuisine filters
    CategoryFilter(
        operator=recipe_schema.Cuisine.contains_all,
        param_name="cuisines_include_all",
        category_name="Cuisine",
        description="Recipes must contain all these cuisines",
    ),
    CategoryFilter(
        operator=recipe_schema.Cuisine.contains,
        param_name="cuisines_include_any",
        category_name="Cuisine",
        description="Recipes must contain at least one of these cuisines",
    ),
    CategoryFilter(
        operator=recipe_schema.Cuisine.not_contains,
        param_name="cuisines_exclude",
        category_name="Cuisine",
        description="Recipes must not contain any of these cuisines",
    ),
]

for filter_item in filters:
    param = sl.Param(
        filter_item.param_name,
        description=filter_item.description,
        options=cat_options.get(filter_item.category_name, []),
    )
    query = query.filter(filter_item.operator(param))



# Natural language query interface
query = query.with_natural_query(
    natural_query=sl.Param("natural_query"),
    client_config=openai_config,
    system_prompt=system_prompt,
)