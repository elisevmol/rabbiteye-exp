#!/usr/bin/python
import json
import re
import sys
from unidecode import unidecode

STOPWORDS = '''
    het de deze
    en of om te hier nog ook al
    in van voor mee per als tot uit bij
    waar waardoor waarvan wanneer
    je uw ze zelf jezelf
    ca bijv bijvoorbeeld
    is bevat hebben kunnen mogen zullen willen
    gemaakt aanbevolen
    belangrijk belangrijke heerlijk heerlijke handig handige dagelijks dagelijkse
    gebruik allergieinformatie bijdrage smaak hoeveelheid
'''.split()


def clean(s):
    if s is None: return None
    # @todo keep '0.50%' and the like (or extract separately) - relevant for alcohol-free
    s = unidecode(s).strip()
    s = re.sub(r'[^A-Za-z0-9\'\s]', '', s, flags=re.MULTILINE)
    s = re.sub(r'\s+', ' ', s, flags=re.MULTILINE)
    return s

def get_brand_name(j):
    '''Return brand name from brand_name or brand_url'''
    s = j.get('brand_name', '').strip()
    if s == '':
        s = j.get('brand_url', '').strip()
        s = re.sub(r'(\Ahttps?://(www\.)?|\Awww\.|\.\w{2,3}\/?\Z)', '', s, flags=re.MULTILINE|re.IGNORECASE)
    return s


def f_name(j):
    f = clean(j.get('name', '').lower())
    # strip brand from front of name, would be twice featurized
    brand_name_clean = clean(get_brand_name(j).lower())
    if brand_name_clean != '' and f.startswith(brand_name_clean):
        f = f[len(brand_name_clean):].strip()

    if f == '': return []
    return f.split()


def f_brand(j):
    f = clean(get_brand_name(j))

    if f == '': return []
    return ['BRN:' + f]


def f_first_ingredient(j):
    if 'ingredients' not in j or len(j['ingredients']) == 0: return []

    f = j['ingredients'][0].strip().lower()

    # we're more interested in whether the ingredient is composed, than its exact content
    if re.search(r'[({:;,\n]', f, flags=re.MULTILINE):
        f = '(COMPOSED)'

    f = clean(f)

    if f == '': return []
    return ['ING:' + f]


def tokenize(j):
    '''Returns array of tokens for product nut dict'''
    return f_name(j) + f_brand(j) + f_first_ingredient(j)

def tokenize_all(data):
    '''Returns a dict including the tokens, usage and product_id for all products nuts'''
    id_tokens = []
    for j in data:

        tokens = tokenize(j)
        tokens = filter(lambda s: s not in STOPWORDS, tokens)
        tokens = filter(lambda s: len(s) > 1, tokens)
        
        id_tokens.append({'id': j['id'], 'tokens': tokens, 'usage':j['usage'], 'product_id':j['product_id']})
        
    return id_tokens