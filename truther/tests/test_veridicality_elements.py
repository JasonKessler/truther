from src.truther.veridicality_elements import VeridicalityElements


def test_get_patterns():
    patterns = VeridicalityElements().get_patterns()
    assert all(len(x) == 2 for x in patterns)
    assert set(o for _, o in patterns) == {'causals',
                                           'conditionals',
                                           'counter_factive_verbs',
                                           'factive_verbs',
                                           'negative_adjectives',
                                           'negative_nouns',
                                           'negative_sources',
                                           'negative_verbs',
                                           'neutral_verbs',
                                           'positive_adjectives',
                                           'positive_nouns',
                                           'positive_verbs'}
