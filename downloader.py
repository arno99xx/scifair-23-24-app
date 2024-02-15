
# https://filebin.net/uf8cv67w6oipvcfy/saved_models.zip
# The bin uf8cv67w6oipvcfy was created 4 minutes ago, updated 3 minutes ago and it expires 6 days from now. It contains 1 uploaded file at 154 MB.
# date: Feb 15 2024

import os
import urllib.request
import zipfile


urls = { 
    "saved_models" : "https://filebin.net/uf8cv67w6oipvcfy/saved_models.zip"
}

def download_all():
    for item in urls.items():
        name = item[0]
        url = item[1]
        filename = f"{name}.zip"
        if os.path.exists(filename):
            print(f"already exists file {filename}")
        else:
            print(f"downloading {filename} from {url} ...")
            urllib.request.urlretrieve(url, filename)
    print(f"done downloading all")

def unzip_all():
    for item in urls.items():
        name = item[0]
        url = item[1]
        filename = f"{name}.zip"
        print(filename)
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            print(f"unzipping {filename} to folder")
            zip_ref.extractall(f"{name}")


if __name__ == "__main__":
    download_all()
    unzip_all()
