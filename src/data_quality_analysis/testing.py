from pathlib import Path

from botok import TSEK, Chunks, WordTokenizer
from botok.config import Config


def get_tokens(wt, text):
    tokens = wt.tokenize(text, split_affixes=False)
    return tokens


if __name__ == "__main__":
    config = Config(dialect_name="general", base_path=Path.home())
    wt = WordTokenizer(config=config)
    text = "ལ་་ལ་ལ་ལ་ལ་བ་ཡོད།"
    c = Chunks(text)
    chunks = c.make_chunks()
    non_word_count = 0
    ocr_error = 0
    affixed_count = 0
    punc_count = 0
    tokens = get_tokens(wt, text)
    for token in tokens:
        print(token)
        if token.chunk_type == "PUNCT":
            punc_count += 1
            continue
        if token.text != token.text_cleaned:
            ocr_error += 1
            if token.text + TSEK == token.text_cleaned:
                ocr_error -= 1
                continue
            print(token.text, token.text_cleaned)
        if token.pos == "NON_WORD":
            non_word_count += 1
        if token.text != token.text_unaffixed:
            val = token.senses
            if val[0]["affixed"] is True:
                affixed_count += 1
    print(ocr_error, non_word_count, affixed_count, punc_count, len(chunks), len(text))
