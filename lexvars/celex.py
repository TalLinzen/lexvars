# Author: Tal Linzen <linzen@nyu.edu>
# 2011-2014
# License: BSD (3-clause)

import os

db_fields = {
    'efl': ['IdNum', 'Head', 'Cob', 'CobDev', 'CobMln', 'CobLog', 'CobW',
            'CobWMln', 'CobWLog', 'CobS', 'CobSMln', 'CobSLog'],
    'esl': ['IdNum', 'Head', 'Cob', 'ClassNum', 'C_N', 'Unc_N', 'Sing_N',
            'Plu_N', 'GrC_N', 'GrUnc_N', 'Attr_N', 'PostPos_N', 'Voc_N',
            'Proper_N', 'Exp_N', 'Trans_V', 'TransComp_V', 'Intrans_V',
            'Ditrans_V', 'Link_V', 'Phr_V', 'Prep_V', 'PhrPrep_V', 'Exp_V',
            'Ord_A', 'Attr_A', 'Pred_A', 'PostPos_A', 'Exp_A', 'Ord_ADV',
            'Pred_ADV', 'PostPos_ADV', 'Comb_ADV', 'Exp_ADV', 'Card_NUM',
            'Ord_NUM', 'Exp_NUM', 'Pers_PRON', 'Dem_PRON', 'Poss_PRON',
            'Refl_PRON', 'Wh_PRON', 'Det_PRON', 'Pron_PRON', 'Exp_PRON',
            'Cor_C', 'Sub_C'],
    'efw': ['IdNum', 'Word', 'IdNumLemma', 'Cob', 'CobDev', 'CobMln',
            'CobLog', 'CobW', 'CobWMln', 'CobWLog', 'CobS', 'CobSMln',
            'CobSLog'],
    'emw': ['IdNum', 'Word', 'Cob', 'IdNumLemma', 'FlectType', 'TransInfl'],
    'epw': ['IdNum', 'Word', 'Cob', 'IdNumLemma', 'PronCnt', 'PronStatus',
            'PhonStrsDISC', 'PhonCVBr', 'PhonSylBCLX'],
}

field_keys = {

    'ClassNum': {
        1: 'noun',
        2: 'adjective',
        3: 'number',
        4: 'verb',
        5: 'article',
        6: 'pronoun',
        7: 'adverb',
        8: 'preposition',
        9: 'conjunction',
        10: 'interjection',
        11: 'single_contraction',
        12: 'complex_contraction',
        13: '?',   # Not from the docs
        14: '??',
        15: '???'
    },

    'FlatSA': {
        'S': 'stem',
        'A': 'affix',
        'F': 'inflected_stem',
    },

    'FlectType': {
        'S': 'singular',
        'P': 'plural',
        'b': 'positive',
        'c': 'comparative',
        's': 'superlative',
        'i': 'infinitive',
        'p': 'participle',
        'e': 'present_tense',
        'a': 'past_tense',
        '1': '1st_person_verb',
        '2': '2nd_person_verb',
        '3': '3rd_person_verb',
        'r': 'rare_form',
        'X': 'headword_form'
    },

    'ImmAllo': {
        'B': 'blend',
        'C': 'clipping',
        'D': 'derivational',
        'F': 'flectional',
        'Z': 'conversion',
        'N': 'none'
    },

    'ImmSA': {
        'S': 'stem',
        'A': 'affix',
        'F': 'inflected_stem',
    },

    'ImmSubCat': {
        'N': 'noun',
        'A': 'adjective',
        'Q': 'numeral',
        '0': 'unmarked_transitivity_verb',
        '1': 'intrans_verb',
        '2': 'trans_verb',
        '3': 'trans_and_intrans_verb',
        'D': 'article',
        'O': 'pronoun',
        'B': 'adverb',
        'P': 'preposition',
        'C': 'conjunction',
        'I': 'interjection',
        'S': 'single_contraction',
        'T': 'complex_contraction',
        'x': 'affix',
        '?': '?'
    },

    'Lang': {
        'A': 'American',
        'F': 'French',
        'B': 'British',
        'D': 'German',
        'G': 'Greek',
        'I': 'Italian',
        'S': 'Spanish',
        'L': 'Latin',
        '': ''
    },

    'MorphStatus': {
        'C': 'complex',            # sandbank
        'M': 'monomorphemic',      # camel
        'Z': 'zero_derivation',    # abandon
        'F': 'contracted',         # I've
        'I': 'irrelevant',         # meow
        'O': 'obscure',            # dedicate
        'R': 'may_include_a_root', # imprimatur
        'U': 'undetermined'        # hinterland
    },

    'StrucAllo': {
        'B': 'blend',
        'C': 'clipping',
        'D': 'derivational',
        'F': 'flectional',
        'Z': 'conversion',
        'N': 'none'
    },

    'PronStatus': {
        'P': 'Primary',
        'S': 'Secondary'
    }

}


