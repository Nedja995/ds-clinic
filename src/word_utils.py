##
# Text utility
#
import re

def sredi_slova(text) -> str:
    mape = {"č": "c", "ć": "c", "ž": "z", "š": "s", "đ": "dj", "Č": "C", "Ć": "C", "Ž": "Z", "Š": "S", "Đ": "Dj"}
    for k, v in mape.items(): text = text.replace(k, v)
    return text

def normalize_whitespace(string):
    txt = string.replace("  ", " ")
    txt = txt.strip()
    txt = re.sub(r'(\s)\1{1,}', r'\1', txt)
    return txt

def has_numbers(input_string):
  """Checks if the input string contains any digit using regex."""
  # The pattern r'\d' searches for any digit (0-9)
  return bool(re.search(r'\d', input_string))