import json
import logging
import re
from pathlib import Path

from botok import WordTokenizer
from botok.config import Config
from github import Github


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

            # Iterate through the contents and process text files
            for file_content in base_folder_contents:
                if file_content.type == "file" and file_content.name.endswith(".txt"):
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
                            return full_text, file_content.name, begin, end

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
                        if "།" in full_text:  # Check if shed is present
                            # Split the text into sentences based on the tshek (།)
                            extracted_text = "།".join(selected_sentences) + "།"
                        else:
                            # If shed is not present, use tsek (་) for segmentation
                            extracted_text = "་".join(selected_sentences) + "་"
                    else:
                        extracted_text = "\n".join(selected_sentences) + "\n"

                    # Calculate start and end indices of the extracted text
                    if extracted_text:
                        start_index = full_text.find(extracted_text)
                        end_index = start_index + len(extracted_text)
                    else:
                        start_index, end_index = 0, 0

                    return extracted_text, file_content.name, start_index, end_index

            # Return None values if no files are processed
            return None, None, None, None

        except Exception as e:
            print(f"Error in accessing repository {repo_name}: {e}")
            return None, None, None, None
    except Exception as e:
        print(f"Error in extract_text_from_files: {e}")
        return None, None, None, None


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


def process_pechas(pecha_ids, github_token, organization):
    results = {}
    wt = WordTokenizer(config=Config(dialect_name="general", base_path=Path.home()))

    for pecha_id in pecha_ids:
        print(pecha_id)
        (
            extracted_text,
            pecha_file_name,
            start_index,
            end_index,
        ) = extract_text_from_files(organization, github_token, pecha_id)

        if extracted_text is not None and pecha_file_name is not None:
            analysis_result = tokenize_text(
                wt, extracted_text, pecha_id, pecha_file_name, start_index, end_index
            )
            results[pecha_id] = analysis_result

    return results


def main():
    github_token = "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"
    organization_name = "OpenPecha-Data"

    # Example: List of Pecha IDs to process
    pecha_ids = [
        "I2E7867A6",
        "I6440520B",
        "P000796",
        "P000815",
        "P000779",
        "P000792",
        "I84B5FA9B",
        "I84EB18FB",
        "I0FAA1C40",
        "I229815A9",
        "IFF5475DD",
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
        "/home/gangagyatso/Desktop/project4/pechadata_analysis/data/practise.json"
    )
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()
