from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path

#Several functions in this file is inspired by code from the following repository: https://github.com/mkaanaslan/carbon-footprint-wizard

# Example data: ingredient names and database entries
ingredient_names = [
    "chicken breast",
    "olive oil",
    "red onion",
    "garlic",
    "black beans",
    "corn",
    "tomatoes",
    "vegetable broth",
    "oregano",
    "paprika"
]

product_names = [
    "chicken filet",
    "extra virgin olive oil",
    "onion",
    "minced garlic",
    "black beans can",
    "sweet corn",
    "diced tomatoes",
    "vegetable stock cube",
    "dried oregano",
    "smoked paprika"
]

def initialize_model() -> SentenceTransformer:
    model_path = Path("ST-model")
    if not model_path.exists():
        model = SentenceTransformer("all-MiniLM-L6-v2")
        model.save(str(model_path))
    else:
        model = SentenceTransformer(str(model_path))

    return model


def create_vector_database(product_names: list[str], model: SentenceTransformer):
    vector_db = {
        'DSK': {
            'index': None,
            'products': product_names
        }
    } 



    database_embeddings = model.encode(product_names) #10 x 384-dimensional vectors (each corresponding to a string)
    faiss.normalize_L2(database_embeddings)
    dimension = database_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(database_embeddings)
    vector_db['DSK']['index'] = index

    return vector_db

def search_top_k(model: SentenceTransformer, vector_database: dict, ingredient: str, k: int, verbose: bool=False):
    ingredient_embedding = model.encode([ingredient])
    faiss.normalize_L2(ingredient_embedding)
    
    results = {}

    if verbose: print(f"Ingredient: {ingredient}")
    
    for name, data in vector_database.items():
        distances, idx = data['index'].search(ingredient_embedding, k)
        results[name] = [data['products'][j] for _, j in enumerate(idx[0])]
        if verbose:
            print(f"Top {k} results: : {results[name]}")
            print()
        
    return results

model = initialize_model()
vector_db = create_vector_database(product_names, model)
print(type(vector_db))
print(model)
for ingredient in ingredient_names:
    top_k_results = search_top_k(model, vector_db, ingredient, 5, True)