# Sherlock Recipes 🔍🍳

## Project Overview

SherlockRecipes is a project designed to search for recipes within a dataset. Inspired by the famous detective Sherlock Holmes, this project aims to "investigate" and find the perfect recipe for any query you have.

The architecture of SherlockRecipes is based on **Sperlinked** combined with **Qdrant** to provide efficient and accurate recipe search capabilities.


### Why "Sherlock Recipes"?

Just like Sherlock Holmes solves mysteries, this project helps you solve the mystery of "What should I cook today?" by searching through a rich dataset of recipes to find the best match.



Feel free to explore, contribute, and help make cooking an exciting investigation! 🍽️🕵️‍♂️


## Customizing the `superlinked_app` Folder

#### `index.py`
Defines the schema and indexing logic for recipe data. It includes:

- **Embedded fields** for semantic search: `Name`, `Ingredient_Names_Text`, and `Instructions` using a configured text embedding model.
- **Numeric fields** like `Rating_Value`, `Preparation_Time`, `Cooking_Time`, and `Calories` used for filtering and scoring.
- **Categorical fields**: `Category` and `Cuisine` for filtering.
- **Metadata fields** such as `Nutrition`, `Ingredients`, and `URL`, included for display or hard filtering but not embedded.
- Spaces are constructed (`TextSimilaritySpace`, `NumberSpace`) and composed into a single `sl.Index` object.

Min and max values for number spaces (e.g., `max_value=300` for times) should be adjusted to match your dataset.

---

#### `nlq.py`
Provides configuration and utility functions for natural language query (NLQ) interpretation:

- Loads **OpenAI client configuration** using settings from the app.
- Defines **descriptions** for each field to be used in prompt engineering.
- Implements `get_cat_options()` to load valid category/cuisine options from a local JSON file.
- Contains the `system_prompt` for NLQ interpretation, guiding the extraction of semantic and structured parameters from user input.

This file bridges user input with structured query parameters.

---

#### `query.py`
Constructs and configures the main semantic query for retrieving recipes:

- Imports the index and schemas from `index.py` and descriptive texts from `nlq.py`.
- Defines the `query` using `superlinked.Query`, combining:
  - **Semantic similarity** across name, ingredients, and instructions fields.
  - **Numeric filtering** on rating, preparation time, cooking time, and calories.
  - **Categorical filtering** for categories and cuisines using options from `get_cat_options()`.
- Uses `namedtuple` for modular categorical filters.
- Wraps the entire query with `.with_natural_query()` to enable **natural language interface**, powered by the OpenAI API and `system_prompt`.

Also includes `query_debug` for development testing.

---

#### `api.py`
Defines the API interface and execution environment for the Superlinked application:

- **Data sources**:
  - `RestSource` to receive input via REST.
  - `DataLoaderSource` to load dataset chunks from a JSONL file.
- **Vector database**:
  - Uses `QdrantVectorDatabase` to persist and retrieve vector data.
- **Executor**:
  - Binds sources, queries (`recipe`, `recipe-debug`), and vector index (`index`) together.
  - Registers the execution pipeline using `SuperlinkedRegistry`.

This file effectively exposes the functionality of the semantic search system via a REST interface and integrates data persistence.

---

#### `settings.py`
Houses all configurable parameters for the application via environment variables and default values:

- Embedding model: `text_embedder_name` (default: `sentence-transformers/all-mpnet-base-v2`)
- Data input paths: `path_dataset` (recipes), `path_categories` (filter categories)
- Chunking and timeout settings for data loading and Qdrant
- OpenAI API configuration: model and secret key
- Qdrant vector database credentials and endpoint
- Automatically loads variables from a `.env` file via `pydantic`’s `BaseSettings`

This file centralizes application configuration for easy modification and secure API key management.

---

These modules collectively build a customizable, semantic recipe search engine powered by embeddings, structured filtering, and natural language input.



### Superlinked server

Use [`superlinked_app/.env-example`](./superlinked_app/.env-example) as a template, create `superlinked_app/.env` and set `OPENAI_API_KEY` required for Natural Query Interface, `QDRANT_URL` and `QDRANT_API_KEY` required for Qdrant Vector Database.

```shell
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
APP_MODULE_PATH=superlinked_app python -m superlinked.server
```

It will take some time (depending on the network) to download the sentence-transformers model for the very first time.

