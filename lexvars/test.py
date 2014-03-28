execfile('celex.py')
execfile('lexvars.py')
orig = os.path.expanduser('~/Dropbox/4LexDec/stimuli/1morph_1syll_restricted.csv')
full = os.path.expanduser('~/Dropbox/4LexDec/stimuli/all_restricted.csv')

if 'clx' not in globals():
    clx = Celex(os.path.expanduser('~/Dropbox/celex_english'))
    clx.load_lemmas()
    clx.load_wordforms()
    clx.map_lemmas_to_wordforms()

lv = LexVars(clx)
