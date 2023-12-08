from pathlib import Path

from botok import WordTokenizer
from botok.config import Config

from data_quality_analysis.pipeline import analyze_tokens


def test_analyze_tokens():
    """
    Test function for 'analyze_tokens' to validate its accuracy.

    This test uses a predefined text with a mix of different scripts and characters.
    It then asserts whether the 'analyze_tokens' function correctly counts the number
    of non-words, non-bo words, and the total number of tokens in the text.
    """
    # Configuration for the WordTokenizer
    config = Config(dialect_name="general", base_path=Path.home())
    wt = WordTokenizer(config=config)

    # Test text with known non-word, non-bo word, and total token counts
    text = "abdul kalamའཁྱེད་ལ་སུན་པོ་ཀཟོས་པར་དགོངས་དག་ཞུ་ཨུམ་ཨུམ་་་། ()$%322 ༣༢༢་�� 你好吗 कैसे ཨོཾ་མ་ཎི་པདྨེ་ཧཱུྃ"
    expected_non_word = 4
    expected_bo_non_word = 5
    expected_total_token = 20

    # Analyze the tokens and get counts
    a, b, c = analyze_tokens(wt, text)

    # Assert that the actual counts match the expected counts
    assert expected_non_word == a, "Non-word count mismatch"
    assert expected_bo_non_word == b, "Non-bo word count mismatch"
    assert expected_total_token == c, "Total token count mismatch"
