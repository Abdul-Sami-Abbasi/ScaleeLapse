import os
import re
from pathlib import Path
import pandas as pd
from datasets import load_dataset, Image


BASE_DIR = Path(__file__).resolve().parents[3]
TARGET_DIR = BASE_DIR / "data" / "processed" / "nlp"
TARGET_DIR.mkdir(parents=True, exist_ok=True)

print(f"Target directory: {TARGET_DIR}")
print("Fetching caption dataset from Hugging Face...")


ds = load_dataset("kkcosmos/instagram-images-with-captions", split="train")


if "image" in ds.features:
    ds = ds.cast_column("image", Image(decode=False))

print("Extracting text data into Pandas...")

text_data = [{"caption": example.get("caption", "")} for example in ds]
df = pd.DataFrame(text_data)

def clean_and_split(text):
    if not isinstance(text, str):
        return "", ""
    hashtags = re.findall(r"#\w+", text)
    clean_text = re.sub(r"#\w+", "", text)
    clean_text = re.sub(r"http\S+", "", clean_text).strip()
    return clean_text, " ".join(hashtags)

print("Cleaning captions and extracting hashtag targets...")
df[["clean_caption", "target_hashtags"]] = df["caption"].apply(
    lambda x: pd.Series(clean_and_split(x))
)


filtered_df = df[
    (df["clean_caption"].str.len() > 10) & 
    (df["target_hashtags"].str.split().str.len() >= 1)
].copy()


train_df = filtered_df.sample(frac=0.8, random_state=42)
val_df = filtered_df.drop(train_df.index)

train_path = TARGET_DIR / "train_nlp.csv"
val_path = TARGET_DIR / "val_nlp.csv"

train_df.to_csv(train_path, index=False)
val_df.to_csv(val_path, index=False)

print("\n--- NLP EXTRACT COMPLETE ---")
print(f"Saved Train Set ({len(train_df)} rows) -> {train_path}")
print(f"Saved Val Set ({len(val_df)} rows) -> {val_path}")