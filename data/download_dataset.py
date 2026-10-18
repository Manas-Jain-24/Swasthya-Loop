"""
SwasthyaLoop — UCI 130-Hospitals Dataset Downloader
Downloads the official peer-reviewed clinical dataset from the UCI Machine Learning Repository.
Source: Strack et al., BioMed Research International, 2014.
"""

import urllib.request
import zipfile
import io
import os

DATASET_URL = "https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip"

def download_uci_dataset():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, "raw_uci_dataset")
    os.makedirs(target_dir, exist_ok=True)

    csv_path = os.path.join(target_dir, "diabetic_data.csv")
    if os.path.exists(csv_path):
        print(f"[OK] Dataset already present at: {csv_path}")
        return csv_path

    print(f"Downloading official UCI 130-Hospitals Dataset (101,766 encounters)...")
    print(f"Source: {DATASET_URL}")

    req = urllib.request.Request(DATASET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        zip_bytes = resp.read()

    print(f"Archive downloaded ({len(zip_bytes) / (1024*1024):.2f} MB). Extracting...")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        z.extractall(target_dir)

    print(f"[SUCCESS] Dataset extracted to: {target_dir}")
    print(f" - diabetic_data.csv ({os.path.getsize(csv_path) / (1024*1024):.2f} MB)")
    return csv_path

if __name__ == "__main__":
    download_uci_dataset()
