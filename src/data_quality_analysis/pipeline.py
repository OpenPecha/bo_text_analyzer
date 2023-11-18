import csv
import json
import logging
import random
import re
from pathlib import Path

from botok import WordTokenizer
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
            "NON_WORD": "EMPTY FILE",
            "TOTAL_TOKENS": 0,
        }  # Return a dictionary with "NON_WORD" and 0 count

    if not tibetan_regex.search(text):  # Check if the text contains Tibetan characters
        logging.info(f"Skipped non-Tibetan file: {pecha_id}-{pecha_sub_file}")
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
    csv_file_path = "../../data/opf_catalog.csv"
    num_rows_to_select = 10

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
        # Specify the file name where the JSON data will be written
        file_name = "../../data/pecha_data.json"

        # Writing the dictionary to a JSON file
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)

        print(f"Data written to {file_name}")

    else:
        print("No Pecha IDs were selected.")