API docs will be available at [localhost:8080/docs](http://localhost:8080/docs).

The usual command to ingest the dataset, is, from terminal:
```shell
curl -X 'POST' \
  'http://localhost:8080/data-loader/recipe/run' \
  -H 'accept: application/json' \
  -d ''
```

Because the number of recipes the payload was bigger than 32MB, I decided to split as exaplained in the dataset_loading.ipynb

## Dataset

### 📄 Dataset License

The original recipe dataset used in this project is sourced from:

**[Food.com Recipes and Interactions Dataset (Kaggle)](https://zenodo.org/record/15169428)**  
Zenodo Record ID: [15169428](https://zenodo.org/record/15169428)

**License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

**Under the following terms:**
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.

> This project uses a cleaned and truncated subset (first 300–500 rows) of the original dataset for development and demonstration purposes.



## Preparing the Recipe Dataset — `dataset_loading.ipynb`

This markdown describes the purpose and structure of the notebook `dataset_loading.ipynb`, which prepares and processes a raw recipe dataset for semantic indexing and querying within the Superlinked framework.

The notebook handles data cleaning, formatting, enrichment, and optional batch loading into the vector database.

---

### 🧹 Initial CSV Truncation

The notebook begins by loading a large CSV file of recipe records and trimming it to the first 500 rows. This is done to reduce the dataset size for faster processing and testing during development.

---

### 🔄 Conversion to JSONL Format

To prepare the data for use with Superlinked's data loader:

- The truncated CSV is converted to a `.jsonl` (JSON Lines) file containing the first 300 records.
- Each row is serialized as a compact JSON object, one per line, which is the expected format for Superlinked ingestion.

---

### 🧼 Cleaning and Enrichment (`dataset_ok.jsonl`)

Further transformation of the dataset includes:

- Reading the JSONL data and limiting it to a testable row count (via environment variable).
- Removing duplicates and missing recipe names.
- Standardizing and renaming column names to align with the indexing schema (e.g., replacing spaces with underscores like `Rating Value` → `Rating_Value`).
- Safely parsing fields that may contain stringified lists or dictionaries.

Key fields such as `Category`, `Cuisine`, and `Instructions` are flattened into strings where needed.

---

### 🧂 Ingredient Name Extraction

From the `Ingredients` field (which may be a list of dictionaries), the notebook:

- Extracts just the ingredient names.
- Replaces spaces with underscores and joins them into a space-separated string.
- Saves this derived text into a new column called `Ingredient_Names_Text`, used later for semantic search.

---

### 📊 Numeric Normalization and Nutrition Parsing

- Missing numeric fields (e.g., `Calories`, `Protein`, etc.) are filled with `0.0`.
- A helper function extracts numerical values from nested `Nutrition` dictionaries.
- All nutrition fields are flattened into separate columns and standardized for numeric indexing.
- Optionally, the original `Nutrition` field is preserved as a JSON string for display purposes.

---

### 🆔 ID Assignment

Each recipe is assigned a unique ID of the form `rec1`, `rec2`, ..., making it compatible with Superlinked’s `IdField` requirement.

---

### 🗂️ Category & Cuisine Vocabulary Generation

- Iterates over the dataset to extract all unique `Category` and `Cuisine` values.
- Writes them into a `categories.json` file.
- This file is later used by the app to populate filter options for structured queries.

---

### 🚀 Optional: Batch Upload via REST API

- The notebook includes a final step to split the cleaned dataset into batches.
- Each batch is sent to the Superlinked server via HTTP POST to `/data-loader/recipe/run`.
- This enables automated loading of processed data into the vector index.

---

### ✅ Purpose and Use

This notebook is essential for:

- Converting raw CSV data into the format required for semantic search.
- Ensuring field names and structures are schema-compliant.
- Enhancing the data with derived fields like `Ingredient_Names_Text`.
- Creating consistent filters and enabling REST-based ingestion workflows.

It is a foundational step for preparing datasets used by Superlinked-powered applications.



## Querying Sherlock Recipes — `superlinked_qdrant_recipes.ipynb`

This markdown describes the purpose and structure of the notebook `superlinked_qdrant_recipes.ipynb`, which demonstrates how to interactively query a semantic recipe search system built with the `superlinked` framework and powered by a Qdrant vector database.

The notebook is intended as a practical tool for testing and debugging queries within the same virtual environment as the Superlinked server, ensuring version compatibility.

---

### 🧩 Environment Setup

The notebook dynamically locates and adds the `superlinked_app` directory to the Python path. This enables proper importing of application modules regardless of the working directory. It also ensures that the environment uses the same `superlinked` package version as the backend server.

---

### ⚙️ Component Initialization

The core components of the app are imported, including the recipe schema, the semantic index, the main query logic, and the vector database interface. An interactive query engine is then initialized using `InteractiveSource` and `InteractiveExecutor`, which allows running local queries in a REPL-like fashion.

---

### 🔍 Example 1: Natural Language Query

The notebook demonstrates how to run a search query using plain natural language input. A textual prompt such as "quick vegan desserts" is passed to the system, which interprets and converts it into structured query parameters using the logic defined in the application. The results are then displayed in a table, along with extracted scoring metadata.

---

### 🛠️ Example 2: Manual Query Parameters

In this section, the user provides explicit parameters for semantic similarity weights, text queries, numeric filters (e.g., rating, preparation time, calories), and categorical constraints (e.g., included cuisines). This approach gives fine-grained control over the query behavior and result ranking.

---

### 📊 Result Visualization

For both natural and manual queries, the notebook extracts partial similarity scores from each matching recipe and assembles them into a DataFrame. This breakdown allows the user to understand the influence of each individual field (such as ingredients or instructions) on the overall score.

---

### ✅ Purpose and Use

This notebook is designed as a development companion for:

- Testing semantic and structured queries
- Tuning query parameters and weights
- Verifying the behavior of natural language interpretation
- Exploring how individual fields contribute to final search rankings

It is a key tool for developers working on search quality, schema design, and interactive debugging within the `superlinked` recipe search system.
