import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from language import Language
from pathlib import Path

#Some functions in this file is inspired by code from the following repository: https://github.com/mkaanaslan/carbon-footprint-wizard

def initialize_model(model_name: str) -> SentenceTransformer:
    model_path = Path("sentence-transformer-models/" + model_name)
    if not model_path.exists():
        model = SentenceTransformer(model_name)
        model.save(str(model_path))
    else:
        model = SentenceTransformer(str(model_path))
    return model


def get_dsk_excel_column(path,sheet_name: str, column_name: str):
        dsk_db = pd.read_excel(str(path), sheet_name = sheet_name, index_col = 0)
        product_names = dsk_db[column_name].tolist()
        return product_names    


def get_product_names(language: Language=Language.DK) -> list[str]:
    path = Path("res/DSK_v1.2.xlsx")
    if language is Language.EN:
        return get_dsk_excel_column(path,"GB","Name")
    else:
        return get_dsk_excel_column(path,"DK","Produkt")


def create_vector_database(model: SentenceTransformer, language: Language=Language.DK):
    product_names = get_product_names(language)
    
    vector_db = {
            'index': None,
            'products': product_names
        }
    
    index_path = None
    if language is Language.EN:
        index_path = Path('product_index_EN.faiss')
    else:
        index_path = Path('product_index_DK.faiss')
        
    if index_path.exists():
        vector_db['index'] = faiss.read_index(str(index_path))
    else:
        database_embeddings = model.encode(product_names) #384-dimensional vectors
        faiss.normalize_L2(database_embeddings)
        dimension = database_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(database_embeddings)
        vector_db['index'] = index
        faiss.write_index(index, str(index_path)) #Write to disk

    return vector_db


def search_top_k(model: SentenceTransformer, vector_database: dict, ingredient: str, k: int, verbose: bool=True):
    ingredient_embedding = model.encode([ingredient])
    faiss.normalize_L2(ingredient_embedding)
    
    results = {}

    if verbose: print(f"Ingredient: {ingredient}")
    
    distances, idx = vector_database['index'].search(ingredient_embedding, k)
    results = [vector_database['products'][j] for _, j in enumerate(idx[0])]
    if verbose:
        print(f"Top {k} results:")
        print_res = ""
        for i, name in enumerate(results):
            print_res += f"{i+1}. ({name}, {round(float(distances[0][i]),3)}) "
        print(print_res)
        print("-------------------------------------------------")
        print()
    return results


def get_best_matches(ingredients: list[dict], language=Language.DK):
    model = initialize_model("all-MiniLM-L6-v2")
    vector_db = create_vector_database(model, language)
    result = []
    for ingredient in ingredients:
        top_k_results = search_top_k(model, vector_db, ingredient['name'], 5)
        result.append(top_k_results)
    return result