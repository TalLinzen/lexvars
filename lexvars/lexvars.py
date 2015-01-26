# Author: Tal Linzen <linzen@nyu.edu>
# 2011-2014
# License: BSD (3-clause)

import __builtin__
import collections
import itertools
import os

import numpy as np

from celex import Celex


class LexVars(object):
    '''
    Example:

    clx = Celex(path_to_celex)
    lv = LexVars(clx)
    lv.inflectional_entropy('shoe')
    '''

    def __init__(self, clx):
        self.clx = clx
        self._derivational_families = {}

    def wordnet_synsets(self, word):
        '''
        Number of WordNet "synsets" (roughly, senses) for the given word.
        This variable collapses across different parts of speech, meanings,
        etc.
        '''
        from nltk.corpus import wordnet
        synsets = wordnet.synsets(word)
        return len(synsets) if len(synsets) > 0 else None

    def pos_freq(self, lemma, pos):
        '''
        Total frequency of the lemma when used as the given part of speech:

        >>> lv.pos_freq('wind', 'noun')
        3089
        '''
        lemmas = self.clx.lemma_lookup(lemma)
        return sum(lemma.Cob for lemma in lemmas if lemma.ClassNum == pos)

    def _smoothed_log_ratio(self, a, b):
        return np.log2((a + 1.) / (b + 1.))

    def log_noun_to_verb_ratio(self, lemma):
        noun_freq = self.pos_freq(lemma, 'noun')
        verb_freq = self.pos_freq(lemma, 'verb')
        return _smoothed_log_ratio(noun_freq, verb_freq)

    def derivational_family(self, target, right=False, 
                            include_multiword=False):
        '''
        right: If True, only count derived words that have the target word
        as its leftmost morpheme (e.g. for "think" include "thinker" but
        not "rethink").

        include_multiword: If this option is set to False (default), only
        one-word lemmas are considered. For example, "sleep in" and
        "beauty-sleep" are ignored, but "oversleep" and "sleepwalk" are
        included.
        '''
        families = self._get_derivational_families(right, include_multiword)
        family = families[target]
        return [self.clx.lemma_by_id(x) for x in family]

    def derivational_entropy(self, target, right=False, smooth=1,
                             include_multiword=False):
        families = self._get_derivational_families(right, include_multiword)
        frequencies = []
        for family_member_id in families[target]:
            frequencies.append(self.clx._lemmas[family_member_id]['Cob'])
        return self.entropy(frequencies, smooth)

    def _get_derivational_families(self, right, include_multiword):
        key = (right, include_multiword)
        families = self._derivational_families.setdefault(key, {})
        if families == {}:
            for lemma_id, lemma in enumerate(self.clx._lemmas):
                multiword = '-' in lemma['Head'] or ' ' in lemma['Head']
                if multiword and not include_multiword:
                    continue
                for parse in lemma['Parses']:
                    morphemes = parse['Imm'].split('+')
                    if right:
                        morphemes = morphemes[:1]
                    for morpheme in morphemes:
                        entry = families.setdefault(morpheme, set())
                        entry.add(lemma_id + 1)
        return families

    def inflectional_entropy(self, lemma, kind='separate_bare', smooth=1,
                             verbose=False):
        '''
        This function collapses across all relevant lemmas, e.g. the noun 
        "build" and the verb "build", or the various "wind" verbs.

        Caution: if there are two ways to express the same inflection, the
        function will treat them as the same cell in the inflection 
        distribution (e.g. "hanged" and "hung"). Probably worth adding this
        as an option in a future version.

        This function supports the following three types of inflectional 
        entropy, but there are many more ways to carve up the various 
        inflections.

        Paradigm 1: separate_bare

        bare forms are separated into nominal and verbal, but the
        verbal bare form is not further differentiated between present 
        plural agreeing form and infinitive

        ache (singular), aches (plural), ache (verb -- infinitive, 
        present tense except third singular),
        aches (3rd singular present),
        aching (participle), ached (past tense),
        ached (participle -- passive and past_tense)

        Paradigm 2: collapsed_bare

        Same as separate_bare but collapsing across bare forms:

        ache (singular noun and all bare verbal forms --
        so all forms with no overt inflection), aches (plural),
        aches (3rd singular present), aching (participle),
        ached (past tense), ached (participles)

        Paradigm 3: no_bare

        Same as collapsed_bare, only without bare form:

        aches (plural), aches (3rd singular present),
        aching (participle), ached (past tense), ached (participles)
        '''

        clx_lemmas = self.clx.lemma_lookup(lemma)
        # Use __builtin__ here in case sum is overshadowed by numpy
        all_wordforms = __builtin__.sum((self.clx.lemma_to_wordforms(clx_lemma) 
                                         for clx_lemma in clx_lemmas), [])

        counter = collections.Counter()

        for wf in all_wordforms:
            infl = wf.FlectType
            freq = wf.Cob
            if (infl[0] == 'present_tense' and infl[1] != '3rd_person_verb' 
                or infl[0] == 'infinitive'):
                counter['bare_verb'] += freq
            if infl[0] == 'singular':
                counter['bare_noun'] += freq
            if infl[0] == 'plural':
                counter['noun_plural'] += freq
            if infl[0] == 'past_tense':
                counter['past_tense'] += freq
            if infl == ['positive']:
                counter['positive'] += freq
            if infl == ['comparative']:
                counter['comparative'] += freq
            if infl == ['superlative']:
                counter['superlative'] += freq
            if infl == ['headword_form']:
                counter['headword_form'] += freq
            if infl == ['present_tense', '3rd_person_verb', 'singular']:
                counter['third_sg'] += freq
            if infl == ['participle', 'present_tense']:
                counter['part_ing'] += freq
            if infl == ['participle', 'past_tense']:
                counter['part_ed'] += freq

        common = ['noun_plural', 'third_sg', 'part_ing', 'part_ed', 
                  'past_tense', 'comparative', 'superlative']
        bare = ['bare_noun', 'bare_verb', 'positive', 'headword_form']
        common_freqs = [counter[i] for i in common if i in counter]
        bare_freqs = [counter[i] for i in bare if i in counter]

        if verbose:
            print counter

        if kind == 'separate_bare':
            return self.entropy(bare_freqs + common_freqs, smooth)
        elif kind == 'collapsed_bare':
            return self.entropy([sum(bare_freqs)] + common_freqs, smooth)
        elif kind == 'no_bare':
            return self.entropy(common_freqs, smooth)
        else:
            raise ValueError('Unknown inflectional entropy kind "%s"' % kind)

    def entropy(self, freq_vec, smoothing_constant=1):
        '''
        This flat smoothing is an OK default but probably not the best idea:
        might be better to back off to the average distribution for the 
        relevant paradigm (e.g. if singular forms are generally twice as likely 
        as plural ones, it's better to use [2, 1] as the "prior" instead of 
        [1, 1]).
        '''
        vec = np.asarray(freq_vec, float) + smoothing_constant
        if sum(vec) == 0:
            return -1
        probs = vec / sum(vec)
        # Make sure we're not taking the log of 0 (by convention if p(x) = 0
        # then p(x) * log(p(x)) = 0 in the definition of entropy)
        probs[probs == 0] = 1
        return -np.sum(probs * np.log2(probs))


def test_all():
    clx = Celex(os.path.expanduser('~/Dropbox/celex_english'))
    clx.load_lemmas()
    clx.load_wordforms()
    clx.map_lemmas_to_wordforms()
    lv = LexVars(clx)
    unique_lemmas = set(x['Head'] for x in clx._lemmas)
    for lemma in unique_lemmas:
        lv.inflectional_entropy(lemma)
