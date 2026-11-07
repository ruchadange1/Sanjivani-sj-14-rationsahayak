import requests
from pathlib import Path
 
# getting project folder path
base_path = Path(__file__).resolve().parent.parent
 
# folder where downloaded files will be saved
raw_folder = base_path / "data" / "raw"
 
# creating folder if it does not exist
raw_folder.mkdir(parents=True, exist_ok=True)
 
 
# government website links
documents = [
    {
        "name": "dfpd_faq.html",
        # The page https://dfpd.gov.in/faqs/en is only an EMPTY SHELL.
        # Its JavaScript loads the FAQ answers from this address afterwards,
        # so we download that address directly.
        "url": "https://dfpd.gov.in/Home/GeneralFAQsList?language=1",
        # the browser sends these two headers when the JavaScript asks for the FAQs
        "extra_headers": {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://dfpd.gov.in/faqs/en"
        }
    },
    {
        "name": "nfsa_features.html",
        "url": "https://nfsa.gov.in/portal/Salient_Features_NFSA_AA"
    },
    {
        "name": "mahafood_nfsa.html",
        "url": "https://mahafood.gov.in/en/national-food-security-act-2013/"
    }
]
 
 
# function to download documents
def download_documents():
 
    for document in documents:
 
        try:
            print("\nDownloading:", document["name"])
 
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9"
            }
 
            # add the extra headers only for the documents that need them
            headers.update(document.get("extra_headers", {}))
 
            response = requests.get(
                document["url"],
                timeout=30,
                headers=headers
            )
 
            # checking HTTP errors
            response.raise_for_status()
 
            # saving downloaded content
            file_path = raw_folder / document["name"]
 
            with open(file_path, "wb") as file:
                file.write(response.content)
 
            print("Downloaded successfully:", document["name"])
            print("File size:", len(response.content), "bytes")
 
            # a tiny file usually means the page content was not really downloaded
            if len(response.content) < 2000:
                print("WARNING: file is very small, the content may be missing")
 
        except requests.exceptions.Timeout:
            print("Request timed out:", document["url"])
 
        except requests.exceptions.HTTPError as error:
            print("HTTP error:", error)
 
        except requests.exceptions.RequestException as error:
            print("Download failed:", error)
 
        except OSError as error:
            print("File saving error:", error)
 
 
if __name__ == "__main__":
    download_documents()
 