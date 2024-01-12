from pathlib import Path

from botok import WordTokenizer
from botok.config import Config


class TextAnalyzer:
    def __init__(self, non_word_threshold, no_bo_word_threshold):
        self.text_report = {}
        self.non_word_preminum_threshold = non_word_threshold
        self.non_bo_word_preminum_threshold = no_bo_word_threshold

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
            non_word_percentage > self.non_word_preminum_threshold
            or non_bo_word_percentage > self.non_bo_word_preminum_threshold
        ):
            return False
        return True

    def trim_text(self, tokens, text_obj, file_name):
        # Get the full text
        text = text_obj.texts[file_name]
        # Calculate the token indices for 25% and 75% of the text
        start_token_index = int(len(tokens) * 0.25)
        end_token_index = int(len(tokens) * 0.75)

        if start_token_index < len(tokens) and end_token_index < len(tokens):
            # Get the character index of these tokens in the full text
            start_char_index = tokens[start_token_index].start
            end_char_index = tokens[end_token_index].start + tokens[end_token_index].len

            # Extract the trimmed text
            trimmed_text = text[start_char_index:end_char_index]
            last_token = end_token_index + 1
            trimmed_tokens = tokens[start_token_index:last_token]

            # Update text_obj
            text_obj.texts[file_name] = trimmed_text
            text_obj.start = start_char_index
            text_obj.end = end_char_index
        else:
            # If the calculated indices are out of range, handle the case appropriately
            print("Calculated token indices are out of the range of the token list.")
        return trimmed_tokens, text_obj

    def analyze(self):
        text_objs = self.get_text()
        for text_obj in text_objs:
            for text_file_name, text in text_obj.texts.items():
                cur_file_report = {}
                tokens = self.tokenize_text(text)
                if text_obj.start == 0 and text_obj.end == -1:
                    if len(tokens) > 1500:
                        tokens, text_obj = self.trim_text(
                            tokens, text_obj, text_file_name
                        )
                    else:
                        text_obj.start = 0
                        text_obj.end = len(text)
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
                cur_file_report["start"] = text_obj.start
                cur_file_report["end"] = text_obj.end
                self.text_report[text_file_name] = cur_file_report
