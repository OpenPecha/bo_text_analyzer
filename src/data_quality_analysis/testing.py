from pathlib import Path

from botok import WordTokenizer
from botok.config import Config

from data_quality_analysis.practise import analyze_tokens

config = Config(dialect_name="general", base_path=Path.home())
wt = WordTokenizer(config=config)

text = "abdul kalamའཁྱེད་ལ་སུན་པོ་ཀཟོས་པར་དགོངས་དག་ཞུ་ཨུམ་ཨུམ་་་། ()$%322 ༣༢༢་�� 你好吗 कैसे ཨོཾ་མ་ཎི་པདྨེ་ཧཱུྃ"
a, b, c = analyze_tokens(wt, text)
print(a, b, c)
