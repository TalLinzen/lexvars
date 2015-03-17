# Author: Tal Linzen <linzen@nyu.edu>
# 2011-2015
# License: BSD (3-clause)

import bz2
import csv
import itertools
import math
import os
import pickle
import re


regexp = re.compile(r'#S\(EPATTERN.*?\(VSUBCAT (?P<frame>.*?)\)'
                    r'.*?CLASSES \((?P<class>\d+) (?P<classfreq>\d+)\)'
                    r'.*?RELFREQ (?P<relfreq>.*?) :FREQCNT (?P<freqcnt>\d*)',
                    re.DOTALL)

class Valex(object):
    '''
    Reads a subcategorization lexicon from VALEX (Korhonen et al., 2006),
    and calculated subcategorization frequencies.

    Korhonen, A., Krymolowski, Y., & Briscoe, T. (2006). A large 
    subcategorization lexicon for natural language processing applications.
    In Proceedings of LREC (Vol. 6).

    Typical usage:
    >> vlx = Valex(path_to_lexicon)
    >> vlx.load_all_verbs()
    >> print vlx.verbs['squash']
    ...
    >> vlx.write_csv(path_to_csv_file)

    Or:
    >> vlx = Valex(path_to_lexicon)
    >> vlx.read_csv(path_to_csv_file)
    '''

    def __init__(self, path, collapse_anlt=False):
        '''
        path: directory where .lex or .lex.bz2 files are located; for example,
            valex_root/release/lexicons/lex-lrec5

        collapse_anlt: if true, use the coarse grained distinctions in ANLT,
            rather than the many distinctions made by VALEX, which 
            distinguishes more than a 100
        '''
        self.verbs = {}
        self.path = path
        self.collapse_anlt = collapse_anlt

    def entropy(self, verb):
        result = 0
        for frame in verb:
            freq = frame['relfreq']
            result += -freq * math.log(freq) / math.log(2)
        return result

    def load_all_verbs(self, progress=True):
        verb_files = os.listdir(self.path)
        for i, verb_file in enumerate(verb_files):
            if progress and i % 500 == 0:
                print i
            fname_parts = verb_file.split('.')
            if fname_parts[-1] in ['bz2', 'lex']:
                filename = os.path.join(self.path, verb_file)
                self.verbs[fname_parts[0]] = self.read_lex_file(filename)

    def read_lex_file(self, filename):
        _, ext = os.path.splitext(filename) 
        if ext == '.bz2':
            s = bz2.BZ2File(filename).read()
        else:
            s = open(filename).read()

        matches = []
        for match in regexp.finditer(s):
            d = match.groupdict()
            d['freqcnt'] = int(d['freqcnt'])
            d['relfreq'] = float(d['relfreq'])
            matches.append(d)

        if self.collapse_anlt:
            collapsed = []
            key = lambda x: x['frame']
            matches.sort(key=key)
            for frame, g in itertools.groupby(matches, key):
                l = list(g)
                collapsed.append({'frame': frame,
                                  'freqcnt': sum(x['freqcnt'] for x in l),
                                  'relfreq': sum(x['relfreq'] for x in l)})
            return collapsed
        else:
            return matches
        
    def write_csv(self, output_filename):
        f = open(output_filename, 'w')
        writer = csv.writer(f)
        writer.writerow(['verb', 'frame', 'relfreq', 'freqcnt'])
        for verb, frames in self.verbs.items():
            for frame in frames:
                writer.writerow([verb, frame['frame'], frame['relfreq'],
                                 frame['freqcnt']])
        f.close()

    def read_csv(self, filename):
        reader = csv.DictReader(open(filename))
        self.verbs = {}
        for row in reader:
            row['freqcnt'] = int(row['freqcnt'])
            row['relfreq'] = float(row['relfreq'])
            dict_entry = self.verbs.setdefault(row.pop('verb'), [])
            dict_entry.append(row)


def generate_all_csvs(input_path, output_path):
    for lexicon in os.listdir(input_path):
        for collapse in [True, False]:
            print lexicon, collapse
            vlx = Valex(os.path.join(input_path, lexicon), collapse)
            vlx.load_all_verbs()
            filename = '%s%s.csv' % (lexicon, '_anlt' if collapse else '')
            vlx.write_csv(os.path.join(output_path, filename))


class ValexRelativeEntropy(object):
    '''
    Calculate the Kullback-Leibler divergence between individual verbs'
    subcategorization distribution and the average subcategorization
    distribution in the language (i.e., averaged across all verbs, weighted
    by the verbs' frequency). Requires Celex for lemma frequencies. See:

    Linzen, T. Marantz, A., & Pylkkanen, L. Syntactic context effects in
    visual word recognition: An MEG study. The Mental Lexicon 8(2), 117-139.

    Typical usage:
    >> clx = Celex(path_to_celex)
    >> vlx = Valex(path_to_valex)
    >> vre = ValexRelativeEntropy(clx, vlx)
    >> vre.build_reference_distribution()
    >> vre.calculate_relative_entropies()
    >> print vre.relative_entropies['squash']
    0.569
    '''

    CELEX_VERB = '4'

    def __init__(self, clx, vlx):
        self.clx = clx
        self.vlx = vlx

    def build_reference_distribution(self):
        counts = {}
        self.clx.load_lemmas()
        for verb, frames in self.vlx.verbs.items():
            lemmas = self.clx._lemma_lookup.get(verb)
            if lemmas is None:
                continue
            relevant_lemmas = [x for x in lemmas if
                               x['ClassNum'] == self.CELEX_VERB]
            freq = sum(int(x['CobMln']) for x in relevant_lemmas)
            for frame in frames:
                current = counts.get(frame['frame'], 0)
                counts[frame['frame']] = current + freq * frame['relfreq']

        total = float(sum(counts.values()))
        self.reference = {}
        for frame, count in counts.items():
            self.reference[frame] = count / total

    def calculate_relative_entropies(self):
        self.relative_entropies = {}
        for verb, verb_frames in self.vlx.verbs.items():
            self.relative_entropies[verb] = 0
            for frame, reference_prob in self.reference.items():
                results = [x for x in verb_frames if x['frame'] == frame]
                verb_prob = (0 if len(results) == 0 else
                                  results[0]['relfreq'])
                if verb_prob > 0:
                    ratio = math.log(verb_prob / reference_prob) / math.log(2) 
                    self.relative_entropies[verb] += verb_prob * ratio
