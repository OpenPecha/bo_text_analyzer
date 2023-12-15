
class TextAnalyzer:
    def __init__(self, text, preminum_threshold):
        self.text = text
        self.total_words = 0
        self.total_non_words = 0
        self.total_non_bo_words = 0
        self.non_word_percentage = 0
        self.non_bo_word_percentage = 0
        self.is_premium = False
        self.preminum_threshold = preminum_threshold

    def tokenize_text(self):
        pass
    
    def count_non_words(self, tokens):
        pass

    def count_non_bo_words(self, tokens):
        pass


    def analyze(self):
        text_report = {}
        tokens = self.tokenize_text()

        self.total_words = len(tokens)
        self.total_non_words = self.count_non_words(tokens)
        self.total_non_bo_words = self.count_non_bo_words(tokens)
        self.non_word_percentage = self.total_non_words / self.total_words
        self.non_bo_word_percentage = self.total_non_bo_words / self.total_words
        self.is_premium = self.non_bo_word_percentage < self.preminum_threshold

        text_report['total_words'] = self.total_words
        text_report['total_non_words'] = self.total_non_words
        text_report['total_non_bo_words'] = self.total_non_bo_words
        text_report['non_word_percentage'] = self.non_word_percentage
        text_report['non_bo_word_percentage'] = self.non_bo_word_percentage
        text_report['is_premium'] = self.is_premium

        return text_report

    
        

        