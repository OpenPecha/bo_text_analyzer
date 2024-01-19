import json

from bo_text_analyzer.opf_analyzer import OpfAnalyzer


def main():
    # Set the pecha ID and premium threshold
    pecha_id = "P000001"

    # Create an instance of OpfAnalyzer
    opf_analyzer = OpfAnalyzer(
        non_word_threshold=0.05,
        no_bo_word_threshold=0.03,
        opf_id=pecha_id,
        opf_path="/home/gangagyatso/.openpecha/pechas/P000001",
    )

    # Fetch and analyze the texts
    opf_analyzer.analyze()

    # Output the analysis results
    print(json.dumps(opf_analyzer.get_opf_report(), indent=4, ensure_ascii=False))

    output_filename = (
        "/home/gangagyatso/Desktop/project8/bo_text_analyzer/data/p000001.json"
    )

    # Write the analysis results to the file
    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(opf_analyzer.get_opf_report(), file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
