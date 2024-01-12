import os

from bo_text_analyzer.opf_analyzer import OpfAnalyzer

# Fetch environment variables
github_token = os.getenv("GITHUB_TOKEN")
openpecha_data_github_org = os.getenv("OPENPECHA_DATA_GITHUB_ORG")
github_username = os.getenv("GITHUB_USERNAME")

# Ensure that the necessary environment variables are set
assert github_token is not None, "GITHUB_TOKEN is not set"
assert openpecha_data_github_org is not None, "OPENPECHA_DATA_GITHUB_ORG is not set"
assert github_username is not None, "GITHUB_USERNAME is not set"

pecha_id = "IFF5475DD"


def test_analyze():
    expected_report = {
        "IFF5475DD": {
            "C07B": {
                "total_words": 4168,
                "total_non_words": 548,
                "total_non_bo_words": 109,
                "non_word_percentage": 0.13147792706333974,
                "non_bo_word_percentage": 0.026151631477927064,
                "is_premium": False,
                "start": 591,
                "end": 20495,
            }
        }
    }
    opf_obj = OpfAnalyzer(
        non_word_threshold=0.05,
        no_bo_word_threshold=0.03,
        opf_id=pecha_id,
    )
    opf_obj.analyze()
    actual_report = opf_obj.get_opf_report()

    assert expected_report == actual_report, "Report mismatch"
