from pprint import pprint

from spacy.tokens.doc import Doc

from truther.sentence import make_sentence_from_doc
from truther.veridicality_orientation import update_proposition_orientation
from truther.veridicality_transformation import LogicalSentence


def get_proposition_veridicity(
        sentence: Doc,
        proposition: Doc,
) -> str:
    logical_sentence = LogicalSentence(
        sentence=make_sentence_from_doc(sentence).search_and_merge(
            [x.orth_ for x in proposition],
            label='proposition'
        )
    )

    veridicality_orientation = 'positive'
    factive_freeze = False
    veridicality_transform = logical_sentence.find_a_veridicality_transform()
    while veridicality_transform is not None:
        veridicality_orientation, factive_freeze = update_proposition_orientation(
            start_orientation=veridicality_orientation,
            element_name=veridicality_transform.veridicality_element,
            factive_freeze=factive_freeze
        )
        logical_sentence = logical_sentence.merge_in_transform(veridicality_transform)
        veridicality_transform = logical_sentence.find_a_veridicality_transform()
    return veridicality_orientation
