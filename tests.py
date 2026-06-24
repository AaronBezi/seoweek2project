import unittest
from unittest.mock import MagicMock, patch
from genai_client import (
    build_repo_summary,
    generate_nontechnical_explanation,
    generate_interview_talking_points,
    generate_resume_bullets,
    display_results,
    analyze_repo,
)

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
