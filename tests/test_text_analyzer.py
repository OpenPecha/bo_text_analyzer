from bo_text_analyzer.text_analyzer import TextAnalyzer

text = "abdul kalamའཁྱེད་ལ་སུན་པོ་ཀཟོས་པར་དགོངས་དག་ཞུ་ཨུམ་ཨུམ་་་། ()$%322 ༣༢༢་�� 你好吗 कैसे ཨོཾ་མ་ཎི་པདྨེ་ཧཱུྃ"
ta = TextAnalyzer(non_word_threshold=0.05, no_bo_word_threshold=0.03)
tokens = ta.tokenize_text(text)
total_words = len(tokens)


def test_count_non_words():
    expected_non_word_count = 4
    actual_non_word_count = ta.count_non_words(tokens)
    assert expected_non_word_count == actual_non_word_count, "Non-word count mismatch"


def test_count_non_bo_words():
    expected_non_bo_word_count = 5
    actual_non_bo_word_count = ta.count_non_bo_words(tokens)
    assert (
        expected_non_bo_word_count == actual_non_bo_word_count
    ), "Non-Bo word count mismatch"


def test_is_premium():
    expected_is_premium = False
    non_word_percentage = ta.count_non_words(tokens) / total_words
    non_bo_word_percentage = ta.count_non_bo_words(tokens) / total_words
    actual_is_premium = ta.check_is_preminum(
        non_word_percentage, non_bo_word_percentage
    )
    assert expected_is_premium == actual_is_premium, "Premium check mismatch"
