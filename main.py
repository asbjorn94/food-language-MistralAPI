import json
from dotenv import load_dotenv
from ingredient_parser import extract_ingredient_information
from product_mapper import get_best_matches

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


if __name__ == "__main__":
    # result = make_prompt("What is the best French cheese?")
    ingredients = extract_ingredient_information(ingredients)
    best_matches: list[dict] = get_best_matches(ingredients)

    for i in range(0,len(ingredients)):
        print(f"Ingredient: {ingredients[i]}")
        print(f"Best matches: {best_matches[i]}")
        print()