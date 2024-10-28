from typing import Optional

from kanren import Relation, membero, var, run
from kanren.constraints import neq

from truther.veridicality_elements import VeridicalityElements
from truther.sentence import Sentence


class FoundVeridicalityTransformation:
    def __init__(self, name: str, veridicality_element: str, node_ids: tuple):
        self.name = name
        self.veridicality_element = veridicality_element
        self.node_ids = node_ids


class LogicalSentence:
    def __init__(self,
                 sentence: Sentence,
                 veridicality_elements: VeridicalityElements | None = None):
        if veridicality_elements is None:
            veridicality_elements = VeridicalityElements()
        for pattern, label in veridicality_elements.get_patterns():
            sentence = sentence.search_and_merge(pattern, label)
            sentence = sentence.search_and_merge_lemmas(pattern, label)

        self.id_text = Relation()
        self.id_lemma = Relation()
        self.id_ve = Relation()
        self.id_pos = Relation()
        self.headdaut_gramrel = Relation()
        self.sent = sentence

        for i, pos in sentence.tok_pos:
            self.id_pos.add_fact(i, pos)

        for i, lemma in sentence.lemmas:
            self.id_lemma.add_fact(i, lemma)

        for i, tok in sentence.toks:
            self.id_text.add_fact(i, tok)
            for label_i, label in sentence.label_facts:
                if i == label_i:
                    self.id_ve.add_fact(i, label)

        for head, daut_rels in sentence.get_heads().items():
            for (daut, gramrel) in daut_rels:
                self.headdaut_gramrel.add_fact((head, daut), gramrel)

    def find_a_veridicality_transform(self) -> Optional[FoundVeridicalityTransformation]:
        for ve in [
            self.__double_pp_source,
            self.__non_possessive_pp_source,
            self.__subject_source,
            self.__double_pp,
            self.__single_passive_source_pp,
            self.__single_pp,
            self.__adjective_modification,
            self.__do_characterization,
            self.__passive,
            self.__verb_complement,
            self.__conditional_consequent_1,
            self.__conditional_consequent_2,
            self.__conditional_antecedent,
            self.__broken_pobj
        ]:
            out = ve()
            if out is not None:
                return out

    def merge_in_transform(self, veridicality_transformation: FoundVeridicalityTransformation) -> 'LogicalSentence':
        return LogicalSentence(sentence=self.sent.merge_and_label_node_ids(
            node_ids=veridicality_transformation.node_ids,
            label='proposition'
        ))

    def __double_pp_source(self) -> Optional[FoundVeridicalityTransformation]:
        # Double (and single) PP source
        # Sam agrees with the assertion of the idiot that it is raining
        # Sam argues in defense of the idiot’s assertion that it is raining
        # VE2 <-poss- VE1 <-acl- P # links 2 to P
        prop_id = var()
        ve_id = var()
        ve = var()
        ve_id_intermediate = var()
        out = run(
            10,
            (prop_id, ve_id),
            self.id_ve(ve_id, "negative_sources"),
            self.id_ve(prop_id, "proposition"),
            self.headdaut_gramrel((prop_id, ve_id_intermediate), 'acl'),
            self.headdaut_gramrel((ve_id, ve_id_intermediate), 'poss'),
            neq(prop_id, ve_id)
        )
        if out:
            return FoundVeridicalityTransformation('Double PP Source', "negative_sources", out[0])

    def __double_pp(self) -> Optional[FoundVeridicalityTransformation]:
        # Double PP
        # assessment (VE) -> winning (P): P <-ccomp|xcomp- v0 -prep-> prep -pobj-> VE
        prop_id = var()
        ve = var()
        ve_id = var()
        v0, prep, comp_rel = var(), var(), var()
        out = run(
            10,
            (ve, ve_id, prop_id),
            self.id_ve(ve_id, ve),
            self.id_ve(prop_id, "proposition"),
            self.headdaut_gramrel((prop_id, v0), comp_rel),
            membero(comp_rel, ('ccomp', 'xcomp')),
            self.headdaut_gramrel((prep, v0), 'prep'),
            self.headdaut_gramrel((ve_id, prep), 'pobj'),
            neq(prop_id, ve_id)
        )
        if out:
            return FoundVeridicalityTransformation('Double PP', out[0][0], out[0][1:])

    def __non_possessive_pp_source(self) -> Optional[FoundVeridicalityTransformation]:
        # Non possessive PP source

        # ve_id_intermediate <-prep- prep_id <-pobj- src_ve_id <-relcl- P
        prep_id = var()
        prop_id = var()
        src_ve_id = var()
        ve_id_intermediate = var()
        out = run(
            10,
            (prop_id, src_ve_id, prep_id),
            self.id_ve(src_ve_id, "negative_sources"),
            self.id_ve(prop_id, "proposition"),
            self.headdaut_gramrel((prop_id, src_ve_id), 'relcl'),
            self.headdaut_gramrel((src_ve_id, prep_id), 'pobj'),
            self.headdaut_gramrel((prep_id, ve_id_intermediate), 'prep'),
            neq(prop_id, ve_id_intermediate),
            neq(src_ve_id, ve_id_intermediate),
        )
        if out:
            return FoundVeridicalityTransformation('Non-Possessive PP Source',
                                                   "negative_sources",
                                                   out[0])

    def __single_passive_source_pp(self) -> Optional[FoundVeridicalityTransformation]:
        # It was argued by the idiot that it was raining
        # ve_id_intermediate <-agent- prep_id <-pobj- src_ve_id <-relcl- P
        prep_id = var()
        prop_id = var()
        src_ve_id = var()
        ve_id_intermediate = var()
        out = run(
            10,
            (prop_id, src_ve_id, prep_id),
            self.id_ve(src_ve_id, "negative_sources"),
            self.id_ve(prop_id, "proposition"),
            self.headdaut_gramrel((prop_id, src_ve_id), 'relcl'),
            self.headdaut_gramrel((src_ve_id, prep_id), 'pobj'),
            self.headdaut_gramrel((prep_id, ve_id_intermediate), 'agent'),
            neq(prop_id, ve_id_intermediate),
            neq(src_ve_id, ve_id_intermediate),
            neq(prep_id, ve_id_intermediate),
        )
        if out:
            return FoundVeridicalityTransformation('Single Passive Source PP',
                                                   "negative_sources",
                                                   out[0])

    def __passive(self) -> Optional[FoundVeridicalityTransformation]:
        # #It was argued by the idiot that it was raining
        # pass_id <-*pass- src_ve_id <-ccomp- P
        prop_id = var()
        src_ve_id = var()
        ve = var()
        pass_id = var()
        pass_rel = var()
        pos = var()
        out = run(
            10,
            (ve, prop_id, src_ve_id),
            self.id_ve(src_ve_id, ve),
            self.id_pos(src_ve_id, pos),
            self.id_ve(prop_id, "proposition"),
            self.headdaut_gramrel((prop_id, src_ve_id), 'ccomp'),
            self.headdaut_gramrel((pass_id, src_ve_id), pass_rel),
            membero(pass_rel, ('auxpass', 'nsubjpass')),
            neq(prop_id, src_ve_id),
            neq(prop_id, pass_id),
            neq(src_ve_id, pass_id),
        )
        if out:
            return FoundVeridicalityTransformation('Passive',
                                                   out[0][0],
                                                   out[0][1:])

    def __single_pp(self) -> Optional[FoundVeridicalityTransformation]:
        # She agreed with the assertion that the sun is yellow
        # prep_id <-pobj- src_ve_id <-acl- P
        prop_id = var()
        src_ve_id = var()
        prep_id = var()
        ve = var()
        out = run(
            10,
            (ve, prop_id, src_ve_id, prep_id),
            self.id_ve(src_ve_id, ve),
            self.id_ve(prop_id, "proposition"),
            self.headdaut_gramrel((prop_id, src_ve_id), 'acl'),
            self.headdaut_gramrel((src_ve_id, prep_id), 'pobj'),
            neq(prop_id, src_ve_id),
            neq(prop_id, prep_id),
            neq(src_ve_id, prep_id),
        )
        if out:
            return FoundVeridicalityTransformation('Single PP',
                                                   out[0][0],
                                                   out[0][1:])

    #
    def __do_characterization(self) -> Optional[FoundVeridicalityTransformation]:
        # She uttered the falsehood *(that) the sun is yellow
        # src_ve_id <-ccomp|relcl|acl- P
        prop_id = var()
        src_ve_id = var()
        ve = var()
        rel = var()

        out = run(
            10,
            (ve, prop_id, src_ve_id),
            self.id_ve(src_ve_id, ve),
            membero(ve, ('positive_nouns', 'negative_nouns', 'factive_nouns')),
            self.id_ve(prop_id, "proposition"),
            self.id_pos(src_ve_id, 'NOUN'),
            self.headdaut_gramrel((prop_id, src_ve_id), rel),
            membero(rel, ('ccomp', 'relcl', 'acl', 'nsubj', 'mark')),
            neq(prop_id, src_ve_id),
        )
        if out:
            return FoundVeridicalityTransformation('DO Characterization',
                                                   out[0][0],
                                                   out[0][1:])

    def __subject_source(self) -> Optional[FoundVeridicalityTransformation]:
        # The idiot said that the sun is yellow.
        # ve <-nsujb- ve_2 <-ccomp- P
        prop_id = var()
        src_ve_id = var()
        ve2_id = var()
        ve = var()
        pos = var()
        out = run(
            10,
            (ve, prop_id, src_ve_id),
            self.id_ve(src_ve_id, ve),

            membero(ve, ('positive_nouns', 'negative_nouns', 'factive_nouns', 'negative_sources')),
            self.id_ve(prop_id, "proposition"),
            self.id_pos(src_ve_id, pos),
            membero(pos, ('NOUN', 'PROPN')),
            self.headdaut_gramrel((prop_id, ve2_id), 'ccomp'),
            self.headdaut_gramrel((src_ve_id, ve2_id), 'nsubj'),
            neq(prop_id, src_ve_id),
            neq(prop_id, ve2_id),
            neq(src_ve_id, ve2_id),
        )

        if out:
            return FoundVeridicalityTransformation('Subject Source',
                                                   out[0][0],
                                                   out[0][1:])

    def __verb_complement(self) -> Optional[FoundVeridicalityTransformation]:
        # He lied that the sun is yellow.
        # ve <-ccomp- P
        prop_id = var()
        src_ve_id = var()
        ve = var()

        out = run(
            10,
            (ve, prop_id, src_ve_id),
            self.id_ve(src_ve_id, ve),
            self.id_pos(src_ve_id, "VERB"),
            membero(ve, ('positive_verbs', 'negative_verbs', 'factive_verbs', 'counter_factive_verbs')),
            self.headdaut_gramrel((prop_id, src_ve_id), 'ccomp'),
            self.id_ve(prop_id, "proposition"),
            neq(prop_id, src_ve_id),
        )
        if out:
            return FoundVeridicalityTransformation('Verb Complement',
                                                   out[0][0],
                                                   out[0][1:])

    def __adjective_modification(self) -> Optional[FoundVeridicalityTransformation]:
        # It is true that the sun is yellow
        # ve_adj -acomp-> be <-ccomp- P
        prop_id = var()
        src_ve_id = var()
        ve = var()
        be_lemma = var()
        be_id = var()

        out = run(
            10,
            (ve, prop_id, be_id, src_ve_id),
            self.id_ve(src_ve_id, ve),
            self.id_lemma(be_id, be_lemma),
            membero(be_lemma, ("remain", "be")),
            membero(ve, ('negative_adjectives', 'positive_adjectives')),
            self.headdaut_gramrel((src_ve_id, be_id), 'acomp'),
            self.headdaut_gramrel((prop_id, be_id), 'ccomp'),
            self.id_ve(prop_id, "proposition"),
            neq(prop_id, src_ve_id),
            neq(prop_id, be_id),
            neq(src_ve_id, be_id),
        )
        if out:
            return FoundVeridicalityTransformation('Adjective Modification',
                                                   out[0][0],
                                                   out[0][1:])

    def __conditional_consequent_1(self) -> Optional[FoundVeridicalityTransformation]:
        # If he comes on time then the sun is yellow.
        # ve_adj <-acomp- head <-advcl- P
        prop_id = var()
        head_id = var()
        src_ve_id = var()
        ve_head_rel_rel = var()
        prop_head_rel = var()

        out = run(
            10,
            (prop_id, src_ve_id),
            self.headdaut_gramrel((src_ve_id, head_id), ve_head_rel_rel),
            membero(ve_head_rel_rel, ('mark', 'acomp')),
            self.headdaut_gramrel((head_id, prop_id), prop_head_rel),
            membero(prop_head_rel, ('advcl',)),
            self.id_ve(src_ve_id, 'conditionals'),
            self.id_ve(prop_id, "proposition"),
            neq(prop_id, src_ve_id),
            neq(prop_id, head_id),
            neq(src_ve_id, head_id),
        )
        if out:
            return FoundVeridicalityTransformation('Conditional Consequent',
                                                   "conditionals",
                                                   out[0])

    def __conditional_consequent_2(self) -> Optional[FoundVeridicalityTransformation]:
        # The sun is yellow as soon as next week.
        # P -advmod-> conditional_ve
        prop_id = var()
        conditional_ve_id = var()

        out = run(
            10,
            (prop_id, conditional_ve_id),
            self.headdaut_gramrel((conditional_ve_id, prop_id), "advmod"),
            self.id_ve(conditional_ve_id, 'conditionals'),
            self.id_ve(prop_id, "proposition"),
            neq(prop_id, conditional_ve_id),
        )
        if out:
            return FoundVeridicalityTransformation('Conditional Consequent',
                                                   "conditionals",
                                                   out[0])

    def __conditional_antecedent(self) -> Optional[FoundVeridicalityTransformation]:
        # If the sun is yellow it will rain.
        # prop -mark-> conditional_ve
        prop_id = var()
        conditional_ve_id = var()
        ve = var()

        out = run(
            10,
            (prop_id, conditional_ve_id),
            self.headdaut_gramrel((conditional_ve_id, prop_id), "mark"),
            self.id_ve(conditional_ve_id, ve),
            membero(ve, ('conditionals', 'causals')),
            self.id_ve(prop_id, "proposition"),
            neq(prop_id, conditional_ve_id),
        )
        if out:
            return FoundVeridicalityTransformation('Conditional Antecedent or Causal',
                                                   "conditionals",
                                                   out[0])

    def __broken_pobj(self):
        # He disagreed with Bill's assessment that the sun is yellow., after first VT
        # VE -prep-> prop
        prop_id = var()
        ve_id = var()
        ve = var()

        out = run(
            10,
            (ve, prop_id, ve_id),
            self.headdaut_gramrel((prop_id, ve_id), "prep"),
            self.id_ve(ve_id, ve),
            self.id_pos(ve_id, 'VERB'),
            membero(ve, ('negative_verbs', 'positive_verbs', 'factive_verbs', 'counter_factive_verbs')),
            self.id_ve(prop_id, "proposition"),
            neq(prop_id, ve_id),
        )
        if out:
            return FoundVeridicalityTransformation('Broken Pobj',
                                                   out[0][0],
                                                   out[0][1:])