class CelexRecord(object):
    '''
    Base class for CelexLemma and CelexWordform
    '''

    _frequency_fields = [
        ('Cob', int, 'Frequency in the COBUILD corpus (17.9m words)'),
        ('CobDev', int, 'How good is the frequency estimate, when the '
         'disambiguation was not done by hand; if higher than Cob, not a '
         'good sign'),
        ('CobMln', int, 'Frequency per words million'),
        ('CobLog', float, 'Base 10 logarithm of frequency per million words'),
        ('CobS', int, 'Frequency in spoken part of corpus (1.3m words)'),
        ('CobSMln', int, 'Frequency per million words in spoken part of '
         'corpus (1.3m words)'),
        ('CobSLog', float, 'Base 10 logarithm of frequency per million words '
         'in spoken part of corpus (1.3m words)'),
        ('CobW', int, 'Frequency in written part of corpus (16.6m words)'),
        ('CobWMln', int, 'Frequency per million words in written part of '
         'corpus (1.3m words)'),
        ('CobWLog', float, 'Base 10 logarithm of frequency per million words '
         'in written part of corpus (1.3m words)')
    ]

    def __init__(self, d):
        self._d = d

        fields = self._subclass_fields
        if self._has_frequency:
            fields += self._frequency_fields

        self._documentation = {}

        for field, field_type, doc in fields:
            if field not in d:
                continue
            self._documentation[field] = doc
            if field_type == 'decoded_list':
                setattr(self, field, [field_keys[field][x] for x in d[field]])
            elif field_type == 'decoded_char':
                if len(d[field]) > 1:
                    raise ValueError('More than one character in field "%s": '
                                     '"%s"' % (field, d[field]))
                setattr(self, field, field_keys[field][d[field]])
            elif field_type == 'decoded_num':
                setattr(self, field, field_keys[field][int(d[field])])
            elif field_type == 'boolean':
                if d[field] not in ['Y', 'N']:
                    raise ValueError('Unexpected value for boolean field "%s": '
                                     '"%s"' % (field, d[field]))
                setattr(self, field, d[field] == 'Y')
            else:
                setattr(self, field, field_type(d[field]))

        converted = set(x for x in self.__dict__.keys() if x[0] != '_')
        diff = set(d.keys()) - converted
        if len(set(diff)) > 0:
            raise ValueError('Unconverted fields: %r' % diff)

    def help(self, field):
        print self._documentation[field]


class CelexMorphParse(CelexRecord):

    _subclass_fields = [
        ('Comp', 'boolean', 'This row contains a noun-verb-affix compound '
         'which is analysed as a compound'),
        ('Def', 'boolean', 'This is the default analysis (simplest, most '
         'useful etc)'),
        ('Der', 'boolean', 'This row contains a noun-verb-affix compound '
         'which is analysed as a derivation'),
        ('DerComp', 'boolean', 'This row contains a noun-verb-affix compound '
         'which is analysed as a derivational compound'),
        ('FlatSA', 'decoded_list', 'Stem / affix status of constituents'),
        ('ImmAllo', 'decoded_char', 'Stem allophony (clear -> clarify)'),
        ('ImmInfix', 'boolean', 'Infixation, e.g. looker-on from look on'),
        ('ImmOpac', 'boolean', 'Morphologically / semantically opaque '
         '(accordion)'),
        ('ImmRevers', 'boolean', 'Reversed, e.g. offputting from put off'),
        ('ImmSubCat', 'decoded_list', 'Syntactic categories of constituents'),
        ('ImmSubst', 'boolean', 'Affix substitution in stem (action -> '
         'active)'),
        ('ImmSA', 'decoded_list', 'Stem / affix status of constituents'),
        ('NVAffComp', 'boolean', 'Noun-verb-affix compound (typesetter)'),
        ('StrucAllo', 'decoded_list', 'Stem allophony at any level'),
        ('StrucLab', str, 'Structured segmentation with word class label'),
        ('StrucOpac', 'boolean', 'Semantic opacity (at any level)'),
        ('StrucSubst', 'boolean', 'Affix substitution (at any level)'),
        ('TransDer', str, 'Sound changes in morphological derivation:'
         'undersized is given as #-e#, since nothing happens to the first '
         'morpheme under-, the final e of the second morpheme size is removed, '
         'and nothing happens to the last morpheme -ed.')
    ]

    _has_frequency = False

    def __init__(self, d):
        self.Imm = d['Imm'].split('+')
        super(CelexMorphParse, self).__init__(d)

    def __repr__(self):
        return '<CelexMorphParse %s>' % self.Imm


