from pathlib import Path

from botok import TSEK, WordTokenizer
from botok.config import Config


def get_tokens(wt, text):
    tokens = wt.tokenize(text, split_affixes=False)
    return tokens


if __name__ == "__main__":
    config = Config(dialect_name="general", base_path=Path.home())
    wt = WordTokenizer(config=config)
    text = "ལ་ལ་ལ་་ལ་ལ་ལ་བ་ཡོད།106svsf"
    tokens = get_tokens(wt, text)
    for token in tokens:
        print(token)
        if token.chunk_type == "PUNCT":
            continue
        if token.text != token.text_cleaned:
            if token.text + TSEK == token.text_cleaned:
                continue
            print(token.text, token.text_cleaned)
