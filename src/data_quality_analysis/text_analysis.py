import glob
import logging
import os
import re
from pathlib import Path

from botok import WordTokenizer
from botok.config import Config


def tokenize_text_from_file(file_path):
    with open(file_path, encoding="utf-8") as file:
        text = file.read()
        if not text.strip():
            # Check if the text is empty or contains only whitespace
            logging.info(f"Empty file: {file_path}")
            return {
                "NON_WORD": "EMPTY FILE",
                "TOTAL_TOKENS": 0,
            }  # Return a dictionary with "NON_WORD" and 0 count

        if not tibetan_regex.search(
            text
        ):  # Check if the text contains Tibetan characters
            logging.info(f"Skipped non-Tibetan file: {file_path}")
            return {
                "NON_WORD": "NOT TIBETAN",
                "TOTAL_TOKENS": 0,
            }  # Return a dictionary with "NON_WORD" and 0 count

        tokens = wt.tokenize(text, split_affixes=False)

        nonword_count = 0
        for token in tokens[1:-1]:
            if token.pos == "NON_WORD":
                nonword_count += 1

        return {"NON_WORD": nonword_count, "TOTAL_TOKENS": len(tokens) - 2}


if __name__ == "__main__":
    # Configure the logging settings
    logging.basicConfig(
        filename="empty_files.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )
    # Configure the botok settings
    config = Config(dialect_name="general", base_path=Path.home())
    # Regular expression to match Tibetan characters
    tibetan_regex = re.compile(r"[\u0F00-\u0FFF]+")
    wt = WordTokenizer(config=config)
    # Specify the directory containing text files
    text_files_directory = "../../data/output1"

    # Create a dictionary to store results
    results = {}

    # List all text files in the directory
    text_files = glob.glob(os.path.join(text_files_directory, "*.txt"))

    for text_file in text_files:
        nonword_dict = tokenize_text_from_file(text_file)
        results[os.path.basename(text_file)] = nonword_dict
    cnt = 0
    # Print the results dictionary
    for file_name, nonword_dict in results.items():
        cnt = cnt + 1
        print(cnt, f"File: {file_name}")
        print(f"Non-word Count: {nonword_dict['NON_WORD']}")
        print(f"TOKEN COUNT TOTAL: {nonword_dict['TOTAL_TOKENS']}")
0
