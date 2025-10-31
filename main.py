import os
import time
import random
import json
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

ingredients = [
    "600 g kyllingeinderfilet (i mundrette stykker)",
    "2 spsk olie",
    "1 stort rødløg (hakket)",
    "6 fed hvidløg (knust og hakket)",
    "1 tsk spidskommen",
    "250 g sorte bønner (svarende til en dåse)",
    "250 g majs (ca. en stor dåse)",
    "1 dåse hakkede tomater",
    "2 dl vand",
    "1 terning grøntsagsbouillon",
    "2 tsk oregano",
    "2 tsk paprika",
    "1 tsk chili (eller cayennepeber)",
    "citronsaft (friskpresset)",
    "salt og friskkværnet peber"
]

def extract_ingredient_information(ingredients: list[str], max_retries=5):
    api_key = os.getenv("MISTRAL_API_KEY")
    client = Mistral(api_key=api_key)

    prompt = f"""
    Extract the following information from each ingredient in the list below.
    Return the result as a JSON list of dictionaries with the fields:
    "ingredient": {{
        "name": string,
        "unit": str or null,
        "quantity": str, int, float, or null
    }}

    Ingredients:
    {ingredients}
    """

    for i in range(max_retries):
        try:
            chat_response = client.chat.complete(
                model="mistral-tiny",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return chat_response
        except Exception as e:
            if "429" in str(e) and i < max_retries - 1:
                wait_time = (2 ** i) + random.random()
                print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise


if __name__ == "__main__":
    # result = make_prompt("What is the best French cheese?")
    result = extract_ingredient_information(ingredients)
    content = result.choices[0].message.content
    ingredients = json.loads(content)

    for ingredient in ingredients:
        ingredient = ingredient['ingredient']
        print(f"Name: {ingredient['name']}")
        print(f" - Unit: {ingredient['unit']}")
        print(f" - Quantity: {ingredient['quantity']}")
        print()