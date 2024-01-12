from bo_text_analyzer.plain_text_analyzer import PlainTextAnalyzer


def test_analyze():
    expected_report = {
        "text_file.txt": {
            "total_words": 20,
            "total_non_words": 4,
            "total_non_bo_words": 5,
            "non_word_percentage": 0.2,
            "non_bo_word_percentage": 0.25,
            "is_premium": False,
            "start": 0,
            "end": 100,
        }
    }
    pt_obj = PlainTextAnalyzer(
        non_word_threshold=0.05,
        no_bo_word_threshold=0.03,
        file_path="./data/text_file.txt",
    )
    pt_obj.analyze()
    actual_report = pt_obj.get_text_report()

    assert expected_report == actual_report, "Report mismatch"
