from collections import defaultdict
from typing import List, Tuple, Dict, Set

from spacy.tokens.doc import Doc


class Sentence(object):
    def __init__(self,
                 doc: Doc,
                 toks: List[Tuple[int, str]],
                 lemmas: List[Tuple[int, str]],
                 tok_pos: List[Tuple[int, str]],
                 follows_facts: List[Tuple[int, int | None]],
                 headof_facts: List[Tuple[int, Tuple[int, str]]],
                 label_facts: List[Tuple[int, str]]):
        self.doc = doc
        self.toks = toks
        self.lemmas = lemmas
        self.tok_pos = tok_pos
        self.follows_facts = follows_facts
        self.headof_facts = headof_facts
        self.label_facts = label_facts
        self._setup()

    def _setup(self):
        self._tok_index = {}
        for i, tok in self.toks:
            self._tok_index.setdefault(tok, []).append(i)

        self._lemma_index = {}
        for i, lemma in self.lemmas:
            self._lemma_index.setdefault(lemma, []).append(i)

        self._index_tok = {i: tok for i, tok in self.toks}
        self._index_lemma = {i: lemma for i, lemma in self.lemmas}
        self._dep_index = defaultdict(set)
        self._dauts: Dict[int, Set[Tuple[int, str]]] = defaultdict(set)
        self._heads: Dict[int, Set[Tuple[int, str]]] = defaultdict(set)
        for daut, (head, dep) in self.headof_facts:
            self._dep_index[dep].add((daut, head))
            self._dauts[head].add((daut, dep))
            self._heads[daut].add((head, dep))
        self._labels = defaultdict(set)
        self._label_index = defaultdict(set)
        for tok_i, label in self.label_facts:
            self._label_index[label].add(tok_i)
            self._labels[tok_i].add(label)
        return self

    def get_heads(self) -> Dict[int, Set[Tuple[int, str]]]:
        return self._heads

    def print_labeled(self) -> None:
        for i, tok in self.toks:
            print(i, tok, [label for label_i, label in self.label_facts if i == label_i],
                  [pos for pos_i, pos in self.tok_pos if i == pos_i])

    def search_and_merge(self, search: List[str], label: str) -> 'Sentence':
        try:
            start_indices = self._tok_index[search[0]]
        except KeyError:
            return self
        for start_idx in start_indices:
            if start_idx + len(search) > len(self.toks):
                return self
            elements_to_merge = list(range(start_idx, start_idx + len(search)))
            # ensure that all search tokens, and not just first, match
            if all(self._index_tok[tok_i] == search[search_i]
                   for search_i, tok_i in enumerate(elements_to_merge)):
                return self.merge_and_label_node_ids(elements_to_merge, label)
        return self

    def search_and_merge_lemmas(self, search: List[str], label: str) -> 'Sentence':
        try:
            start_indices = self._lemma_index[search[0]]
        except KeyError:
            return self
        for start_idx in start_indices:
            if start_idx + len(search) > len(self.lemmas):
                return self
            elements_to_merge = list(range(start_idx, start_idx + len(search)))
            if all(self._index_lemma[tok_i] == search[search_i]
                   for search_i, tok_i in enumerate(elements_to_merge)):
                return self.merge_and_label_node_ids(elements_to_merge, label)
        return self

    def merge_and_label_node_ids(self, node_ids: List[int] | tuple, label: str) -> 'Sentence':
        if (node_ids[0], label) not in self.label_facts:
            self.label_facts.append((node_ids[0], label))

        if len(node_ids) == 1:
            return self._setup()

        new_toks = []
        new_lemmas = []
        new_tok_pos = []
        new_follows_facts = []
        new_headof_facts = []
        last_tok = None
        headof_dict = {}
        for tok_i, head_i in self.headof_facts:
            headof_dict.setdefault(tok_i, []).append(head_i)
        for tok_i, tok in self.toks:
            cur_tok = None
            if tok_i not in node_ids:
                cur_tok = (tok_i, tok)
                new_toks.append(cur_tok)
                for lemma_id, lemma in self.lemmas:
                    if lemma_id == tok_i:
                        new_lemmas.append((tok_i, lemma))
                for pos_id, pos in self.tok_pos:
                    if pos_id == tok_i:
                        new_tok_pos.append((tok_i, pos))
                for head_i, rel in headof_dict[tok_i]:
                    if head_i in node_ids:
                        new_headof_facts.append((tok_i, (node_ids[0], rel)))
                    else:
                        new_headof_facts.append((tok_i, (head_i, rel)))
            elif tok_i == node_ids[0]:
                new_string = ' '.join([tok for i, tok in self.toks
                                       if i in node_ids])
                new_i = node_ids[0]
                cur_tok = (new_i, new_string)
                new_toks.append(cur_tok)
                new_lemmas.append((new_i, ' '.join([lemma for i, lemma in self.lemmas
                                                    if i in node_ids])))

                for el_to_merge_i in node_ids:
                    new_tok_pos.append((tok_i, self.tok_pos[el_to_merge_i][1]))

                    for head_i, rel in headof_dict[el_to_merge_i]:
                        if head_i not in node_ids:
                            new_headof_facts.append((new_i, (head_i, rel)))
            if cur_tok is not None and last_tok is not None:
                new_follows_facts.append((last_tok[0], cur_tok[0]))
            if cur_tok is not None:
                last_tok = cur_tok
        return Sentence(doc=self.doc,
                        toks=new_toks,
                        lemmas=new_lemmas,
                        tok_pos=new_tok_pos,
                        follows_facts=new_follows_facts,
                        headof_facts=new_headof_facts,
                        label_facts=self.label_facts)


def make_sentence_from_doc(doc: Doc) -> Sentence:
    toks = [(tok.i, tok.lower_) for tok in doc]
    lemmas = [(tok.i, tok.lemma_) for tok in doc]
    tok_pos = [(tok.i, tok.pos_) for tok in doc]
    tokidx = [i for i, tok in toks]
    follows_facts = list(zip(tokidx, (tokidx[1:] + [None])))
    headof_facts = [(tok.i, (-1 if tok.head == tok else tok.head.i, tok.dep_)) for tok in doc]
    return Sentence(doc=doc,
                    toks=toks,
                    lemmas=lemmas,
                    tok_pos=tok_pos,
                    follows_facts=follows_facts,
                    headof_facts=headof_facts,
                    label_facts=[])
