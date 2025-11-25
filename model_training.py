from sentence_transformers import SentenceTransformerTrainer
from sentence_transformers.losses import CosineSimilarityLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments, BatchSamplers
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator, SimilarityFunction

# from torch.utils.data import DataLoader, Dataset
from pathlib import Path
from datasets import load_dataset, DatasetDict
from product_mapper import initialize_model

if __name__ == "__main__":
    base_model = initialize_model("all-MiniLM-L6-v2")
    loss = CosineSimilarityLoss(base_model)

    dataset = load_dataset("csv", data_files="danish_ingredient_pairs_manual.csv")
    train_valtest = dataset['train'].train_test_split(test_size=0.3, seed=42)
    val_test = train_valtest['test'].train_test_split(test_size=0.5, seed=42)

    split_dataset = DatasetDict({
        'train': train_valtest['train'],
        'validation': val_test['train'],
        'test': val_test['test']
    })

    print()
    print('Training dataset:')
    print(split_dataset['train'])
    print()
    print('Validation dataset:')
    print(split_dataset['validation'])

    args = SentenceTransformerTrainingArguments(
        # Required parameter:
        output_dir="sentence-transformer-models/all-MiniLM-L6-v2-finetuned-DK-ingredients",
        # Optional training parameters:
        num_train_epochs=1,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_ratio=0.1,
        fp16=True,  # Set to False if your GPU can't handle FP16
        bf16=False,  # Set to True if your GPU supports BF16
        batch_sampler=BatchSamplers.NO_DUPLICATES,
        # Optional tracking/debugging parameters:
        eval_strategy="steps",
        eval_steps=100,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        logging_steps=100
    )

    val_dataset = split_dataset['validation']

    val_evaluator = EmbeddingSimilarityEvaluator(
        sentences1=val_dataset["ingredient_1"],
        sentences2=val_dataset["ingredient_2"],
        scores=val_dataset["label"],
        main_similarity=SimilarityFunction.COSINE,
        name="finetuned-validation",
    )

    trainer = SentenceTransformerTrainer(
        model=base_model,
        args=args,
        train_dataset=split_dataset['train'],
        eval_dataset=val_dataset,
        loss=loss,
        evaluator=train_valtest,
    )
    
    trainer.train()

    base_model.save_pretrained("sentence-transformer-models/all-MiniLM-L6-v2-finetuned-DK-ingredients/final")





