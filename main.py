import json
import time
from contextlib import contextmanager
from dotenv import load_dotenv
from ingredient_parser import extract_ingredient_information
from product_mapper import get_best_matches
from language import Language

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

@contextmanager
def timeit_context(name):
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"{name} took {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    language = Language.EN
    with timeit_context("Ingredient extraction"):
        ingredients = extract_ingredient_information(ingredients, use_saved_json=True, language=language)
    with timeit_context("Product matchting"):
        best_matches: list[dict] = get_best_matches(ingredients, language=language)