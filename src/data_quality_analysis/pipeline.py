import csv
import json
import logging
import random
from pathlib import Path

from botok import WordTokenizer
from botok.config import Config
from github import Github


def select_random_pecha_ids(csv_file_path, num_rows):
    """
    Selects a random set of Pecha IDs from a CSV file.

    Args:
        csv_file_path (str): Path to the CSV file containing Pecha IDs.
        num_rows (int): Number of random IDs to select.

    Returns:
        list: A list of randomly selected Pecha IDs.
    """
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
    """
    Extracts a specific range of text from files in a GitHub repository.

    Args:
        organization (str): Name of the GitHub organization.
        github_token (str): Personal access token for GitHub API.
        pecha_id (str): Identifier of the Pecha in the repository.

    Returns:
        tuple: Extracted text, file name, start index, end index of the extracted text.
               Returns None for each if no files are processed or an error occurs.
    """
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
                    text_length = len(full_text)

                    if (text_length / 2 - text_length / 4) <= 500 and text_length > 0:
                        start_offset = text_length / 2 - text_length / 4
                        end_offset = text_length / 2 + text_length / 4
                    elif text_length == 0:
                        start_offset = 0
                        end_offset = 0
                    else:
                        start_offset = text_length / 2 - 500
                        end_offset = text_length / 2 + 500

                    # Extract the desired text range
                    start = int(start_offset)
                    end = int(end_offset)
                    extracted_text = full_text[start:end]

                    return extracted_text, file_content.name, start, end
            # Return None values if no files are processed
            return None, None, None, None

        except Exception as e:
            print(f"Error in accessing repository {repo_name}: {e}")
            return None, None, None, None
    except Exception as e:
        print(f"Error in extract_text_from_files: {e}")
        return None, None, None, None


def select_files(base_folder_contents):
    """
    Selects a number of text files from the contents of a base folder.

    Args:
        base_folder_contents (list): List of file contents from the base folder.

    Returns:
        list: Selected text files for processing.
    """
    text_files = [
        f for f in base_folder_contents if f.type == "file" and f.name.endswith(".txt")
    ]
    num_files = 3 if len(text_files) > 5 else 1
    return random.sample(text_files, min(num_files, len(text_files)))


def analyze_tokens(wt, text):
    """
    Analyzes the tokens in a given text to count non-words and non-bo words.

    Args:
        wt (WordTokenizer): Instance of WordTokenizer.
        text (str): Text to be tokenized and analyzed.

    Returns:
        tuple: Counts of non-words, non-bo words, and total tokens.
    """
    non_word_count = 0
    non_bo_word_count = 0
    tokens = wt.tokenize(text, split_affixes=False)
    total_token = len(tokens) - 2
    for token in tokens[1:-1]:
        if token.pos == "NON_WORD" and not token.skrt:
            non_word_count += 1

        if token.chunk_type in ["LATIN", "CJK", "OTHER"] and (
            token.chunk_type != "OTHER" or not token.skrt
        ):
            non_bo_word_count += 1

    return non_word_count, non_bo_word_count, total_token


def tokenize_text(wt, text, pecha_id, pecha_sub_file, start, end):
    """
    Tokenizes the text and performs analysis to count non-words and non-bo words.

    Args:
        wt (WordTokenizer): Instance of WordTokenizer.
        text (str): Text to be tokenized and analyzed.
        pecha_id (str): Identifier of the Pecha.
        pecha_sub_file (str): Name of the sub-file in the Pecha.
        start (int): Starting index of the text segment.
        end (int): Ending index of the text segment.

    Returns:
        dict: A dictionary containing analysis results and metadata.
    """
    if not text.strip():
        # Check if the text is empty or contains only whitespace
        logging.info(f"Empty file: {pecha_id}-{pecha_sub_file}")
        return {}

    non_word_count, non_bo_word_count, total_word_count = analyze_tokens(wt, text)

    return {
        "base_text": pecha_sub_file,
        "character_start": start,
        "character_end": end,
        "total_word_count": total_word_count,
        "non_word_count": non_word_count,
        "non_bo_word_count": non_bo_word_count,
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

    wt = WordTokenizer(config=config)
    # Create a dictionary to store results
    results = {}
    # Example usage:
    csv_file_path = "../../data/opf_catalog.csv"
    num_rows_to_select = 50

    selected_pecha_ids = select_random_pecha_ids(csv_file_path, num_rows_to_select)
    if selected_pecha_ids:
        print("Randomly selected Pecha IDs:")
        for pecha_id in selected_pecha_ids:
            print(pecha_id)
            (
                extracted_text,
                pecha_file_name,
                start_index,
                end_index,
            ) = extract_text_from_files(organization_name, github_token, pecha_id)
            if extracted_text is not None and pecha_file_name is not None:
                nonword_dict = tokenize_text(
                    wt,
                    extracted_text,
                    pecha_id,
                    pecha_file_name,
                    start_index,
                    end_index,
                )
                base_id = f"{pecha_file_name.split('.')[0]}"
                results[f"{pecha_id}"] = {f"{base_id}": nonword_dict}

        # Specify the file name where the JSON data will be written
        file_name = "../../data/pecha_data.json"

        # Writing the dictionary to a JSON file
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)

        print(f"Data written to {file_name}")

    else:
        print("No Pecha IDs were selected.")