class CelexPronunciation(CelexRecord):

    _subclass_fields = [
        ('PronStatus', 'decoded_char', 'Status of pronunciation'),
        ('PhonStrsDISC', str, 'Syllabified and stressed DISC transcription'),
        ('PhonCVBr', str, 'Phonetic CV pattern, with brackets'),
        ('PhonSylBCLX', str, 'Syllabified CELEX char set, brackets')
    ]

    _has_frequency = False

    def __repr__(self):
        return '<CelexPronunciation %s>' % self.PhonSylBCLX


class CelexLemma(CelexRecord):

    _subclass_fields = [
        ('Attr_A', 'boolean', 'Is this lemma an adjective which in some '
         'contexts can only be used attributively? (e.g. "sheer" in ' 
         '"sheer nonsense"'),
        ('Attr_N', 'boolean', 'Can this noun be used attributively? '
         '(e.g. "machine" in "machine translation"'),
        ('Card_NUM', 'boolean', 'Cardinal number?'),
        ('ClassNum', 'decoded_num', 'Syntactic category'),
        ('C_N', 'boolean', 'Countable noun?'),
        ('Comb_ADV', 'boolean', 'Can the adverb be combined with another '
         'adverb or preposition (e.g. "all" in "all alone")?'),
        ('Cor_C', 'boolean', 'Coordinating conjunction ("and", "or", "but")'),
        ('Dem_PRON', 'boolean', 'Demonstrative pronoun ("this")'),
        ('Det_PRON', 'boolean', 'Pronoun that can be used as a determiner'),
        ('Ditrans_V', 'boolean', 'Ditransitive verb?'),
        ('Exp_A', 'boolean', 'Adjective limited to a particular phrase '
         '(e.g. "bated" in "bated breath")'),
        ('Exp_ADV', 'boolean', 'Adverb limited to a particular phrase '
         '(e.g. "amok" in "run amok")'),
        ('Exp_N', 'boolean', 'Noun limited to a single phrase ("loggerheads")'),
        ('Exp_NUM', 'boolean', 'Number used as part of an expression ("sixty '
         'four" in "sixty four thousand dollar question")'),
        ('Exp_PRON', 'boolean', 'Pronoun used a part of an expression ("aught" '
         'in "for aught I know")'),
        ('Exp_V', 'boolean', 'Verb limited to a single phrase ("toe" in "toe '
         'the line"'),
        ('GrC_N', 'boolean', 'Collective noun that has both a singular and a '
         'plural form ("government")?'),
        ('GrUnc_N', 'boolean', 'Is this lemma a collective noun that only '
         'has a singular form, and not a plural form?'),
        ('Head', str, ''),
        ('IdNum', int, ''),
        ('Intrans_V', 'boolean', 'Intransitive verb?'),
        ('Lang', 'decoded_char', 'Language'),
        ('Link_V', 'boolean', 'Linking verb ("be")?'),
        ('MorphCnt', int, 'Number of morphological analyses'),
        ('MorphStatus', 'decoded_char', 'Morphological status'),
        ('Ord_A', 'boolean', 'Ordinary adjective (can be used both '
         'attributively and predicatively)?'),
        ('Ord_ADV', 'boolean', 'Ordinary adverb'),
        ('Ord_NUM', 'boolean', 'Ordinal number?'),
        ('Pers_PRON', 'boolean', 'Personal pronoun ("he", "them")?'),
        ('Phr_V', 'boolean', 'Phrasal verb ("speak out")?'),
        ('Plu_N', 'boolean', 'Lemma occurs in a plural-only form?'),
        ('PhrPrep_V', 'boolean', 'Phrasal verb + prep ("walk away with")'),
        ('Poss_PRON', 'boolean', 'Possessive pronoun ("her", "hers")'),
        ('PostPos_A', 'boolean', 'Postpositive adjective ("life everlasting")'),
        ('PostPos_ADV', 'boolean', 'Postpositive adverb ("adrift" in "the boat '
         'is adrift")'),
        ('PostPos_N', 'boolean', 'Postpositive noun ("proof" in "forty two '
         'proof")'),
        ('Pron_PRON', 'boolean', 'Pronominal pronoun that can replace a noun, '
         'e.g. "mine" in "mine is better"'),
        ('PronCnt', int, 'Number of pronunciations'),
        ('Pred_A', 'boolean', 'Predicative adjective ("awake")'),
        ('Pred_ADV', 'boolean', 'Predicative adverb ("adrift")'),
        ('Prep_V', 'boolean', 'Verb with preposition ("minister to")'),
        ('Proper_N', 'boolean', 'Proper noun'),
        ('Refl_PRON', 'boolean', 'Reflexive pronoun ("yourself")'),
        ('Sing_N', 'boolean', 'Noun that only ever occurs in the singular'),
        ('Sub_C', 'boolean', 'Subordinating conjunction ("because")'),
        ('Trans_V', 'boolean', 'Transitive verb'),
        ('TransComp_V', 'boolean', 'Transitive verb with complement ("find '
         'someone guilty")'),
        ('Unc_N', 'boolean', 'Uncountable noun'),
        ('Voc_N', 'boolean', 'Vocative noun ("chicken!")'),
        ('Wh_PRON', 'boolean', 'Wh pronoun ("who", "howsoever")')
    ]

    _has_frequency = True

    def __init__(self, d):
        self.Parses = [CelexMorphParse(x) for x in d['Parses']]
        self.Prons = [CelexPronunciation(x) for x in d['Prons']]
        super(CelexLemma, self).__init__(d)

    def __repr__(self):
        if hasattr(self, 'ClassNum'):
            pos = ' (%s)' % self.ClassNum
        else:
            pos = ''
        return '<CelexLemma %d "%s"%s>' % (self.IdNum, self.Head, pos)


