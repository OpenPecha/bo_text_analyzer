from openpecha.core.pecha import OpenPechaGitRepo

from bo_text_analyzer.text import Text
from bo_text_analyzer.text_analyzer import TextAnalyzer


class OpfAnalyzer(TextAnalyzer):
    def __init__(self, non_word_threshold, no_bo_word_threshold, opf_id):
        super().__init__(non_word_threshold, no_bo_word_threshold)
        self.opf_id = opf_id
        self.opf_report = {}
        self.opf = OpenPechaGitRepo(pecha_id=self.opf_id)

    def get_base_text(self):
        try:
            text_objs = []
            bases = self.opf.base_names_list
            for base in bases:
                text_obj = Text()
                text = self.opf.read_base_file(base)
                text_obj.texts[base] = text
                text_obj = self.truncate_text(text_obj, base)
                text_objs.append(text_obj)
            return text_objs
        except Exception as e:
            print(f"An error occurred while processing Pecha ID {self.opf_id}: {e}")
            return None

    def get_text(self):
        text_obj = self.get_base_text()
        return text_obj

    def analyze(self):
        return super().analyze()

    def get_intro_page(self, base_name):
        default_intro_page = 2  # Default value
        intro_page = default_intro_page
        try:
            # First attempt to get intro page
            intro_page = self.opf.meta.bases[base_name]["source_metadata"][
                "volume_pages_intro"
            ]
        except Exception:
            try:
                # Second attempt to get intro page
                intro_page = self.opf.meta.source_metadata[base_name][
                    "volume_pages_intro"
                ]
            except Exception:
                pass
        return intro_page

    def get_page_length(self, base_name):
        default_page_length = 2
        page_length = default_page_length
        try:
            # First attempt to get page length
            page_length = self.opf.meta.bases[base_name]["source_metadata"][
                "total_pages"
            ]
        except Exception:
            try:
                # Second attempt to get page length
                page_length = self.opf.meta.source_metadata["base"][base_name][
                    "total_pages"
                ]
            except Exception:
                pass
        return page_length

    def get_begin_end_index(self, intro_page, total_pages, base_name):
        begin = 0
        end = -1
        layers = self.opf.components[base_name]
        try:
            for layer in layers:
                if layer.name == "pagination":
                    layer_obj = self.opf.get_layer(base_name, layer)
                    for ann_id, ann_obj in layer_obj.annotations.items():
                        if ann_obj.get("imgnum") == intro_page + 1:
                            begin = ann_obj.get("span").get("start")
                        if ann_obj.get("imgnum") == total_pages - 2:
                            end = ann_obj.get("span").get("end")
        except Exception as e:
            print(f"pagination layer can't be found for Pecha ID {self.opf_id}: {e}")
            pass
        return begin, end

    def truncate_text(self, text_obj, base_name):
        intro_page = self.get_intro_page(base_name)
        page_length = self.get_page_length(base_name)
        begin, end = self.get_begin_end_index(
            intro_page=intro_page, total_pages=page_length, base_name=base_name
        )
        if begin == 0 and end == -1:
            text_obj = text_obj.texts[base_name][:]
        else:
            text_obj.texts[base_name] = text_obj.texts[base_name][begin:end]
        text_obj.start = begin
        text_obj.end = end
        return text_obj

    def get_opf_report(self):
        self.opf_report[self.opf_id] = self.text_report
        return self.opf_report
