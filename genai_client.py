import os
from google import genai
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


# turns repo data into plain text so the AI can read it
def build_repo_summary(repo_data):
    name = repo_data.get("repo_name", "Unknown")
    owner = repo_data.get("owner", "Unknown")
    description = repo_data.get("description", "No description provided")
    language = repo_data.get("language", "Unknown")
    stars = repo_data.get("stars", 0)
    readme = repo_data.get("readme", "No README available")

    return (
        f"Repository: {name} by {owner}\n"
        f"Description: {description}\n"
        f"Main language: {language}\n"
        f"Stars: {stars}\n"
        f"README:\n{readme[:2000]}"
    )


# asks the AI to explain the project in plain english for non-technical people
def generate_nontechnical_explanation(repo_data):
    summary = build_repo_summary(repo_data)

    prompt = f"""
You are helping a developer explain one of their projects to non-technical people like family or friends.

Here is the project:
{summary}

Write 2-3 short paragraphs explaining:
- What this project does (no jargon)
- What problem it solves
- Why it matters to everyday people

Write simply, like explaining to a curious 12-year-old.
"""
    response = _get_client().models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text.strip()


# asks the AI to create 5 interview talking points about this specific project/repo
def generate_interview_talking_points(repo_data):
    summary = build_repo_summary(repo_data)

    prompt = f"""
You are a career coach preparing a developer to talk about one of their projects in a job interview.

Here is the project:
{summary}

Write 5 interview talking points about this project. Each one should:
- Highlight a specific feature, technical decision, or challenge from this project
- Be 2-3 sentences long
- Sound natural when spoken out loud

Format as a numbered list.
"""
    response = _get_client().models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text.strip()


# asks the AI to write resume bullet points specifically about this project
def generate_resume_bullets(repo_data):
    summary = build_repo_summary(repo_data)

    prompt = f"""
You are a professional resume writer for software engineers.

Here is one of their projects:
{summary}

Write 3-5 resume bullet points about this project. Each one should:
- Start with a strong action verb (Built, Developed, Designed, Integrated, etc.)
- Mention the specific technology or tools used
- Be one short line, ready to paste into a resume
- If possible use numerical data to show impact (e.g., "Reduced load time by 30%")

Format using bullet points (•). Do not use markdown, asterisks, or bold text.
"""
    response = _get_client().models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text.strip().replace("**", "").replace("*", "")


# prints all three AI outputs in a clean readable format
def display_results(repo_name, results):
    print("=" * 50)
    print(f"  AI ANALYSIS FOR: {repo_name}")
    print("=" * 50)

    print("\n--- NON-TECHNICAL EXPLANATION ---")
    print(results["nontechnical_explanation"])

    print("\n--- INTERVIEW TALKING POINTS ---")
    print(results["interview_talking_points"])

    print("\n--- RESUME BULLET POINTS ---")
    print(results["resume_bullets"])

    print("\n" + "=" * 50)


# runs all three AI prompts for a repo and returns the results as a dictionary
def analyze_repo(repo_data):
    repo_name = repo_data.get("repo_name", "unknown")
    print(f"Generating AI analysis for: {repo_name} made by {repo_data.get('owner', 'unknown')}...")

    results = {
        "repo_name": repo_name,
        "nontechnical_explanation": generate_nontechnical_explanation(repo_data),
        "interview_talking_points": generate_interview_talking_points(repo_data),
        "resume_bullets": generate_resume_bullets(repo_data),
    }

    display_results(repo_name, results)
    return results


# testing block uncomment to test just this file :D
# enter python3 genai_client.py to run

# if __name__ == "__main__":
#     test_data = {
#         "repo_name": "SipSafe",
#         "owner": "kaylainoa",
#         "description": "AI-powered mobile safety app that detects drink tampering, provides voice guidance, and alerts trusted contacts in real time.",
#         "language": "TypeScript",
#         "stars": 0,
#         "readme": """SipSafe — Best Use of Digital Ocean, WiNGHacks 2026

# A mobile app that helps you drink safer. SipSafe uses AI-powered drink verification,
# real-time BAC estimation, and emergency contact alerts to keep you and your crew safe on a night out.

# Features:
# - AI Drink Verification: Snap a photo of your drink and Google Gemini vision AI checks for signs of tampering
# - Live BAC Estimation: Real-time blood alcohol content tracking using the Widmark formula
# - Drink Logging: Log drinks by type and track them through the night
# - Night Receipt: A receipt-style summary of last night's drinks
# - Emergency Alerts: One-tap SMS to your saved emergency contacts
# - Voice Feedback: ElevenLabs TTS reads verification results aloud after each scan
# """,
#     }

#     analyze_repo(test_data)
