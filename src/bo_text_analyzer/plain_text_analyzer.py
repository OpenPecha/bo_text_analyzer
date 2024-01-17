from pathlib import Path

from bo_text_analyzer.text import Text
from bo_text_analyzer.text_analyzer import TextAnalyzer


class PlainTextAnalyzer(TextAnalyzer):
    def __init__(self, non_word_threshold, no_bo_word_threshold, file_path):
        super().__init__(non_word_threshold, no_bo_word_threshold)
        self.file_path = Path(file_path)
        self.text_file_report = {}

    def get_text(self):
        text_objs = []
        path_obj = self.file_path
        if path_obj.is_dir():
            # Traverse the directory for text files
            for file_path in path_obj.iterdir():
                if file_path.is_file() and file_path.suffix == ".txt":
                    try:
                        text_obj = Text()
                        with open(file_path, encoding="utf-8") as file:
                            text = file.read()
                            text_obj.texts[file_path.name] = text
                            text_objs.append(text_obj)
                    except Exception as e:
                        print(f"An error occurred while reading {file_path}: {e}")

        elif path_obj.is_file() and path_obj.suffix == ".txt":
            # Read a single text file
            try:
                with open(path_obj, encoding="utf-8") as file:
                    text = file.read()
                    text_obj = Text()
                    text_obj.texts[path_obj.name] = text
                    text_objs.append(text_obj)
            except Exception as e:
                print(f"An error occurred while reading {path_obj}: {e}")
        else:
            print(
                f"The provided path {self.file_path} is neither a directory nor a text file."
            )

        return text_objs

    def analyze(self):
        return super().analyze()

    def get_text_report(self):
        self.text_file_report = self.text_report
        return self.text_file_report
