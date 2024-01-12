import json

from bo_text_analyzer.plain_text_analyzer import PlainTextAnalyzer


def main():

    plain_text_analyzer = PlainTextAnalyzer(
        non_word_threshold=0.05,
        no_bo_word_threshold=0.03,
        file_path="/home/gangagyatso/Desktop/project8/bo_text_analyzer/data/text_file.txt",
    )
    plain_text_analyzer.analyze()

    print(
        json.dumps(plain_text_analyzer.get_text_report(), indent=4, ensure_ascii=False)
    )


if __name__ == "__main__":
    main()
