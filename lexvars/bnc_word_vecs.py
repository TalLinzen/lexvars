import collections
import json
import lxml
import math
import os
import re
import time

import nltk
import nltk.corpus
from nltk.corpus.reader.wordnet import NOUN, VERB, ADJ, ADV


class BNCWordVecs(object):
    '''
    Punctuation, capitalization, and sentence/utterance boundary information are
    removed.

    To generate Contextual Distinctiveness (McDonald and Shillcock 2001):

    b = BNCWordVecs([target_word_file])
    (Target word file is a text file that has each word in a separate line)

    # If creating context words from most frequent words in corpus,
    # first pass:
    b.read_all()
    b.save_context_words('/tmp/context_words.txt')

    # If creating target word list from most frequent words in corpus (rather then
    # a list of the particular words you're interested in), run also:
    b.save_target_words('/tmp/target_words.txt')

    # Second pass. Start here if first pass was not needed. Note that context
    # words need to be dictionary of the form {word: frequency}, dumped in JSON
    # format.
    b.load_target_words('/tmp/target_words.txt')
    b.load_context_words('/tmp/context_words.txt')   # if first pass skipped
    b.initialize_matrix()
    b.read_all(process=True)
    b.calculate_cd()

    The CD values will be in b.cds.

    McDonald, S. A. & Shillcock, R. C. 2001. Rethinking the word frequency
    effect: The neglected role of distributional information in lexical
    processing. Language and Speech.
    '''

    pos_map = {'A': ADV, 'J': ADJ, 'N': NOUN, 'V': VERB}
    project_root = os.path.expanduser('~/Dropbox/4LexDec/stimuli/distsem')
    corpus_root = os.path.expanduser('~/Desktop/BNC/Texts')
    context_words_file = 'context_words.json'
    target_words_file = 'target_words.json'
    stored_all = 'stored_all.json'
    vectors_file = 'vectors.json'
    cds_file = 'cds.json'
    word_regex = re.compile('<w (.+?)>(.+?)(?=<)')

    def __init__(self, corpus_root, stopwords=None, n_context_words=500,
                 n_target_words=50000, window_size=5, max_words=None):
        '''
        '''
        self.n_context_words = n_context_words
        self.n_target_words = n_target_words
        self.window_size = window_size
        self.context_words = None
        self.target_words = None
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.frequencies = collections.Counter()
        self.vectors = {}
        self.total_n_words = 0
        self.max_words = max_words
        if stopwords is None:
            self.stopwords = set(nltk.corpus.stopwords.words('english'))
        else:
            self.stopwords = set(stopwords)

    def initialize_matrix(self, bigrams=False):
        if not bigrams:
            keys = self.context_words.keys()
            for tw in self.target_words:
                self.vectors[tw] = dict((cw, 0) for cw in keys)
        elif bigrams:
            for tw in self.target_words:
                self.vectors[tw] = {}

    def read_file(self, filename, bigrams=False):
        contents = open(filename).read()
        words = self.word_regex.finditer(contents)
        lemmatized, lemma_pos = [], []

        # remove punctuation, capitalization, and sentence/utterance
        # boundary information
        for word in words:
            self.total_n_words += 1
            if word.group(2) is None:
                continue
            normalized = word.group(2).lower().strip()
            if not bigrams:
                if (normalized in self.stopwords or normalized in ['', "n't"] or
                        normalized[0] == "'"):
                    continue
            penn_pos = word.group(1)
            wordnet_pos = self.pos_map.get(penn_pos[0], VERB)
            lemma = self.lemmatizer.lemmatize(normalized, wordnet_pos)
            lemmatized.append(lemma)
            lemma_pos.append(wordnet_pos)

        self.frequencies.update(lemmatized)
        return lemmatized, lemma_pos

    def process(self, words):
        is_context_word = [x in self.context_words for x in words]
        for i in range(len(words)):
            if words[i] not in self.target_words:
                continue
            lower = max(0, i - self.window_size)
            upper = min(len(words), i + self.window_size + 1)
            for j in range(lower, i) + range(i + 1, upper):
                if is_context_word[j]:
                    self.vectors[words[i]][words[j]] += 1

    def process_bigrams(self, words, verbs_only=False, lemma_pos=None):
        is_verb = [x == VERB for x in lemma_pos]
        for i in range(len(words)-1):
            if words[i] not in self.target_words or (verbs_only and not is_verb[i]):
                continue
            self.vectors[words[i]].setdefault(words[i+1], 0)
            self.vectors[words[i]][words[i+1]] += 1

    def all_files(self):
        for f1 in os.listdir(self.corpus_root):
            f1_full = os.path.join(self.corpus_root, f1)
            if os.path.isdir(f1_full):
                for f2 in os.listdir(f1_full):
                    print f2, self.total_n_words
                    f2_full = os.path.join(f1_full, f2)
                    if os.path.isdir(f2_full):
                        for f3 in os.listdir(f2_full):
                            if f3[0] != '.':
                                f3_full = os.path.join(f2_full, f3)
                                yield f3_full
                                if (self.max_words is not None and
                                    self.total_n_words > self.max_words):
                                    return

    def calculate_cd(self):
        self.cds = {}
        total_freq = sum(self.context_words.values())
        p_context_words = dict((x, float(y) / total_freq) for x, y in
                               self.context_words.items())

        for w, vector in self.vectors.items():
            total_freq = float(sum(vector.values()))
            if total_freq == 0:
                cd = None
            else:
                cd = 0
                for cw, freq in vector.items():
                    pcw = freq / total_freq
                    pc = p_context_words[cw]
                    if pcw == 0:
                        term = 0
                    else:
                        term = pcw * (math.log(pcw / pc) / math.log(2))
                    cd += term
            self.cds[w] = cd

    def calculate_entropy(self):
        self.entropies = {}

        for w, vector in self.vectors.items():
            total_freq = float(sum(vector.values()))
            if total_freq == 0:
                ent = None
            else:
                ent = 0
                for cont, freq in vector.items():
                    relfreq = freq / total_freq
                    if relfreq == 0:
                        term = 0
                    else:
                        term = -1 * relfreq * (math.log(relfreq) / math.log(2))
                    ent += term
            self.entropies[w] = ent

    def read_all(self, process=False, bigrams=False, verbs_only=False):
        self.total_n_words = 0
        if process:
            self.initialize_matrix(bigrams=bigrams)
        for filename in self.all_files():
            words, pos = self.read_file(filename, bigrams=bigrams)
            if process:
                if not bigrams:
                    self.process(words)
                elif bigrams:
                    self.process_bigrams(words, verbs_only=verbs_only, lemma_pos=pos)

    def save_context_words(self, filename):
        common = self.frequencies.most_common(self.n_context_words)
        f = open(filename, 'w')
        json.dump(common, f)
        self.context_words = dict(common)

    def load_context_words(self, filename):
        f = open(filename)
        self.context_words = dict(json.load(f))

    def save_target_words(self, filename, n_most_common=1000):
        common = self.frequencies.most_common(self.n_target_words)
        common_words = [x[0] for x in common]
        self.target_wrods = set(common_words)
        f = open(filename, 'w')
        f.write('\n'.join(common_words))

    def load_target_words(self, filename):
        f = open(filename)
        self.target_words = set([x.strip() for x in f.readlines()])

    def save_all(self):
        f = open(os.path.join(self.project_root, self.stored_all), 'w')
        json.dump(self.words, f)

    def load_all(self):
        f = open(os.path.join(self.project_root, self.stored_all))
        self.words = json.load(f)

    def save_vectors(self, filename):
        f = open(filename)
        json.dump(self.vectors, f)

    def save_cds(self):
        f = open(os.path.join(self.project_root, self.cds_file), 'w')
        json.dump(self.cds, f)


def test(corpus_root):

    b = BNCWordVecs(corpus_root, max_words=1000000)

    # First pass
    b.read_all()
    b.save_context_words('/tmp/context_words.txt')
    b.save_target_words('/tmp/target_words.txt')

    # Second pass
    b.load_context_words('/tmp/context_words.txt')
    b.load_target_words('/tmp/target_words.txt')
    b.read_all(process=True)
    b.calculate_cd()

    return b
