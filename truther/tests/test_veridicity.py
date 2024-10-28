from unittest import TestCase

import spacy

from truther.veridicity import get_proposition_veridicity


class TestVeridicalityTransformations(TestCase):
    def setUp(self):
        self.nlp = spacy.load('en_core_web_lg')

    def test_get_proposition_veridicity_factive(self):
        assert get_proposition_veridicity(
            sentence=self.nlp("The fiction that George knows the sun is yellow."),
            proposition=self.nlp("the sun is yellow")
        ) == 'positive'

    def test_get_proposition_veridicity_neg(self):
        assert get_proposition_veridicity(
            sentence=self.nlp("The fiction that the sun is yellow."),
            proposition=self.nlp("the sun is yellow")
        ) == 'negative'

    def test_get_proposition_veridicity_cond(self):
        assert get_proposition_veridicity(
            sentence=self.nlp("If the sun is yellow it will be a good day."),
            proposition=self.nlp("the sun is yellow")
        ) == 'neutral'

    def test_get_proposition_veridicity_pos(self):
        assert get_proposition_veridicity(
            sentence=self.nlp("Bill forgot that Sarah believes the sun is yellow."),
            proposition=self.nlp("the sun is yellow")
        ) == 'positive'


    def test_get_proposition_veridicity_neg2(self):
        assert get_proposition_veridicity(
            sentence=self.nlp("He disagreed with Bill's assessment that the sun is yellow."),
            proposition=self.nlp("the sun is yellow")
        ) == 'negative'
