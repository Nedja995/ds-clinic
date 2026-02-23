##
# Text utility
#
import re

def sredi_slova(text) -> str:
    mape = {"č": "c", "ć": "c", "ž": "z", "š": "s", "đ": "dj", "Č": "C", "Ć": "C", "Ž": "Z", "Š": "S", "Đ": "Dj"}
    for k, v in mape.items(): text = text.replace(k, v)
    return text

def normalize_whitespace(string):
    return re.sub(r'(\s)\1{1,}', r'\1', string)