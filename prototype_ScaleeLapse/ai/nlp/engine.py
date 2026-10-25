import json
import re
import importlib.util
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=2)
def load_model(path, version):
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    return AutoTokenizer.from_pretrained(
        path, local_files_only=True
    ), AutoModelForSequenceClassification.from_pretrained(
        path, local_files_only=True
    ).eval()


def preprocess(text):
    text = re.sub(r"https?://\S+|#\w+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def recommend(caption, model_dir=None, k=10):
    clean = preprocess(caption)
    if not clean:
        raise ValueError("Enter a caption containing text, not only hashtags or links.")
    path = Path(model_dir) if model_dir else Path("models/hashtag_transformer")
    artifact = (path / "config.json").exists() and (path / "labels.json").exists()
    runtime = all(
        importlib.util.find_spec(x) is not None for x in ["torch", "transformers"]
    )
    if artifact and runtime:
        import torch

        tokenizer, model = load_model(
            str(path), (path / "config.json").stat().st_mtime_ns
        )
        with torch.no_grad():
            scores = model(
                **tokenizer(clean, return_tensors="pt", truncation=True, max_length=64)
            ).logits.sigmoid()[0]
        labels = json.loads((path / "labels.json").read_text())
        indices = scores.argsort(descending=True)[:k].tolist()
        evidence = (
            json.loads((path / "evaluation.json").read_text())
            if (path / "evaluation.json").exists()
            else {}
        )
        editorial = list(
            dict.fromkeys("#" + w.lower() for w in re.findall(r"[A-Za-z]{5,}", clean))
        )[:5]
        return {
            "status": "EXPERIMENTAL_TRANSFORMER",
            "hashtags": [labels[i] for i in indices],
            "scores": [float(scores[i]) for i in indices],
            "model": "DistilBERT multilabel (local artifact)",
            "validation": evidence.get("metrics", {}),
            "editorial_keywords": editorial,
            "notice": "Experimental model trained on the supplied general-domain captions. Validation quality is limited; review every suggestion. Scores are uncalibrated model outputs, not relevance guarantees.",
        }
    # Explicit editorial assistance; never masquerades as trained inference.
    stop = {
        "this",
        "that",
        "with",
        "from",
        "your",
        "have",
        "will",
        "about",
        "their",
        "there",
        "today",
        "https",
    }
    words = list(
        dict.fromkeys(
            w.lower()
            for w in re.findall(r"[A-Za-z]{4,}", clean)
            if w.lower() not in stop
        )
    )
    return {
        "status": "MODEL_RUNTIME_REQUIRED" if artifact else "MODEL_REQUIRED",
        "hashtags": ["#" + w for w in words[:k]],
        "scores": [],
        "model": None,
        "notice": "Keyword suggestions only. Install the local transformer dependencies and a fine-tuned artifact for academic inference.",
        "cta": "Consider a clear next step, such as asking readers to share their experience.",
    }
