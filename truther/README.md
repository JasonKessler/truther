# truther

Determine whether someone is asserting, denying, or not taking a stance toward a proposition.

## Cite as:

Kessler, Jason S. Polling the Blogosphere: A Rule-Based Approach to Belief Classification. 2007. Proceedings of the International AAAI Conference on Web and Social Media, 2(1), 68-75. https://doi.org/10.1609/icwsm.v2i1.18619

## Introduction

This is a Python implementation to the above paper (Kessler 2007), which allows one to determine if, given a sentence,
whether the author of the sentence is asserting, denying or taking no stance toward a proposition within the sentence.
This is also referred to as the veridicity of the proposition.

The original code was written in Prolog and used an early version of the Stanford CoreNLP toolkit for parsing and 
part-of-speech tagging. That code has been lost, but this package recreates it, using [spaCy](https://spacy.io/) and 
a Python [implementation](https://github.com/pythological/kanren) of [miniKanren](http://minikanren.org/) (Friedman et al. 2005).

## Usage

```python
import spacy
from truther import get_proposition_veridicity

nlp = spacy.load('en_core_web_lg')

get_proposition_veridicity(
    sentence=nlp("If it rains today, we might get wet."),
    proposition=nlp("it will rain today")
)
# returns "neutral"



get_proposition_veridicity(
    sentence=nlp("He denied it will rain today."),
    proposition=nlp("it will rain today")
)
# returns "negative"


get_proposition_veridicity(
    sentence=nlp("He forgot it will rain today."),
    proposition=nlp("it will rain today")
)
# returns "positive"

get_proposition_veridicity(
    sentence=nlp("He did not deny it will rain today."),
    proposition=nlp("it will rain today")
)
# returns "neutral"

```

## References

Kessler, Jason S. (2021). Polling the Blogosphere: A Rule-Based Approach to Belief Classification. Proceedings of the International AAAI Conference on Web and Social Media, 2(1), 68-75. https://doi.org/10.1609/icwsm.v2i1.18619

Daniel P. Friedman,  William E. Byrd,  Oleg Kiselyov. The Reasoned Schemer. The MIT Press. 2005
