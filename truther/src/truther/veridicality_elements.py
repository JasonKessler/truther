import os
from glob import glob


class VeridicalityElements(object):
    def __init__(self):
        unsorted_patterns = []
        for file_name in self._list_veridicality_element_files():
            for line in open(file_name).readlines():
                ve_class_name = os.path.basename(file_name)
                ve_tokens = line.strip().lower().split()
                unsorted_patterns.append([-len(ve_tokens), ve_tokens, ve_class_name])
        self._patterns = [(tokens, ve_class)
                          for _, tokens, ve_class
                          in sorted(unsorted_patterns)]
    def _list_veridicality_element_files(self):
        return glob(os.path.join(os.path.dirname(__file__), 'lexicon', '*'))
    def get_patterns(self):
        return self._patterns
