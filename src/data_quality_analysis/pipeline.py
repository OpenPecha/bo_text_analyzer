import base64
import json
import logging
import random
import re
from pathlib import Path

from botok import WordTokenizer
from botok.config import Config
from github import Github


def find_base_folder(repo, path=""):
    """
    Recursively searches for a directory named 'base' in the GitHub repository.

    Args:
        repo: Repository object from PyGithub.
        path: Current path being searched, defaults to the root of the repository.

    Returns:
        Path to the 'base' directory, or None if not found.
    """
    try:
        contents = repo.get_contents(path)
        for content in contents:
            if content.type == "dir":
                if content.name == "base":  # Check if the directory is named 'base'
                    return content.path  # Return the path if found
                else:
                    # If not, search within this directory
                    base_folder_path = find_base_folder(repo, content.path)
                    if base_folder_path:
                        return base_folder_path
    except Exception as e:
        print(e)
        pass  # Ignore errors and continue searching

    return None  # Return None if 'base' directory is not found


def extract_text_from_large_file(repo, file_sha):
    """
    Retrieves and decodes the content of a large file from a GitHub repository using its SHA identifier.
    Handles base64 encoded content for large files.

    Args:
        repo: GitHub repository object.
        file_sha: SHA identifier of the file's blob.

    Returns:
        Decoded text content of the file as a string or None if an error occurs.
    """
    try:
        # Get the blob from the repository using the file's SHA
        blob = repo.get_git_blob(file_sha)
        # Blob content is base64 encoded, so it needs to be decoded
        content = base64.b64decode(blob.content)
        text = content.decode("utf-8")  # assuming the file is utf-8 encoded
        return text
    except Exception as e:
        print(f"Error in fetching large file content: {e}")
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

        all_results = []  # List to store results of all files

        try:
            # Get the repository within the organization
            repo = org.get_repo(repo_name)

            predefined_base_folder_path = f"{pecha_id}.opf/base"
            try:
                # Attempt to get contents of the predefined base folder
                base_folder_contents = repo.get_contents(predefined_base_folder_path)
            except Exception as e:
                # If the predefined path is not found, search for the base folder
                base_folder_path = find_base_folder(repo)
                if not base_folder_path:
                    print(f"Base folder not found in repository {pecha_id}", e)
                    return []
                base_folder_contents = repo.get_contents(base_folder_path)

            # Filter to keep only text files
            text_files = [
                file
                for file in base_folder_contents
                if file.type == "file" and file.name.endswith(".txt")
            ]

            if text_files:
                # Select one random file (or the only file if there's just one)
                file_content = random.choice(text_files)

                if file_content.size > 1000000:  # If file size is larger than 1MB
                    full_text = extract_text_from_large_file(repo, file_content.sha)
                else:
                    full_text = file_content.decoded_content.decode(
                        "utf-8", errors="replace"
                    )

                # Check for the presence of Tibetan script
                if re.search(r"[\u0F00-\u0FFF]+", full_text):
                    if len(full_text) > 3000:  # Check if shed is present
                        # Split the text into sentences based on the tshek (།)
                        sentences = full_text.split("།")
                        length = 10
                    else:
                        begin = 0
                        end = len(full_text)
                        all_results.append((full_text, file_content.name, begin, end))
                        return all_results
                else:
                    # Handle non-Tibetan text segmentation or other logic
                    sentences = full_text.split(
                        "\n"
                    )  # Example: split on nextline for mandarin
                    length = 5

                # Determine the midsection of the text
                mid_point = len(sentences) // 2
                half_span = min(
                    length, (len(sentences) // 2 + 1)
                )  # Half of 30 or half of total sentences if less

                # Select up to 50 sentences from the midsection
                start_indexs = max(0, mid_point - half_span)
                end_indexs = min(len(sentences), mid_point + half_span)
                selected_sentences = sentences[start_indexs:end_indexs]

                # Join the sentences back with appropriate delimiter
                if re.search(r"[\u0F00-\u0FFF]+", full_text):
                    if len(full_text) > 3000:  # Check if shed is present
                        # Split the text into sentences based on the tshek (།)
                        extracted_text = "།".join(selected_sentences) + "།"
                        start_index = full_text.find(extracted_text)
                        end_index = start_index + len(extracted_text)

                else:
                    extracted_text = "\n".join(selected_sentences) + "\n"
                    start_index, end_index = 0, 0

                all_results.append(
                    (extracted_text, file_content.name, start_index, end_index)
                )

        except Exception as e:
            print(f"Error in accessing repository {repo_name}: {e}")
            return (None, None, None, None)
    except Exception as e:
        print(f"Error in extract_text_from_files: {e}")
        return (None, None, None, None)
    return all_results


def analyze_tokens(wt, text):
    """
    Analyzes and tokenizes provided Tibetan text using WordTokenizer.
    Counts occurrences of non-words and non-bo words.

    Args:
        wt: Instance of WordTokenizer.
        text: Text to tokenize and analyze.

    Returns:
        Tuple with counts of non-words, non-bo words, and total tokens.
    """

    non_word_count = 0
    non_bo_word_count = 0
    tokens = wt.tokenize(text, split_affixes=False)
    total_token = len(tokens)
    for token in tokens:
        if token.pos == "NON_WORD" and not token.skrt:
            non_word_count += 1

        if token.chunk_type in ["LATIN", "CJK", "OTHER"] and (
            token.chunk_type != "OTHER" or not token.skrt
        ):
            non_bo_word_count += 1

    return non_word_count, non_bo_word_count, total_token


def tokenize_text(wt, text, pecha_id, pecha_sub_file, start, end):
    """
    Tokenizes provided text using WordTokenizer and compiles analysis results.

    Args:
        wt: Instance of WordTokenizer.
        text: Text to analyze.
        pecha_id: Identifier of the Pecha.
        pecha_sub_file: Sub-file name in the Pecha.
        start: Starting index of text segment.
        end: Ending index of text segment.

    Returns:
        Dictionary containing analysis results and metadata.
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


def process_pechas(pecha_ids, github_token, organization):
    """
    Processes list of Pecha IDs to extract and analyze text data from GitHub repositories.

    Args:
        pecha_ids: List of Pecha IDs to process.
        github_token: Personal access token for GitHub API.
        organization: Name of GitHub organization.

    Returns:
        Dictionary with Pecha IDs as keys and text analysis results as values.
    """
    results = {}
    wt = WordTokenizer(config=Config(dialect_name="general", base_path=Path.home()))

    for pecha_id in pecha_ids:
        print(f"Processing Pecha ID: {pecha_id}")
        all_results = extract_text_from_files(organization, github_token, pecha_id)

        if all_results is None:
            print(f"No data returned for Pecha ID {pecha_id}")
            continue

        pecha_results = {}  # Dictionary to store results for this pecha
        for result in all_results:
            if result is None:
                continue
            extracted_text, pecha_file_name, start_index, end_index = result

            if extracted_text is not None and pecha_file_name is not None:
                analysis_result = tokenize_text(
                    wt,
                    extracted_text,
                    pecha_id,
                    pecha_file_name,
                    start_index,
                    end_index,
                )
                pecha_results[
                    pecha_file_name
                ] = analysis_result  # Store analysis result for each file

        results[pecha_id] = pecha_results  # Store all file results for this pecha

    return results


def main():
    """
    Main function that initializes configurations, processes Pecha IDs, and saves results to JSON.

    Args:
        None

    Returns:
        None (Outputs are saved to file and logged)
    """
    github_token = "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"
    organization_name = "OpenPecha-Data"

    # Example: List of Pecha IDs to process
    pecha_ids = [
        "I8A764804",
        "O1EB43CCE",
        "I8A764804",
        "I229815A9",
        "IFF5475DD",
        "I84B5FA9B",
        "P000792",
        "I84EB18FB",
        "I0FAA1C40",
        "I20A50BB6",
        "I06324580",
        "IB3BFD2E7",
        "I33D3B96F",
        "I340DE5FA",
        "ICB0FDD9A",
        "ID194E73E",
        "IBF06BC6C",
        "I79C6CCCC",
        "O1EB43CCE",
        "O3C4D0D40",
        "I2E7867A6",
        "I6440520B",
        "P000796",
        "P000815",
        "P000779",
    ]

    # Configure logging
    logging.basicConfig(
        filename="pecha_processing.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )

    results = process_pechas(pecha_ids, github_token, organization_name)

    # Output the results to a JSON file
    output_file = (
        "/home/gangagyatso/Desktop/project4/pechadata_analysis/data/pechas.json"
    )
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()
