from openpecha.core.pecha import OpenPechaGitRepo

from bo_text_analyzer.text_analyzer import TextAnalyzer


class OpfAnalyzer(TextAnalyzer):
    def __init__(self, premium_threshold, opf_id):
        super().__init__(premium_threshold)
        self.opf_id = opf_id
        self.opf_report = {}

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

    def get_text(self):
        base_texts = self.get_base_text()
        return base_texts

    def analyze(self):
        return super().analyze()

    def truncate_text(self, text):
        pass

    def get_opf_report(self):
        self.opf_report[self.opf_id] = self.text_report
        return self.opf_report
