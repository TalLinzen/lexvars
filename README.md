Package for generating variables for word recognition research.

Examples:
```python
>>> from lexvars.celex import Celex
>>> c = Celex(celex_path)
>>> c.load_lemmas()
>>> wind = c.lemma_lookup('wind')
>>> wind
[<CelexLemma 51690 "wind" (noun)>, <CelexLemma 51691 "wind" (noun)>, <CelexLemma 51692 "wind" (verb)>, <CelexLemma 51693 "wind" (verb)>, <CelexLemma 51694 "wind" (verb)>]

>>> lightbulb = c.lemma_lookup('lightbulb')
>>> lightbulb[0].Parses
[<CelexMorphParse ['light', 'bulb']>]
>>> dir(lightbulb[0])[:3]
['Attr_A', 'Attr_N', 'C_N']
>>> lightbulb.help('Attr_A')
Is this lemma an adjective which in some contexts can only be used attributively? (e.g. "sheer" in "sheer nonsense")
>>> lightbulb[0].Attr_A
False

>>> c.load_wordforms()
>>> windows = c.wordform_lookup('windows')
>>> windows[0].FlectType
['plural']
>>> windows[0].Cob
1212

>>> c.map_lemmas_to_wordforms()
>>> c.lemma_to_wordforms(c.lemma_lookup('build')[1])
[<CelexWordform 10550 "build">, <CelexWordform 10555 "building">, <CelexWordform 10570 "builds">, <CelexWordform 10581 "built">, <CelexWordform 102411 "build">, <CelexWordform 102418 "built">, <CelexWordform 119690 "build">, <CelexWordform 119697 "built">, <CelexWordform 136600 "build">, <CelexWordform 136607 "built">, <CelexWordform 152608 "built">]
>>> wfs = _
>>> wfs[-1].FlectType
['participle', 'past_tense']
>>> wfs[-2].FlectType
['past_tense', 'plural']
```
