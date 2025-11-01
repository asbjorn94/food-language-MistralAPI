import os
import time
import random
import json
from mistralai import Mistral

def extract_ingredient_information(ingredients: list[str], max_retries=5) -> dict:
    api_key = os.getenv("MISTRAL_API_KEY")
    client = Mistral(api_key=api_key)

    prompt = f"""
    Extract the following information from each ingredient in the list below.
    Return the result as a JSON list of dictionaries with the fields:
    "ingredient": {{
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
    "ingredient": {{
        "name": string,
        "unit": str or null
        "quantity": int, float or null.
    }}

    The name should exclude any commentary information, that doesn't describe the ingredient.

    Examples: 
    "5 cm ingefær (kan udelades)" should return:
    
    "ingredient": {{
        "name": "ingefær",
        "unit": "cm"
        "quantity": 5
    }}

    "1 stort græskar" should return:
    
    "ingredient": {{
        "name": "græskar",
        "unit": "stort"
        "quantity": 1
    }}


    "En lime" should return:
    
    "ingredient": {{
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
            ingredients_data = json.loads(content)
            return ingredients_data
        except Exception as e:
            if "429" in str(e) and i < max_retries - 1:
                wait_time = (2 ** i) + random.random()
                print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise