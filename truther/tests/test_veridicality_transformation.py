from unittest import TestCase
from unittest.mock import patch, call

import spacy

from truther.sentence import make_sentence_from_doc
from truther.veridicality_transformation import LogicalSentence, FoundVeridicalityTransformation


class TestVeridicalityTransformations(TestCase):
    def setUp(self):
        self.nlp = spacy.load('en_core_web_lg')

    @patch('builtins.print')
    def test_printing(self, mock_print):
        sent = make_sentence_from_doc(self.nlp('My name is Jason.'))
        sent.print_labeled()
        assert mock_print.call_args_list == [call(0, 'my', [], ['PRON']),
                                             call(1, 'name', [], ['NOUN']),
                                             call(2, 'is', [], ['AUX']),
                                             call(3, 'jason', [], ['PROPN']),
                                             call(4, '.', [], ['PUNCT'])]

    def test_double_pp_source(self):
        doc = self.nlp("Sam argues in defense of the idiot’s assertion that it is raining.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'it is raining'.split(),
                label='proposition'
            )
        )

        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == vars(
            FoundVeridicalityTransformation(
                name='Double PP Source',
                node_ids=(10, 6),
                veridicality_element='negative_sources'
            )
        )

    def test_double_pp(self):
        doc = self.nlp(
            "He disagreed with President Bush’s assessment earlier in the day that the U.S. is winning the war in Iraq.")
        found_vt = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the U.S. is winning the war in Iraq'.lower().split(),
                label='proposition'
            )
        ).find_a_veridicality_transform()

        assert vars(found_vt) == vars(
            FoundVeridicalityTransformation(
                name='Double PP',
                node_ids=(6, 12),
                veridicality_element='positive_nouns'
            )
        )

    def test_pp_source2(self):
        doc = self.nlp("Sam agrees with idiot’s assertion that it is raining.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'it is raining'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == vars(
            FoundVeridicalityTransformation(
                name='Double PP Source',
                node_ids=(7, 3),
                veridicality_element='negative_sources'
            )
        )

    def test_non_possessive_pp_source(self):
        doc = self.nlp("Sam agrees with assertion of the idiot that it is raining.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'it is raining'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Non-Possessive PP Source',
                                  'node_ids': (8, 6, 4),
                                  'veridicality_element': 'negative_sources'}

    def test_single_passive_source_pp(self):
        doc = self.nlp("It was argued by the idiot that it is raining.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'it is raining'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Single Passive Source PP',
                                  'node_ids': (7, 5, 3),
                                  'veridicality_element': 'negative_sources'}

    def test_passive(self):
        doc = self.nlp("It was denied that the sun is yellow.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        print(lsent.sent.print_labeled())
        import pprint;
        pprint.pprint(lsent.sent.get_heads())
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Passive',
                                  'node_ids': (4, 2),
                                  'veridicality_element': 'negative_verbs'}

    def test_single_pp(self):
        doc = self.nlp("She agreed with the assertion that the sun is yellow.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Single PP',
                                  'node_ids': (6, 4, 2),
                                  'veridicality_element': 'positive_nouns'}

    def test_do_characterization(self):
        doc = self.nlp("She uttered the falsehood that the sun is yellow.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'DO Characterization',
                                  'node_ids': (5, 3),
                                  'veridicality_element': 'negative_nouns'}

    def test_do_characterization2(self):
        doc = self.nlp("The fiction that the sun is yellow.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'DO Characterization',
                                  'node_ids': (3, 1),
                                  'veridicality_element': 'negative_nouns'}


    def test_subject_source(self):
        doc = self.nlp("The idiot said that the sun is yellow.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()

        assert vars(found_vt) == {'name': 'Subject Source',
                                  'node_ids': (4, 1),
                                  'veridicality_element': 'negative_sources'}

    def test_verb_complement(self):
        doc = self.nlp("He lied that the sun is yellow.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Verb Complement',
                                  'node_ids': (3, 1),
                                  'veridicality_element': 'negative_verbs'}

    def test_adjective_modification(self):
        doc = self.nlp("It is true that the sun is yellow.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Adjective Modification',
                                  'node_ids': (4, 1, 2),
                                  'veridicality_element': 'positive_adjectives'}

    def test_conditional_consequent_1(self):
        doc = self.nlp("If he is on time the sun is yellow.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        lsent.sent.print_labeled()
        assert vars(found_vt) == {'name': 'Conditional Consequent',
                                  'node_ids': (5, 0),
                                  'veridicality_element': 'conditionals'}

    def test_conditional_consequent_2(self):
        doc = self.nlp("The sun is yellow as soon as next week.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Conditional Consequent',
                                  'node_ids': (0, 4),
                                  'veridicality_element': 'conditionals'}

    def test_conditional_antecedent(self):
        doc = self.nlp("If the sun is yellow then it will rain.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Conditional Antecedent or Causal',
                                  'node_ids': (1, 0),
                                  'veridicality_element': 'conditionals'}

    def test_causal(self):
        doc = self.nlp("While the sun is yellow it will rain.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Conditional Antecedent or Causal',
                                  'node_ids': (1, 0),
                                  'veridicality_element': 'conditionals'}


    def test_causal(self):
        doc = self.nlp("While the sun is yellow it will rain.")
        lsent = LogicalSentence(
            sentence=make_sentence_from_doc(doc).search_and_merge(
                'the sun is yellow'.split(),
                label='proposition'
            )
        )
        found_vt = lsent.find_a_veridicality_transform()
        assert vars(found_vt) == {'name': 'Conditional Antecedent or Causal',
                                  'node_ids': (1, 0),
                                  'veridicality_element': 'conditionals'}
