import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

# Load the API key from the .env file
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
BASE_URL = "https://api.github.com"


# splits a github url into owner and repo name
def parse_github_url(url):
    url = url.strip().rstrip("/")
    parts = url.split("/")
    if len(parts) < 5 or "github.com" not in parts:
        raise ValueError(f"Invalid GitHub URL: {url}")
    owner = parts[-2]
    repo = parts[-1]
    return owner, repo


# calls the github api and returns key repo metadata as a dictionary
def get_repo_info(owner, repo):
    response = requests.get(f"{BASE_URL}/repos/{owner}/{repo}", headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return {
        "name": data["name"],
        "owner": data["owner"]["login"],
        "description": data.get("description", ""),
        "language": data.get("language", ""),
        "stars": data["stargazers_count"],
    }


# fetches the readme from github and decodes it from base64 to plain text
def get_readme(owner, repo):
    response = requests.get(f"{BASE_URL}/repos/{owner}/{repo}/readme", headers=HEADERS)
    response.raise_for_status()
    encoded_content = response.json()["content"]
    return base64.b64decode(encoded_content).decode("utf-8")
