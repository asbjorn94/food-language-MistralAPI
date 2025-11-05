import os
import time
import random
import json
from pathlib import Path
from mistralai import Mistral
from language import Language

def fetch_from_api(ingredients: list[str], max_retries=5):
    api_key = os.getenv("MISTRAL_API_KEY")
    client = Mistral(api_key=api_key)

    prompt = f"""
    Extract the following information from each ingredient in the list below.
    Return the result as a JSON list of dictionaries with the fields:
    {{
        "name": string,
        "unit": str or null
        "quantity": int, float or null.
    }}

    The name should exclude any commentary information, that doesn't describe the ingredient.

    Ingredients:
    {ingredients}
    """

    prompt_with_examples = f"""
    Extract the following information from each ingredient in the list below.
    Return the result as a JSON list of dictionaries with the fields:
    {{
        "name": str,
        "unit": str or null
        "quantity": float or null.
    }}

    The name should exclude any commentary information, that doesn't describe the ingredient.

    Examples: 
    "5 cm ingefær (kan udelades)" should return:
    
    {{
        "name": "ingefær",
        "unit": "cm"
        "quantity": 5
    }}

    "1 stort græskar" should return:
    
    {{
        "name": "græskar",
        "unit": "stort"
        "quantity": 1
    }}


    "En lime" should return:
    
    {{
        "name": "lime"
        "unit": null
        "quantity": 1
    }}


    
    Ingredients:
    {ingredients}
    """

    for i in range(max_retries):
        try:
            chat_response = client.chat.complete(
                model="mistral-tiny",
                messages=[{"role": "user", "content": prompt_with_examples}],
                response_format={"type": "json_object"}
            )
            content = chat_response.choices[0].message.content
            ingredients_data = json.loads(str(content))
            if ingredients_data:
                save_to_json(ingredients_data)
                return ingredients_data
            else:
                return []
        except Exception as e:
            if "429" in str(e) and i < max_retries - 1:
                wait_time = (2 ** i) + random.random()
                print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise

def get_json(file: str):
    path = Path(file)
    if path.exists():
        with open(str(path)) as json_file:
            return json.load(json_file)
    else:
        print(f"Couldn't load ingredients since {file} doesn't exist.")

def extract_ingredient_information(ingredients: list[str], max_retries=5, use_saved_json=False, language=Language.DK) -> list[dict[str, str | float]]:
    if use_saved_json is True:
        if language is Language.DK:
            return get_json("ingredients_DK.json")
        elif language is Language.EN:
            return get_json("ingredients_EN.json")
        else:
            print("Couldn't load ingredients since json file doesn't exist for the given language.")


    else:
        fetch_from_api(ingredients,max_retries)
       

def save_to_json(response: str):
    with open(str(Path("ingredients.json")), "w", encoding='utf8') as f:
        result_json = json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False)
        f.write(result_json) 