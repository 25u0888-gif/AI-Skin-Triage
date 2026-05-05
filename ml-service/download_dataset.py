import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

def download_ham10000(destination="data/"):
    # Set the Kaggle API token environment variable before initializing the API
    os.environ["KAGGLE_API_TOKEN"] = "KGAT_e6adad56d9ade8ee29616e22a98ddff9"
    
    print("Authenticating with Kaggle API...")
    api = KaggleApi()
    api.authenticate()
    
    dataset = "kmader/skin-cancer-mnist-ham10000"
    
    print(f"Downloading dataset {dataset} to {destination}...")
    if not os.path.exists(destination):
        os.makedirs(destination)
        
    api.dataset_download_files(dataset, path=destination, unzip=False)
    
    zip_path = os.path.join(destination, "skin-cancer-mnist-ham10000.zip")
    if os.path.exists(zip_path):
        print(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destination)
        print("Extraction complete.")
        os.remove(zip_path) # Clean up zip file
    else:
        print("Download finished, but zip file not found. It may have already been extracted.")

if __name__ == "__main__":
    download_ham10000()
