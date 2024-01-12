import json
import os

from bo_text_analyzer.opf_analyzer import OpfAnalyzer


def main():
    # Set environment variables
    os.environ["GITHUB_TOKEN"] = "personal_access_token"
    os.environ["OPENPECHA_DATA_GITHUB_ORG"] = "OpenPecha-Data"
    os.environ["GITHUB_USERNAME"] = "github_username"
    # Set the pecha ID and premium threshold
    pecha_id = "IFF5475DD"

    # Create an instance of OpfAnalyzer
    opf_analyzer = OpfAnalyzer(
        non_word_threshold=0.05, no_bo_word_threshold=0.03, opf_id=pecha_id
    )

    # Fetch and analyze the texts
    opf_analyzer.analyze()

    # Output the analysis results
    print(json.dumps(opf_analyzer.get_opf_report(), indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