class CelexWordform(CelexRecord):

    _subclass_fields = [
        ('Word', str, ''),
        ('TransInfl', str, 'inflectional transformation from base to wordform; '
         'e.g., for "abiding", this will be @-e+ing @: first the final -e of '
         '"abide" is removed, and then the suffix -ing is added.'),
        ('IdNum', int, ''),
        ('IdNumLemma', int, ''),
        ('FlectType', 'decoded_list', 'List of inflectional categories'),
        ('PronCnt', int, 'Number of pronunciations'),
        ('Head', str, 'Head')
    ]

    _has_frequency = True

    def __init__(self, d):
        self.Prons = [CelexPronunciation(x) for x in d['Prons']]
        super(CelexWordform, self).__init__(d)

    def __repr__(self):
        return '<CelexWordform %d "%s">' % (self.IdNum, self.Word)


class Celex(object):
    '''
    Supported DBs are 's' (syntax), 'm' (morphology), 'f' (frequency)
    and 'p' (phonology)
    '''

    eml_base = ['IdNum', 'Head', 'Cob', 'MorphStatus', 'Lang', 'MorphCnt']

    eml_parse = ['NVAffComp', 'Der', 'Comp', 'DerComp', 'Def', 'Imm', 
                 'ImmSubCat', 'ImmSA', 'ImmAllo', 'ImmSubst', 'ImmOpac',
                 'TransDer', 'ImmInfix', 'ImmRevers', 'FlatSA', 'StrucLab',
                 'StrucAllo', 'StrucSubst', 'StrucOpac']

    epl_base = ['IdNum', 'Head', 'Cob', 'PronCnt']
    epw_base = ['IdNum', 'Head', 'Cob', 'IdNumLemma', 'PronCnt']
    ep_pron = ['PronStatus', 'PhonStrsDISC', 'PhonCVBr', 'PhonSylBCLX']

    supported_dbs = ['s', 'm', 'f', 'p']

    # If a word has more than 4 parses, they don't all fit in
    # the same line. We ignore the additional parses for these
    # words (copyholder, leaseholder, potterer, putterer,
    # southeaster, southwester; see eml/README)
    max_parses = 4
    max_epl_prons = 24
    max_epw_prons = 23

    def __init__(self, celex_english_root, dbs=None):
        self._lemmas = None
        self._wordforms = None
        self._lemmas_to_wordforms = None
        self.celex_english_root = celex_english_root
        if dbs is None:
            self.dbs = self.supported_dbs
        else:
            diff = set(dbs) - set(self.supported_dbs)
            if len(diff) > 0:
                raise ValueError('Unknown DBs %s' % diff)
            self.dbs = dbs

    def load_lemmas(self):
        if self._lemmas is not None:
            return
        l = []
        self._lemmas = self.read_dbs(['e%sl' % db for db in self.dbs])
        self._lemma_lookup = {}
        for lemma in self._lemmas:
            self._lemma_lookup.setdefault(lemma['Head'], []).append(lemma)

    def load_wordforms(self):
        if self._wordforms is not None:
            return
        # No syntax DB for wordforms
        self._wordforms = self.read_dbs(['e%sw' % db for db in self.dbs 
                                         if db != 's'])
        self._wf_lookup = {}
        for wf in self._wordforms:
            self._wf_lookup.setdefault(wf['Word'], []).append(wf)

    def map_lemmas_to_wordforms(self):
        if self._lemmas_to_wordforms is not None:
            return
        self.load_lemmas()
        self.load_wordforms()
        self._lemmas_to_wordforms = [[] for x in range(len(self._lemmas))]
        for wordform in self._wordforms:
            wf_id = int(wordform['IdNum'])
            lemma_id = int(wordform['IdNumLemma'])
            lemma = self._lemmas[lemma_id - 1]
            assert int(lemma['IdNum']) == lemma_id
            self._lemmas_to_wordforms[lemma_id - 1].append(wf_id)

    def read_dbs(self, dbs):
        first_db = self.read_db(dbs[0])
        for other_db_name in dbs[1:]:
            other_db = self.read_db(other_db_name)
            for first, other in zip(first_db, other_db):
                first.update(other)
        return first_db

    def read_db(self, db):
        fname = os.path.join(self.celex_english_root, db, '%s.cd' % db)
        records = []
        for x in open(fname).readlines():
            actual_fields = x.strip().split('\\')
            if db == 'eml':
                n_parses = min(max(1, int(actual_fields[5])), 
                               self.max_parses)
                expected_fields = self.eml_base + n_parses * self.eml_parse
            elif db == 'epl':
                cnt = len(self.epl_base) - 1
                n_prons = min(max(1, int(actual_fields[cnt])), 
                              self.max_epl_prons)
                expected_fields = self.epl_base + n_prons * self.ep_pron
            elif db == 'epw':
                cnt = len(self.epw_base) - 1
                n_prons = min(max(1, int(actual_fields[cnt])),
                              self.max_epw_prons)
                expected_fields = self.epw_base + n_prons * self.ep_pron
            else:
                expected_fields = db_fields[db]

            if len(expected_fields) != len(actual_fields):
                raise ValueError('Number of fields (%d) doesn\'t match '
                                 'expected number (%d)' % 
                                 (len(actual_fields), len(expected_fields)))
            if db == 'eml':
                record = self.parse_eml(actual_fields)
            elif db == 'epl':
                record = self.parse_ep(self.epl_base, self.max_epl_prons,
                                       actual_fields) 
            elif db == 'epw':
                record = self.parse_ep(self.epw_base, self.max_epw_prons,
                                       actual_fields) 
            else:
                record = dict(zip(expected_fields, actual_fields))
            records.append(record)
        return records

    def parse_eml(self, fields):
        record = dict(zip(self.eml_base, fields))
        record['Parses'] = []
        n_parses = min(int(record['MorphCnt']), self.max_parses)
        for i in range(n_parses):
            start = len(self.eml_base) + i * len(self.eml_parse)
            end = len(self.eml_base) + (i + 1) * len(self.eml_parse)
            d = dict(zip(self.eml_parse, fields[start:end]))
            record['Parses'].append(d)
        return record

    def parse_ep(self, ep_base, max_prons, fields):
        record = dict(zip(ep_base, fields))
        record['Prons'] = []
        n_prons = min(int(record['PronCnt']), max_prons)
        for i in range(n_prons):
            start = len(ep_base) + i * len(self.ep_pron)
            end = len(ep_base) + (i + 1) * len(self.ep_pron)
            d = dict(zip(self.ep_pron, fields[start:end]))
            record['Prons'].append(d)
        return record

    def lemma_by_id(self, lemma_id):
        self.load_lemmas()
        return CelexLemma(self._lemmas[lemma_id - 1])

    def lemma_lookup(self, x):
        self.load_lemmas()
        return [CelexLemma(l) for l in self._lemma_lookup[x]]

    def wordform_by_id(self, wf_id):
        self.load_wordforms()
        return CelexWordform(self._wordforms[wf_id - 1])

    def wordform_lookup(self, x):
        self.load_wordforms()
        return [CelexWordform(wf) for wf in self._wf_lookup[x]]

    def lemma_to_wordforms(self, lemma):
        '''
        Takes a CelexLemma object and returns a list of CelexWordform objects
        corresponding to each of the wordforms connected to the lemma
        '''
        self.map_lemmas_to_wordforms()
        return [self.wordform_by_id(wf_id) for wf_id in 
                self._lemmas_to_wordforms[lemma.IdNum - 1]]
