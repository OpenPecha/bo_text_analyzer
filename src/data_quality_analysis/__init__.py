import csv

from github import Github

# GitHub repository information
repository_url = "https://github.com/OpenPecha-Data/"
file_path = "catalog/opf_catalog.csv"

# Your GitHub personal access token (replace with your actual token)
github_token = "YOUR_GITHUB_TOKEN"


def download_github_file(repository_url, file_path, github_token):
    try:
        # Initialize the PyGithub client with your token
        g = Github(github_token)

        # Get the repository
        repo = g.get_repo(repository_url)

        # Get the contents of the file
        file_contents = repo.get_contents(file_path)

        # Download and save the file
        with open(file_path, "wb") as file:
            file.write(file_contents.decoded_content)

        print(f"File downloaded and saved to '{file_path}'")
    except Exception as e:
        print(f"Error downloading the file: {e}")


def extract_page_ids_from_csv(csv_file_path, page_ids_to_extract):
    try:
        # Initialize an empty dictionary
        page_id_dictionary = {page_id: "" for page_id in page_ids_to_extract}

        # Open the CSV file and read its contents
        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)

            # Iterate through each row in the CSV
            for row in csv_reader:
                page_id = row["Pecha ID"].strip()

                # Check if the page ID is in the list of IDs to extract
                if page_id in page_ids_to_extract:
                    page_id_dictionary[page_id] = ""

        return page_id_dictionary
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    download_github_file(repository_url, file_path, github_token)

    # Example usage:
    csv_file_path = "path_to_your_csv_file.csv"
    page_ids_to_extract = ["P000001", "P000002", "P000270", "P000080"]

    resulting_dictionary = extract_page_ids_from_csv(csv_file_path, page_ids_to_extract)
    print(resulting_dictionary)
