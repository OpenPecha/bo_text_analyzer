from bo_text_analyzer.text_analyzer import TextAnalyzer


class OpfAnalyzer(TextAnalyzer):

    def __init__(self, preminum_threshold, opf_id):
        super().__init__(preminum_threshold)
        self.opf_id = opf_id
    
    def get_text(self):
        text = {}
        return text
