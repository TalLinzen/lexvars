# Lexvars
A package for generating variables for word recognition research, primarily
from the CELEX corpus but from other resources as well.

## Using CELEX
Examples:
```python
>>> from lexvars.celex import Celex
>>> c = Celex(celex_path)
>>> c.load_lemmas()
>>> wind = c.lemma_lookup('wind')
>>> wind
[<CelexLemma 51690 "wind" (noun)>, <CelexLemma 51691 "wind" (noun)>,
<CelexLemma 51692 "wind" (verb)>, <CelexLemma 51693 "wind" (verb)>,
<CelexLemma 51694 "wind" (verb)>]

>>> lightbulb = c.lemma_lookup('lightbulb')
>>> lightbulb[0].Parses
[<CelexMorphParse ['light', 'bulb']>]
>>> dir(lightbulb[0])[:3]
['Attr_A', 'Attr_N', 'C_N']
>>> lightbulb.help('Attr_A')
Is this lemma an adjective which in some contexts can only be used 
attributively? (e.g. "sheer" in "sheer nonsense")
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
[<CelexWordform 10550 "build">, <CelexWordform 10555 "building">,
<CelexWordform 10570 "builds">, <CelexWordform 10581 "built">,
<CelexWordform 102411 "build">, <CelexWordform 102418 "built">,
<CelexWordform 119690 "build">, <CelexWordform 119697 "built">,
<CelexWordform 136600 "build">, <CelexWordform 136607 "built">,
<CelexWordform 152608 "built">]
>>> wfs = _
>>> wfs[-1].FlectType
['participle', 'past_tense']
>>> wfs[-2].FlectType
['past_tense', 'plural']
```

## Derivational family
```python
>>> celex = Celex(celex_path)
>>> celex.load_lemmas()
>>> lv = LexVars(celex)

>>> think_family = lv.derivational_family('think')
>>> think_family
[<CelexLemma 13412 "doublethink" (noun)>,
<CelexLemma 38606 "rethink" (verb)>,
<CelexLemma 47061 "think" (noun)>,
<CelexLemma 47062 "think" (verb)>,
<CelexLemma 47063 "thinkable" (adjective)>,
<CelexLemma 47064 "thinker" (noun)>,
<CelexLemma 3805 "bethink" (verb)>]

>>> lv.derivational_family('think', right=True)
[<CelexLemma 47064 "thinker" (noun)>,
<CelexLemma 47061 "think" (noun)>,
<CelexLemma 47062 "think" (verb)>,
<CelexLemma 47063 "thinkable" (adjective)>]

>>> lv.derivational_family('think', right=True, include_multiword=True)
[<CelexLemma 47072 "think up" (verb)>,
<CelexLemma 47061 "think" (noun)>,
<CelexLemma 47062 "think" (verb)>,
<CelexLemma 47063 "thinkable" (adjective)>,
<CelexLemma 47064 "thinker" (noun)>,
<CelexLemma 47067 "think of" (verb)>,
<CelexLemma 47068 "think out" (verb)>,
<CelexLemma 47069 "think over" (verb)>,
<CelexLemma 47070 "think-tank" (noun)>,
<CelexLemma 47071 "think through" (verb)>]

>>> think_family[0].help('Cob')
Frequency in the COBUILD corpus (17.9m words)

>>> [x.Cob for x in think_family]
[2, 32, 0, 35874, 2, 136, 5]

>>> lv.derivational_entropy('think')
0.17897018795918829

>>> lv.inflectional_entropy('think')
1.5716274042735443
```
