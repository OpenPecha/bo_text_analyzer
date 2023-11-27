import csv
import json
import logging
import random
import re
from pathlib import Path

from botok import TSEK, Chunks, WordTokenizer
from botok.config import Config
from github import Github


def select_random_pecha_ids(csv_file_path, num_rows):
    try:
        selected_pecha_ids = []

        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            all_rows = list(csv_reader)

            # Check if the number of rows requested is greater than the total number of rows
            if num_rows > len(all_rows):
                num_rows = len(all_rows)

            # Randomly select num_rows from the list of all rows
            selected_rows = random.sample(all_rows, num_rows)

            # Extract the Pecha IDs from the selected rows
            for row in selected_rows:
                pecha_id = row["Pecha ID"].strip()
                selected_pecha_ids.append(pecha_id)

        return selected_pecha_ids  # Ensure that the list of Pecha IDs is returned
    except Exception as e:
        print(f"Error in select_random_pecha_ids: {e}")
        return None


def extract_text_from_files(organization, github_token, pecha_id):
    try:
        # Initialize the PyGithub client with your token
        g = Github(github_token)

        # Get the organization
        org = g.get_organization(organization)

        repo_name = pecha_id

        try:
            # Get the repository within the organization
            repo = org.get_repo(repo_name)

            # Construct the base folder path within the repository
            base_folder_path = f"{pecha_id}.opf/base"

            # Get the contents of the base folder
            base_folder_contents = repo.get_contents(base_folder_path)
            # Implementing the new file selection logic
            files_to_process = select_files(base_folder_contents)

            # Iterate through the contents and process text files
            for file_content in files_to_process:
                if file_content.type == "file" and file_content.name.endswith(".txt"):
                    # Decode the content to get the text
                    full_text = file_content.decoded_content.decode(
                        "utf-8", errors="replace"
                    )
                    if (len(full_text) / 2 - len(full_text) / 4) <= 500 and len(
                        full_text
                    ) > 0:
                        start_offset = len(full_text) / 2 - len(full_text) / 4
                        end_offset = len(full_text) / 2 + len(full_text) / 4
                    elif len(full_text) == 0:
                        start_offset = 0
                        end_offset = 0
                    else:
                        start_offset = len(full_text) / 2 - 500
                        end_offset = len(full_text) / 2 + 500

                    # Extract the desired text range
                    start = int(start_offset)
                    end = int(end_offset)
                    extracted_text = full_text[start:end]

                return extracted_text, file_content.name
            # Return None values if no files are processed
            return None, None

        except Exception as e:
            print(f"Error in accessing repository {repo_name}: {e}")
        return None, None
    except Exception as e:
        print(f"Error in extract_text_from_files: {e}")


def select_files(base_folder_contents):
    text_files = [
        f for f in base_folder_contents if f.type == "file" and f.name.endswith(".txt")
    ]
    num_files = 3 if len(text_files) > 5 else 1
    return random.sample(text_files, min(num_files, len(text_files)))


def tokenize_text(text, pecha_id, pecha_sub_file):
    if not text.strip():
        # Check if the text is empty or contains only whitespace
        logging.info(f"Empty file: {pecha_id}-{pecha_sub_file}")
        return {
            "NON_WORD": "NOT APPLICBLE",
            "TOTAL_TOKENS": "NOT APPLICABLE",
            "OCR_ERROR_COUNT": "NOT APPLICABLE",
            "TEXT_QUALITY": "NOT APPLICABLE",  # Assign a quality label
            "ERROR_LOCATIONS": "NOT APPLICABLE",  # Empty list for error locations
            "LANGUAGE": "NOT APPLICABLE",
            "CHUNK_SIZE": "NOT APPLICABLE",
            "CHARACTER_COUNT": "NOT APPLICABLE",
            "AFFIXED_WORD_COUNT": "NOT APPLICABLE",
        }  # Return a dictionary with "NON_WORD" and 0 count

    if not tibetan_regex.search(text):  # Check if the text contains Tibetan characters
        cjk_regex = re.compile(r"[\u2e80-\ufaff\ufe30-\ufe4f\u20000-\u2fa1f]+")
        latin_regex = re.compile(r"[\u0020-\u036f\u1e00-\u20cf]+")
        if cjk_regex.search(text):
            lang = "CJK"
        elif latin_regex.search(text):
            lang = "LATIN"
        else:
            lang = "OTHER"
        logging.info(f"Skipped non-Tibetan file: {pecha_id}-{pecha_sub_file}")
        return {
            "NON_WORD": "NOT APPLICBLE",
            "TOTAL_TOKENS": "NOT APPLICABLE",
            "OCR_ERROR_COUNT": "NOT APPLICABLE",
            "TEXT_QUALITY": "NOT APPLICABLE",  # Assign a quality label
            "OCR_ERROR_LOCATIONS": "NOT APPLICABLE",
            "LANGUAGE": lang,
            "CHUNK_SIZE": "NOT APPLICABLE",
            "CHARACTER_COUNT": "NOT APPLICABLE",
            "AFFIXED_WORD_COUNT": "NOT APPLICABLE",
        }  # Return a dictionary with "NON_WORD" and 0 count

    tokens = wt.tokenize(text, split_affixes=False)
    ocr_error = 0
    nonword_count = 0
    nonword_text = []
    affixed_count = 0
    error_locations = []
    c = Chunks(text)
    chunks = c.make_chunks()
    error_index = 0  # Add this variable to track the index in the original text
    for i, token in enumerate(tokens[1:-1], start=1):
        if token.chunk_type == "PUNCT":
            continue
        if token.pos == "NON_WORD":
            nonword_text.append(token.text)
            nonword_count += 1
        if token.text != token.text_cleaned:
            ocr_error += 1
            # Append the error index in the original text
            error_index += text[error_index:].find(token.text)
            error_locations.append((error_index, error_index + len(token.text)))
            if token.text + TSEK == token.text_cleaned:
                ocr_error -= 1
                error_locations.remove((error_index, error_index + len(token.text)))
                continue
        if token.text != token.text_unaffixed:
            val = token.senses
            if val is not None and "affixed" in val[0] and val[0]["affixed"] is True:
                affixed_count += 1
    ocr_error_ratio = ocr_error / (len(tokens) - 2)
    # Determine text quality based on criteria (you can customize this)
    text_quality = (
        "Excellent"
        if ocr_error_ratio < 0.001 and nonword_count == 0
        else "Good"
        if ocr_error_ratio < 0.020
        else "Fair"
        if ocr_error_ratio < 0.040
        else "Poor"
    )

    return {
        "NON_WORD": nonword_count,
        "NON_WORD_TEXT": nonword_text,
        "TOTAL_TOKENS": len(tokens) - 2,
        "OCR_ERROR_COUNT": ocr_error,
        "OCR_ERROR_COUNT_RATIO": ocr_error_ratio,
        "TEXT_QUALITY": text_quality,
        "OCR_ERROR_LOCATIONS": error_locations,
        "LANGUAGE": "TIBETAN",
        "CHUNK_SIZE": len(chunks),
        "CHARACTER_COUNT": len(text),
        "AFFIXED_WORD_COUNT": affixed_count,
    }


if __name__ == "__main__":
    # Your GitHub personal access token (replace with your actual token)
    github_token = "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"
    # Example usage:
    organization_name = "OpenPecha-Data"
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
    # Create a dictionary to store results
    results = {}
    # Example usage:
    csv_file_path = (
        "/home/gangagyatso/Desktop/project4/pechadata_analysis/data/opf_catalog.csv"
    )
    num_rows_to_select = 5

    selected_pecha_ids = select_random_pecha_ids(csv_file_path, num_rows_to_select)
    if selected_pecha_ids:
        print("Randomly selected Pecha IDs:")
        for pecha_id in selected_pecha_ids:
            print(pecha_id)
            extracted_text, pecha_file_name = extract_text_from_files(
                organization_name, github_token, pecha_id
            )
            if extracted_text is not None and pecha_file_name is not None:
                nonword_dict = tokenize_text(extracted_text, pecha_id, pecha_file_name)
                results[f"{pecha_id}-{pecha_file_name}"] = nonword_dict

        cnt = 0
        # Print the results dictionary
        for file_name, nonword_dict in results.items():
            cnt = cnt + 1
            print(cnt, f"File: {file_name}")
            print(f"Non-word Count: {nonword_dict['NON_WORD']}")
            print(f"TOKEN COUNT TOTAL: {nonword_dict['TOTAL_TOKENS']}")
            print(f"OCR_ERROR_COUNT: {nonword_dict['OCR_ERROR_COUNT']}")
        # Specify the file name where the JSON data will be written
        file_name = "../../data/pecha_data.json"

        # Writing the dictionary to a JSON file
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)

        print(f"Data written to {file_name}")

    else:
        print("No Pecha IDs were selected.")
