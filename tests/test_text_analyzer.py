from bo_text_analyzer.text_analyzer import TextAnalyzer


def test_count_non_words():
    text = "abdul kalamའཁྱེད་ལ་སུན་པོ་ཀཟོས་པར་དགོངས་དག་ཞུ་ཨུམ་ཨུམ་་་། ()$%322 ༣༢༢་�� 你好吗 कैसे ཨོཾ་མ་ཎི་པདྨེ་ཧཱུྃ"
    expected_non_word_count = 4
    ta = TextAnalyzer(non_word_threshold=0.05, no_bo_word_threshold=0.03)
    tokens = ta.tokenize_text(text)
    actual_non_word_count = ta.count_non_words(tokens)
    assert expected_non_word_count == actual_non_word_count, "Non-word count mismatch"


def test_count_non_bo_words():
    text = "abdul kalamའཁྱེད་ལ་སུན་པོ་ཀཟོས་པར་དགོངས་དག་ཞུ་ཨུམ་ཨུམ་་་། ()$%322 ༣༢༢་�� 你好吗 कैसे ཨོཾ་མ་ཎི་པདྨེ་ཧཱུྃ"
    expected_non_bo_word_count = 5
    ta = TextAnalyzer(non_word_threshold=0.05, no_bo_word_threshold=0.03)
    tokens = ta.tokenize_text(text)
    actual_non_bo_word_count = ta.count_non_bo_words(tokens)
    assert (
        expected_non_bo_word_count == actual_non_bo_word_count
    ), "Non-Bo word count mismatch"
