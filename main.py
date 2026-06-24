from github_client import parse_github_url, get_repo_info, get_readme
from genai_client import analyze_repo

url = input("Enter a GitHub repo URL: ")

owner, repo_name = parse_github_url(url)
repo_info = get_repo_info(owner, repo_name)
readme = get_readme(owner, repo_name)

repo_data = {
    "repo_name": repo_info["name"],
    "owner": repo_info["owner"],
    "description": repo_info["description"],
    "language": repo_info["language"],
    "stars": repo_info["stars"],
    "readme": readme,
}

analyze_repo(repo_data)
