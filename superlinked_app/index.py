from superlinked import framework as sl
from superlinked_app.config import settings

@sl.schema
class Recipe:
    # Obligatory field
    id: sl.IdField

    # Embedded fields for semantic search
    Name: sl.String
    Ingredient_Names_Text: sl.String  # concatenated ingredient names for embedding
    Instructions: sl.String


    # Numeric fields for scoring/filtering
    Rating_Value: sl.Float
    Preparation_Time: sl.Float
    Cooking_Time: sl.Float

    # Nutrition fields (extracted as floats for filtering/sorting)
    Category: sl.StringList # list of categories for filtering
    Cuisine: sl.StringList # list of cuisines for filtering 
    Calories: sl.Float
    Carbohydrates: sl.Float
    Cholesterol: sl.Float
    Fiber: sl.Float
    Protein: sl.Float
    Saturated_Fat: sl.Float
    Sodium: sl.Float
    Sugar: sl.Float
    Fat: sl.Float
    Unsaturated_Fat: sl.Float

    # Optional: Store original Nutrition string for display
    Nutrition: sl.String

    # Metadata fields
    Ingredients: sl.String  # original ingredients as string metadata
    URL: sl.String

recipe_schema = Recipe()

# Semantic space for recipe name
name_space = sl.TextSimilaritySpace(
    text=recipe_schema.Name,
    model=settings.text_embedder_name,
)

# Semantic space for concatenated ingredient names
ingredients_space = sl.TextSimilaritySpace(
    text=recipe_schema.Ingredient_Names_Text,
    model=settings.text_embedder_name,
)

# Semantic space for instructions
instructions_space = sl.TextSimilaritySpace(
    text=recipe_schema.Instructions,
    model=settings.text_embedder_name,
)

# Semantic space for category and cuisine
# category_space = sl.TextSimilaritySpace(
#     text=recipe_schema.Category,
#     model=settings.text_embedder_name,
# )
# cuisine_space = sl.TextSimilaritySpace(
#     text=recipe_schema.Cuisine,
#     model=settings.text_embedder_name,
# )

# Number spaces for ratings and times
rating_space = sl.NumberSpace(
    recipe_schema.Rating_Value,
    min_value=0,
    max_value=5,
    mode=sl.Mode.MAXIMUM,
)

prep_time_space = sl.NumberSpace(
    recipe_schema.Preparation_Time,
    min_value=0,
    max_value=300,  # adjust as needed
    mode=sl.Mode.MINIMUM,
)

cook_time_space = sl.NumberSpace(
    recipe_schema.Cooking_Time,
    min_value=0,
    max_value=300,  # adjust as needed
    mode=sl.Mode.MINIMUM,
)

# Nutrition number spaces (optional, add more if needed)
calories_space = sl.NumberSpace(
    recipe_schema.Calories,
    min_value=0,
    max_value=2000,  # adjust as needed
    mode=sl.Mode.MINIMUM,
)

protein_space = sl.NumberSpace(
    recipe_schema.Protein,
    min_value=0,
    max_value=100,  # adjust as needed
    mode=sl.Mode.MAXIMUM,
)

# Compose the index
index = sl.Index(
    spaces=[
        name_space,
        ingredients_space,
        instructions_space,
    #    category_space,
    #    cuisine_space,
        rating_space,
        prep_time_space,
        cook_time_space,
        calories_space,
        protein_space,
    ],
    fields=[
        recipe_schema.Rating_Value,
        recipe_schema.Preparation_Time,
        recipe_schema.Cooking_Time,
        recipe_schema.Category,
        recipe_schema.Cuisine,
        recipe_schema.Calories,
        recipe_schema.Carbohydrates,
        recipe_schema.Cholesterol,
        recipe_schema.Fiber,
        recipe_schema.Protein,
        recipe_schema.Saturated_Fat,
        recipe_schema.Sodium,
        recipe_schema.Sugar,
        recipe_schema.Fat,
        recipe_schema.Unsaturated_Fat,
        recipe_schema.Nutrition,  # for display
        recipe_schema.Ingredients,  # original ingredients as string metadata
        recipe_schema.URL,
    ],
)
