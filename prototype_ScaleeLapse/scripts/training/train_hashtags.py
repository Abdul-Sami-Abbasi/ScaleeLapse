"""Actual DistilBERT multilabel training; local datasets only, reproducible manifest.

Default freezes the encoder except its final transformer block to fit CPU budgets.
Pass --full-finetune to train the whole encoder. Validation never builds vocabulary.
"""

import argparse, json, hashlib, random, platform, time, os
from pathlib import Path
from collections import Counter
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return [
        json.loads(x) for x in path.read_text(encoding="utf-8").split("\n") if x.strip()
    ]


def metrics(targets, predictions, k=10):
    indices = np.argsort(-predictions, axis=1)[:, :k]
    pred = np.zeros_like(targets)
    np.put_along_axis(pred, indices, 1, axis=1)
    tp = (pred * targets).sum(1)
    den = targets.sum(1)
    return {
        "precision_at_k": float((tp / k).mean()),
        "recall_at_k": float(
            np.divide(tp, den, out=np.zeros_like(tp, dtype=float), where=den > 0).mean()
        ),
        "micro_f1": float(2 * tp.sum() / max(1, pred.sum() + targets.sum())),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--min-frequency", type=int, default=5)
    parser.add_argument("--full-finetune", action="store_true")
    parser.add_argument("--base-model", default="distilbert/distilbert-base-uncased")
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    train = load(ROOT / "data/splits/nlp/train.jsonl")
    val = load(ROOT / "data/splits/nlp/validation.jsonl")
    counts = Counter(t for r in train for t in r["hashtags"])
    labels = sorted(t for t, c in counts.items() if c >= args.min_frequency)
    if len(labels) < 10:
        raise ValueError("Need at least 10 labels with enough training examples.")
    label_index = {v: i for i, v in enumerate(labels)}
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)

    class CaptionDataset(Dataset):
        def __init__(self, rows):
            self.encoded = tokenizer(
                [r["text"] for r in rows],
                truncation=True,
                padding="max_length",
                max_length=64,
                return_tensors="pt",
            )
            self.targets = torch.zeros((len(rows), len(labels)))
            for i, r in enumerate(rows):
                for t in r["hashtags"]:
                    if t in label_index:
                        self.targets[i, label_index[t]] = 1

        def __len__(self):
            return len(self.targets)

        def __getitem__(self, i):
            return {
                **{k: v[i] for k, v in self.encoded.items()},
                "labels": self.targets[i],
            }

    train_data = CaptionDataset(train)
    val_data = CaptionDataset(val)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        num_labels=len(labels),
        problem_type="multi_label_classification",
    )
    if not args.full_finetune:
        for name, p in model.named_parameters():
            p.requires_grad = not name.startswith("distilbert.") or name.startswith(
                "distilbert.transformer.layer.5."
            )
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=5e-5
    )
    start = time.time()
    losses = []
    for epoch in range(args.epochs):
        model.train()
        total = 0
        for step, batch in enumerate(
            DataLoader(train_data, batch_size=args.batch_size, shuffle=True)
        ):
            optimizer.zero_grad()
            loss = model(**batch).loss
            loss.backward()
            optimizer.step()
            total += loss.item()
            if step % 20 == 0:
                print(
                    f"epoch {epoch + 1} step {step} loss {loss.item():.5f}", flush=True
                )
        losses.append(total / (step + 1))
    model.eval()
    scores = []
    with torch.no_grad():
        for batch in DataLoader(val_data, batch_size=args.batch_size):
            scores.append(
                model(**{k: v for k, v in batch.items() if k != "labels"})
                .logits.sigmoid()
                .numpy()
            )
    predictions = np.concatenate(scores)
    result = metrics(val_data.targets.numpy(), predictions)
    # Also report recall against all human labels, including out-of-vocabulary targets.
    recommended = [[labels[i] for i in np.argsort(-p)[:10]] for p in predictions]
    result["recall_at_10_all_reference_labels"] = float(
        np.mean(
            [
                len(set(p) & set(r["hashtags"])) / max(1, len(r["hashtags"]))
                for p, r in zip(recommended, val)
            ]
        )
    )
    result["validation_label_coverage"] = sum(
        t in label_index for r in val for t in r["hashtags"]
    ) / sum(len(r["hashtags"]) for r in val)
    path = ROOT / "models/hashtag_transformer"
    path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(path)
    tokenizer.save_pretrained(path)
    (path / "labels.json").write_text(json.dumps(labels))
    report = {
        "model": args.base_model,
        "formulation": "multilabel classification",
        "training": vars(args),
        "seed": 42,
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset": json.loads((ROOT / "data/splits/nlp/manifest.json").read_text()),
        "metrics": result,
        "losses": losses,
        "seconds": time.time() - start,
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
        },
        "notes": [
            "Supplied dataset license UNKNOWN; confirm before redistribution.",
            "Partial fine-tuning unless full-finetune enabled.",
            "BLEU not reported for unordered hashtag sets; proposal formulation requires supervisor review.",
            "No untouched test set or SME-domain generalization claim.",
        ],
    }
    (path / "evaluation.json").write_text(json.dumps(report, indent=2))
    (ROOT / "artifacts/experiments/nlp_transformer.json").write_text(
        json.dumps(report, indent=2)
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
