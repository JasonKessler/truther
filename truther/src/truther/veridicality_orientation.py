ORIENTATION_TO_ORIENTATION_CLASS = {'causals': 'neutral',
                                    'conditionals': 'neutral',
                                    'counter_factive_verbs': 'counterfactive',
                                    'factive_verbs': 'factive',
                                    'negative_adjectives': 'negative',
                                    'negative_nouns': 'negative',
                                    'negative_sources': 'negative',
                                    'negative_verbs': 'negative',
                                    'neutral_verbs': 'neutral',
                                    'positive_adjectives': 'positive',
                                    'positive_nouns': 'positive',
                                    'positive_verbs': 'positive',
                                    'neutral': 'neutral',
                                    'positive': 'positive',
                                    'negative': 'negative',
                                    'counterfactive': 'counterfactive',
                                    'factive': 'factive'}


def update_proposition_orientation(
        start_orientation: str,
        element_name: str,
        factive_freeze: bool = False
) -> (str, bool):
    start_class = ORIENTATION_TO_ORIENTATION_CLASS[start_orientation]
    element_class = ORIENTATION_TO_ORIENTATION_CLASS[element_name]
    if start_class == 'neutral':
        return 'neutral', factive_freeze
    if element_class == 'factive':
        return start_class, True
    if element_class == 'neutral':
        if not factive_freeze:
            return 'neutral', factive_freeze
        return start_class, factive_freeze
    if element_class == 'negative':
        if not factive_freeze:
            if start_class == 'positive':
                return 'negative', factive_freeze
            if start_class == 'negative':
                return 'positive', factive_freeze
        return start_class, factive_freeze
    if element_class == 'counterfactive':
        if not factive_freeze:
            if start_class == 'positive':
                return 'negative', True
            if start_class == 'negative':
                return 'neutral', True  # don't pretend bill denies it's raining
            return start_class, True
        else:
            return start_class, True  # don't pretend bill knows it's raining

    if element_class == 'positive':
        return start_class, factive_freeze
