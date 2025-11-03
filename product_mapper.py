import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path

#Several functions in this file is inspired by code from the following repository: https://github.com/mkaanaslan/carbon-footprint-wizard

# product_names = [
#     "kyllingefilet",
#     "ekstra jomfru olivenolie",
#     "løg",
#     "hakket hvidløg",
#     "dåse med sorte bønner",
#     "søde majs",
#     "hakkede tomater",
#     "tomater",
#     "grøntsagsbouillon, terning",
#     "tørret oregano",
#     "røget paprika"
# ]

def initialize_model() -> SentenceTransformer:
    model_path = Path("ST-model")
    if not model_path.exists():
        model = SentenceTransformer("all-MiniLM-L6-v2")
        model.save(str(model_path))
    else:
        model = SentenceTransformer(str(model_path))

    return model


def get_product_names() -> list[str]:
    dir = os.path.dirname(__file__)
    file = dir + '/res/DSK_v1.2.xlsx'
    dsk_db = pd.read_excel(file, sheet_name = "DK", index_col = 0)
    product_names = dsk_db['Produkt'].tolist()
    return product_names

def create_vector_database(model: SentenceTransformer):
    product_names = get_product_names()
    
    vector_db = {
            'index': None,
            'products': product_names
        }

    database_embeddings = model.encode(product_names) #10 x 384-dimensional vectors (each corresponding to a string)
    faiss.normalize_L2(database_embeddings)
    dimension = database_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(database_embeddings)
    vector_db['index'] = index

    return vector_db

def search_top_k(model: SentenceTransformer, vector_database: dict, ingredient: str, k: int, verbose: bool=False):
    ingredient_embedding = model.encode([ingredient])
    faiss.normalize_L2(ingredient_embedding)
    
    results = {}

    if verbose: print(f"Ingredient: {ingredient}")
    
    # for name, data in vector_database.items():
    distances, idx = vector_database['index'].search(ingredient_embedding, k)
    results = [vector_database['products'][j] for _, j in enumerate(idx[0])]
    if verbose:
        print(f"Top {k} results:")
        for i, name in enumerate(results):
            print(f"{i+1}.")
            print(f"Name: {name}")
            print(f"Distance: {distances[0][i]}")
            print()
        print("-------------------------------------------------")
        print()
        
    return results

def get_best_matches(ingredients: list[dict]):
    model = initialize_model()
    vector_db = create_vector_database(model)
    print(type(vector_db))
    print(model)

    result = []
    for ingredient in ingredients:
        top_k_results = search_top_k(model, vector_db, ingredient['name'], 5, False)
        result.append(top_k_results)

    return result