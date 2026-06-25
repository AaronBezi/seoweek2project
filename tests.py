import unittest
from unittest.mock import MagicMock, patch
from github_client import parse_github_url
from database import init_db, save_repo, get_repo, update_analysis
from genai_client import (
    build_repo_summary,
    generate_nontechnical_explanation,
    generate_interview_talking_points,
    generate_resume_bullets,
    display_results,
    analyze_repo,
)

SAMPLE_DB_REPO = {
    "owner": "octocat",
    "name": "Hello-World",
    "description": "My first repo",
    "language": "Python",
    "stars": 10,
    "readme": "This is the readme.",
}


class TestParseGithubUrl(unittest.TestCase):

    # checks that a valid github url returns the correct owner and repo
    def test_valid_url(self):
        owner, repo = parse_github_url("https://github.com/octocat/Hello-World")
        self.assertEqual(owner, "octocat")
        self.assertEqual(repo, "Hello-World")

    # checks that a trailing slash is handled correctly
    def test_trailing_slash(self):
        owner, repo = parse_github_url("https://github.com/octocat/Hello-World/")
        self.assertEqual(owner, "octocat")
        self.assertEqual(repo, "Hello-World")

    # checks that an invalid url raises a ValueError
    def test_invalid_url_raises(self):
        with self.assertRaises(ValueError):
            parse_github_url("https://notgithub.com/octocat/Hello-World")


class TestGetRepoInfo(unittest.TestCase):

    # checks that get_repo_info correctly extracts fields from a mocked api response
    @patch("github_client.requests.get")
    def test_extracts_fields_from_response(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            "name": "Hello-World",
            "owner": {"login": "octocat"},
            "description": "My first repo",
            "language": "Python",
            "stargazers_count": 10,
        })
        from github_client import get_repo_info
        result = get_repo_info("octocat", "Hello-World")
        self.assertEqual(result["name"], "Hello-World")
        self.assertEqual(result["owner"], "octocat")
        self.assertEqual(result["stars"], 10)

    # checks that get_readme decodes base64 content to plain text
    @patch("github_client.requests.get")
    def test_readme_decoded_from_base64(self, mock_get):
        import base64
        encoded = base64.b64encode(b"Hello README").decode("utf-8")
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"content": encoded})
        from github_client import get_readme
        result = get_readme("octocat", "Hello-World")
        self.assertEqual(result, "Hello README")


class TestDatabase(unittest.TestCase):

    # points the database to a temp file and creates the table before each test
    def setUp(self):
        import database
        database.DB_NAME = "test_repos.db"
        init_db()

    # deletes the temp database file after each test
    def tearDown(self):
        import os
        if os.path.exists("test_repos.db"):
            os.remove("test_repos.db")

    # checks that a saved repo can be retrieved with the same data
    def test_save_and_get_repo(self):
        save_repo(SAMPLE_DB_REPO)
        result = get_repo("octocat", "Hello-World")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Hello-World")
        self.assertEqual(result["stars"], 10)

    # checks that update_analysis changes only the analysis field
    def test_update_analysis(self):
        save_repo(SAMPLE_DB_REPO)
        update_analysis("octocat", "Hello-World", "Great project!")
        result = get_repo("octocat", "Hello-World")
        self.assertEqual(result["analysis"], "Great project!")


# sample repo data used across multiple tests
SAMPLE_REPO = {
    "repo_name": "SipSafe",
    "owner": "kaylainoa",
    "description": "AI-powered drink safety app",
    "language": "TypeScript",
    "stars": 5,
    "readme": "SipSafe helps you stay safe on a night out.",
}


class TestBuildRepoSummary(unittest.TestCase):

    # checks that all key fields show up in the summary text
    def test_includes_all_fields(self):
        summary = build_repo_summary(SAMPLE_REPO)
        self.assertIn("SipSafe", summary)
        self.assertIn("kaylainoa", summary)
        self.assertIn("TypeScript", summary)
        self.assertIn("AI-powered drink safety app", summary)

    # checks that missing fields fall back to default values
    def test_missing_fields_use_defaults(self):
        summary = build_repo_summary({})
        self.assertIn("Unknown", summary)
        self.assertIn("No description provided", summary)
        self.assertIn("No README available", summary)

    # checks that long READMEs are cut off at 2000 characters
    def test_readme_is_truncated(self):
        long_readme = "x" * 5000
        summary = build_repo_summary({**SAMPLE_REPO, "readme": long_readme})
        self.assertIn("x" * 2000, summary)
        self.assertNotIn("x" * 2001, summary)


class TestGenerateFunctions(unittest.TestCase):

    # checks that generate_nontechnical_explanation returns the AI's response text
    @patch("genai_client.client")
    def test_nontechnical_explanation_returns_text(self, mock_client):
        mock_client.models.generate_content.return_value = MagicMock(text="  Plain English explanation.  ")
        result = generate_nontechnical_explanation(SAMPLE_REPO)
        self.assertEqual(result, "Plain English explanation.")

    # checks that generate_interview_talking_points returns the AI's response text
    @patch("genai_client.client")
    def test_interview_talking_points_returns_text(self, mock_client):
        mock_client.models.generate_content.return_value = MagicMock(text="1. Talking point one.")
        result = generate_interview_talking_points(SAMPLE_REPO)
        self.assertEqual(result, "1. Talking point one.")



class TestDisplayResults(unittest.TestCase):

    # checks that display_results prints all three sections to the terminal
    def test_prints_all_sections(self):
        results = {
            "nontechnical_explanation": "Easy explanation",
            "interview_talking_points": "1. Great point",
            "resume_bullets": "• Built something",
        }
        # patch print so we can capture what gets printed
        with patch("builtins.print") as mock_print:
            display_results("SipSafe", results)
            printed = " ".join(str(c) for c in [call.args for call in mock_print.call_args_list])
            self.assertIn("SipSafe", printed)
            self.assertIn("Easy explanation", printed)
            self.assertIn("Great point", printed)
            self.assertIn("Built something", printed)


class TestAnalyzeRepo(unittest.TestCase):

    # checks that analyze_repo returns a dict with all three expected keys
    @patch("genai_client.generate_resume_bullets", return_value="• Built app")
    @patch("genai_client.generate_interview_talking_points", return_value="1. Point")
    @patch("genai_client.generate_nontechnical_explanation", return_value="Easy explanation")
    @patch("genai_client.display_results")
    def test_returns_correct_keys(self, mock_display, mock_exp, mock_points, mock_bullets):
        results = analyze_repo(SAMPLE_REPO)
        self.assertIn("repo_name", results)
        self.assertIn("nontechnical_explanation", results)
        self.assertIn("interview_talking_points", results)
        self.assertIn("resume_bullets", results)

    # checks that the repo_name in the result matches the input
    @patch("genai_client.generate_resume_bullets", return_value="• Built app")
    @patch("genai_client.generate_interview_talking_points", return_value="1. Point")
    @patch("genai_client.generate_nontechnical_explanation", return_value="Easy explanation")
    @patch("genai_client.display_results")
    def test_repo_name_matches_input(self, mock_display, mock_exp, mock_points, mock_bullets):
        results = analyze_repo(SAMPLE_REPO)
        self.assertEqual(results["repo_name"], "SipSafe")


if __name__ == "__main__":
    unittest.main()
