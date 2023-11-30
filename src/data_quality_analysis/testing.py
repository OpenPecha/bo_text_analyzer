from pathlib import Path

from botok import TSEK, Chunks, WordTokenizer
from botok.config import Config
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0  # To make language detection more deterministic


def detect_languages_in_text(text):
    if not text.strip():
        return []

    # Initialize a set to hold unique languages
    language_set = set()

    # Splitting the text into sentences for language detection
    for sentence in text.split("\n"):
        try:
            lang = detect(sentence.strip())
            language_set.add(lang)
        except Exception as e:
            print("detecction error ", e)  # Ignore errors in language detection

    # Convert the set of languages to a list
    return list(language_set)


def get_tokens(wt, text):
    tokens = wt.tokenize(text, split_affixes=False)
    return tokens


if __name__ == "__main__":
    config = Config(dialect_name="general", base_path=Path.home())
    wt = WordTokenizer(config=config)
    text = "ལ་་ལ་ལ་ལ\n་ལ་བ་ཡོད\n།\ni am here\n斷般若波羅蜜"
    detected_languages = detect_languages_in_text(text)
    c = Chunks(text)
    chunks = c.make_chunks()
    non_word_count = 0
    ocr_error = 0
    affixed_count = 0
    punc_count = 0
    tokens = get_tokens(wt, text)
    for token in tokens:

        print(token)

        # Replace newline characters in token.text with a space
        cleaned_token_text = token.text.replace("\n", "")
        print(cleaned_token_text)

        if token.chunk_type == "PUNCT":
            punc_count += 1
            continue

        if cleaned_token_text != token.text_cleaned:
            ocr_error += 1
            if cleaned_token_text + TSEK == token.text_cleaned:
                ocr_error -= 1
                continue
            print(cleaned_token_text, token.text_cleaned)

        if token.pos == "NON_WORD":
            non_word_count += 1

        if cleaned_token_text != token.text_unaffixed:
            val = token.senses
            if val and val[0].get("affixed"):
                affixed_count += 1

    print(
        ocr_error,
        non_word_count,
        affixed_count,
        punc_count,
        len(chunks),
        len(text),
        cleaned_token_text,
        detected_languages,
    )
