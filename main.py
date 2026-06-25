from github_client import parse_github_url, get_repo_info, get_readme
from genai_client import analyze_repo
from database import init_db, save_repo, update_analysis

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

# run AI analysis
results = analyze_repo(repo_data)

# save repo info and AI analysis to the database
init_db()
save_repo({
    "owner": repo_info["owner"],
    "name": repo_info["name"],
    "description": repo_info["description"],
    "language": repo_info["language"],
    "stars": repo_info["stars"],
    "readme": readme,
})

analysis_text = (
    f"Non-technical explanation:\n{results['nontechnical_explanation']}\n\n"
    f"Interview talking points:\n{results['interview_talking_points']}\n\n"
    f"Resume bullets:\n{results['resume_bullets']}"
)
update_analysis(repo_info["owner"], repo_info["name"], analysis_text)
print("Analysis saved to database.")
