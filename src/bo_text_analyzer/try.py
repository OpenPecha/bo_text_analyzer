import os

from openpecha.core.pecha import OpenPechaGitRepo

# Set environment variables (Replace with actual values and ensure security for sensitive data like tokens)
os.environ["GITHUB_TOKEN"] = "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"
os.environ["OPENPECHA_DATA_GITHUB_ORG"] = "OpenPecha-Data"
os.environ["GITHUB_USERNAME"] = "gangagyatso4364"


def get_base_text_from_cloned_git_repo(pecha_id):
    try:
        opf = OpenPechaGitRepo(pecha_id=pecha_id)
        parts = opf.base_names_list
        return parts
    except Exception as e:
        print(f"An error occurred while processing Pecha ID {pecha_id}: {e}")
        return None


pecha_ids = [
    "O1EB43CCE",
    "I229815A9",
    "IFF5475DD",
    "I84B5FA9B",
    "P000792",
    "I0FAA1C40",
    "I20A50BB6",
    "IB3BFD2E7",
    "I33D3B96F",
    "ICB0FDD9A",
    "ID194E73E",
    "IBF06BC6C",
    "I79C6CCCC",
    "O1EB43CCE",
    "O3C4D0D40",
]

for pecha_id in pecha_ids:
    print(f"Processing Pecha ID: {pecha_id}")
    base_text = get_base_text_from_cloned_git_repo(pecha_id)
    print(f"Base Text for {pecha_id}: {base_text}")
