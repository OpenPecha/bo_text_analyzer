from pathlib import Path

from botok import WordTokenizer
from botok.config import Config


class TextAnalyzer:
    def __init__(self, preminum_threshold):
        self.text = {}
        self.text_report = {}
        self.preminum_threshold = preminum_threshold

    def get_text(self):
        pass

    def tokenize_text(self, text):
        wt = WordTokenizer(config=Config(dialect_name="general", base_path=Path.home()))
        tokens = wt.tokenize(text, split_affixes=False)
        return tokens

    def count_non_words(self, tokens):
        non_word_count = 0
        for token in tokens:
            if token.pos == "NON_WORD" and not token.skrt:
                non_word_count += 1
        return non_word_count

    def count_non_bo_words(self, tokens):
        non_bo_word_count = 0
        for token in tokens:
            if token.chunk_type in ["LATIN", "CJK", "OTHER"] and (
                token.chunk_type != "OTHER" or not token.skrt
            ):
                non_bo_word_count += 1
        return non_bo_word_count

    def check_is_preminum(self, non_word_percentage, non_bo_word_percentage):
        if (
            non_word_percentage > self.preminum_threshold
            or non_bo_word_percentage > self.preminum_threshold
        ):
            return False
        return True

    def analyze(self):
        self.text = self.get_text()
        for text_file_name, text in self.text.items():
            cur_file_report = {}
            tokens = self.tokenize_text(text)
            total_words = len(tokens)
            total_non_words = self.count_non_words(tokens)
            total_non_bo_words = self.count_non_bo_words(tokens)
            non_word_percentage = total_non_words / total_words
            non_bo_word_percentage = total_non_bo_words / total_words
            is_premium = self.check_is_preminum(
                non_word_percentage, non_bo_word_percentage
            )

            cur_file_report["total_words"] = total_words
            cur_file_report["total_non_words"] = total_non_words
            cur_file_report["total_non_bo_words"] = total_non_bo_words
            cur_file_report["non_word_percentage"] = non_word_percentage
            cur_file_report["non_bo_word_percentage"] = non_bo_word_percentage
            cur_file_report["is_premium"] = is_premium
            self.text_report[text_file_name] = cur_file_report
