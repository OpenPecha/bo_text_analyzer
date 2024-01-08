import os

from bo_text_analyzer.opf_analyzer import OpfAnalyzer


def main():
    # Set environment variables
    os.environ["GITHUB_TOKEN"] = "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"
    os.environ["OPENPECHA_DATA_GITHUB_ORG"] = "OpenPecha-Data"
    os.environ["GITHUB_USERNAME"] = "gangagyatso4364"
    # Set the pecha ID and premium threshold
    pecha_id = "I229815A9"
    premium_threshold = 0.05

    # Create an instance of OpfAnalyzer
    opf_analyzer = OpfAnalyzer(premium_threshold, pecha_id)

    # Fetch and analyze the texts
    opf_analyzer.analyze()

    # Output the analysis results
    print(opf_analyzer.get_opf_report())


if __name__ == "__main__":
    main()
