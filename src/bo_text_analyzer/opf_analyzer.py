import os

from openpecha.core.pecha import OpenPechaGitRepo

from bo_text_analyzer.text_analyzer import TextAnalyzer


class OpfAnalyzer(TextAnalyzer):
    def __init__(self, premium_threshold, opf_id):
        super().__init__(premium_threshold)
        self.opf_id = opf_id
        # Set environment variables
        os.environ["GITHUB_TOKEN"] = "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"
        os.environ["OPENPECHA_DATA_GITHUB_ORG"] = "OpenPecha-Data"
        os.environ["GITHUB_USERNAME"] = "gangagyatso4364"

    def get_base_text(self):
        try:
            base_text = {}
            opf = OpenPechaGitRepo(pecha_id=self.opf_id)
            bases = opf.base_names_list
            for base in bases:
                base_text[base] = opf.read_base_file(base)
            return base_text
        except Exception as e:
            print(f"An error occurred while processing Pecha ID {self.opf_id}: {e}")
            return None
