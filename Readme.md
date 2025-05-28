# SherlockRecipes 🔍🍳

## Project Overview

SherlockRecipes is a project designed to search for recipes within a dataset. Inspired by the famous detective Sherlock Holmes, this project aims to "investigate" and find the perfect recipe for any query you have.

The architecture of SherlockRecipes is based on **Sperlinked** combined with **Qdrant** to provide efficient and accurate recipe search capabilities.

---

### Why "SherlockRecipes"?

Just like Sherlock Holmes solves mysteries, this project helps you solve the mystery of "What should I cook today?" by searching through a rich dataset of recipes to find the best match.

---

## Repository Name

**sherlockrecipes**

---

Feel free to explore, contribute, and help make cooking an exciting investigation! 🍽️🕵️‍♂️

## Dataset Preparation

### Dataset
#### Dataset License Notice ⚠️

The dataset used in this project is sourced from [https://zenodo.org/records/15169428](https://zenodo.org/records/15169428).

**Important:**  
The license type for this dataset is not explicitly stated on the Zenodo page.  
Before using, redistributing, or modifying the dataset, please verify the license terms directly on the dataset page or contact the dataset authors to ensure compliance with their usage policies.

This project assumes proper attribution and respect for any license or usage restrictions associated with the dataset.

Thank you for understanding!

#### Create dataset in jsonl
See notebook dataset.ipynb


## AI Model
https://huggingface.co/numind/NuExtract-1.5
To Do
Because I have no access to openai I will plan to use a local LLM to classify natural query tpo json

### Customizing the superlinked_app folder

#### index.py
Fields like Name, Ingredients, Instructions, Category, and Cuisine are embedded for semantic search, using the configured embedding model.

Numeric fields (Rating Value, Preparation Time, Cooking Time) are included as number spaces for scoring and filtering.

Metadata like Nutrition and URL are included for hard filtering or display but are not embedded.

Adjust min_value and max_value for time fields based on your dataset distribution.

Field names are adapted to Python conventions where necessary (e.g., Rating_Value instead of Rating Value).

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
Please wait until the ingestion is finished. You will see the message.
Because for 500 recipes the payload is bigger than 32MB, I decided to split as exaplained in the dataset_loading.ipynb



