import os
import requests

# Model info
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
FILES_TO_DOWNLOAD = [
    "config.json",
    "pytorch_model.bin",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.txt",
    "special_tokens_map.json",
    "modules.json",
    "sentence_bert_config.json"
]

BASE_URL = f"https://huggingface.co/{MODEL_ID}/resolve/main/"
OUTPUT_DIR = os.path.join("engine", "model_data", "all-MiniLM-L6-v2")

def download_file(filename):
    url = BASE_URL + filename
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    print(f"Downloading {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Saved to {output_path}")
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Downloading model '{MODEL_ID}' to '{OUTPUT_DIR}'...")
    
    for filename in FILES_TO_DOWNLOAD:
        download_file(filename)
        
    print("\nDownload complete. Please commit the 'engine/model_data' folder to git.")

if __name__ == "__main__":
    main()
