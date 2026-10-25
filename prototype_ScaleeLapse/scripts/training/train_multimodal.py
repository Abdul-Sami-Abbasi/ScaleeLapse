"""Train the proposed image/text extension only from genuinely paired manifests.

CSV columns: image_path,caption,target_hashtags,source_id,consent_reference,split.
Paths must be inside data/. Train/validation source groups must be disjoint.
"""

import argparse, csv, json, hashlib, random, time, sys, platform
from collections import Counter
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision.models import ResNet50_Weights
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai.nlp.multimodal import MultimodalHashtags
from scripts.training.train_hashtags import metrics


def main():
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--output", type=Path, default=ROOT / "models/multimodal")
    a = p.parse_args()
    with a.manifest.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or any(not r["consent_reference"] or not r["source_id"] for r in rows):
        raise ValueError(
            "Actual paired, consented records and source groups are required."
        )
    train = [r for r in rows if r["split"] == "train"]
    validation = [r for r in rows if r["split"] == "validation"]
    if not train or not validation:
        raise ValueError("Separate train and validation records required.")
    if {r["source_id"] for r in train} & {r["source_id"] for r in validation}:
        raise ValueError("Source groups overlap across splits.")
    hashes = {}
    for r in rows:
        path = (ROOT / r["image_path"]).resolve()
        if not path.is_relative_to(ROOT / "data") or not path.is_file():
            raise ValueError("Image must exist inside data/.")
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        if h in hashes and hashes[h] != r["split"]:
            raise ValueError("Duplicate image crosses splits.")
        hashes[h] = r["split"]
    labels = sorted({t.lower() for r in train for t in r["target_hashtags"].split()})
    if len(labels) < 10:
        raise ValueError("At least ten hashtag labels required for top-10 evaluation.")
    label_index = {v: i for i, v in enumerate(labels)}
    tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
    transform = ResNet50_Weights.DEFAULT.transforms()

    class Paired(Dataset):
        def __init__(self, items):
            self.items = items

        def __len__(self):
            return len(self.items)

        def __getitem__(self, i):
            r = self.items[i]
            with Image.open(ROOT / r["image_path"]) as im:
                image = transform(im.convert("RGB"))
            encoded = {
                k: v[0]
                for k, v in tokenizer(
                    r["caption"],
                    max_length=64,
                    truncation=True,
                    padding="max_length",
                    return_tensors="pt",
                ).items()
            }
            target = torch.zeros(len(labels))
            for tag in r["target_hashtags"].lower().split():
                if tag in label_index:
                    target[label_index[tag]] = 1
            return image, encoded, target

    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)
    torch.set_num_threads(4)
    model = MultimodalHashtags(len(labels))
    # Frozen encoders make a reproducible late-fusion baseline, not full fine-tuning.
    for module in [model.visual, model.text]:
        for parameter in module.parameters():
            parameter.requires_grad = False
    optimizer = torch.optim.AdamW(model.classifier.parameters(), lr=1e-3)
    criterion = torch.nn.BCEWithLogitsLoss()
    for epoch in range(a.epochs):
        model.train()
        model.visual.eval()
        model.text.eval()
        for images, encoded, target in DataLoader(
            Paired(train), batch_size=a.batch_size, shuffle=True
        ):
            optimizer.zero_grad()
            loss = criterion(model(images, **encoded), target)
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch + 1}: final batch loss={loss.item():.5f}", flush=True)
    model.eval()
    truth = []
    pred = []
    with torch.no_grad():
        for images, encoded, target in DataLoader(
            Paired(validation), batch_size=a.batch_size
        ):
            truth.append(target.numpy())
            pred.append(model(images, **encoded).sigmoid().numpy())
    a.output.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), a.output / "weights.pt")
    (a.output / "labels.json").write_text(json.dumps(labels))
    report = {
        "model": "ResNet-50 + DistilBERT frozen encoders and trainable fusion head",
        "dataset": str(a.manifest),
        "dataset_version": hashlib.sha256(a.manifest.read_bytes()).hexdigest(),
        "parameters": {
            "epochs": a.epochs,
            "batch_size": a.batch_size,
            "max_length": 64,
        },
        "split": "source-group-disjoint provided train/validation",
        "seed": 42,
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metrics": metrics(np.concatenate(truth), np.concatenate(pred)),
        "environment": platform.python_version(),
        "notes": [
            "Vocabulary from training only; validate all-reference label coverage separately.",
            "This is an offline experiment, not integrated production inference.",
        ],
    }
    (a.output / "evaluation.json").write_text(json.dumps(report, indent=2))
    (ROOT / "artifacts/experiments/multimodal.json").write_text(
        json.dumps(report, indent=2)
    )


if __name__ == "__main__":
    main()
