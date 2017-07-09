#!/usr/bin/env python
#
# Tokenizes product nut features.
#
#
# Either import in Python, or pipe a jsonlines file with product nuts, like
#
#    cat data/product_nuts.jsonl | python featurize.py >data/product_nut_features.jsonl
#
import json
import re
import sys
from tqdm import tqdm_notebook
from unidecode import unidecode

STOPWORDS = '''
    het de deze en of om te hier nog ook al in van voor mee per als tot uit bij waar waardoor waarvan wanneer
    je uw ze zelf jezelf ca bijv bijvoorbeeld is bevat hebben kunnen mogen zullen willen gemaakt aanbevolen
    belangrijk belangrijke heerlijk heerlijke handig handige dagelijks dagelijkse
    gebruik allergieinformatie bijdrage smaak hoeveelheid aan aangaande aangezien achter achterna afgelopen 
    al aldaar aldus alhoewel alias alle allebei alleen alsnog altijd altoos ander andere anders anderszins 
    behalve behoudens beide beiden ben beneden bent bepaald betreffende bij binnen binnenin boven bovenal 
    bovendien bovengenoemd bovenstaand bovenvermeld buiten daar daarheen daarin daarna daarnet daarom daarop 
    daarvanlangs dan dat de die dikwijls dit door doorgaand dus echter eer eerdat eerder eerlang eerst elk elke 
    en enig enigszins enkel er erdoor even eveneens evenwel gauw gedurende geen gehad gekund geleden gelijk 
    gemoeten gemogen geweest gewoon gewoonweg haar had hadden hare heb hebben hebt heeft hem hen het hierbeneden 
    hierboven hij hoe hoewel hun hunne ik ikzelf in inmiddels inzake is jezelf jij jijzelf jou jouw jouwe juist
    jullie kan klaar kon konden krachtens kunnen kunt later liever maar mag meer met mezelf mij mijn mijnent mijner 
    mijzelf misschien mocht mochten moest moesten moet moeten mogen na naar nadat net niet noch nog nogal nu of 
    ofschoon om omdat omhoog omlaag omstreeks omtrent omver onder ondertussen ongeveer ons onszelf onze ook op 
    opnieuw opzij over overeind overigens pas precies reeds rond rondom sedert sinds sindsdien slechts sommige 
    spoedig steeds tamelijk tenzij terwijl thans tijdens toch toen toenmaals toenmalig tot totdat tussen uit 
    uitgezonderd vaak van vandaan vanuit vanwege veeleer verder vervolgens vol volgens voor vooraf vooral 
    vooralsnog voorbij voordat voordezen voordien voorheen voorop vooruit vrij vroeg waar waarom wanneer 
    want waren was wat weer weg wegens wel weldra welk welke wie wiens wier wij wijzelf zal ze zelfs zichzelf 
    zij zijn zijne zo zodra zonder zou zouden zowat zulke zullen zult een  je  te lekker bekende wordt namelijk
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

    if f == '': return ''
    return f


def f_ingredients(j):
    'Includes all ingredients and splits them.'
    fs = [x.strip().lower() for x in j.get('ingredients', '') if len(j['ingredients']) != 0]
    fs = [clean(f) for f in fs if f != '']
    fs = [x for x in ' '.join(fs).split(' ') if x.isalpha() and not x.isspace()]
    return fs


def f_description(j):
    'Includes the four most common words in the description that are not stopwords'
    f = word_tokenize(clean(j.get('desciption', '')).strip().lower())
    
    words = []
    for word in f:
        if word not in STOPWORDS and word.isalpha():
            words.append(word)
            
    return [word[0] for word in list(Counter(words).most_common(4)) if x[1] > 1]


def tokenize(j):
    '''Returns array of tokens for product nut dict'''
    tokens = f_name(j) + [f_brand(j)] + f_ingredients(j) + f_description(j) + [str(len(j.get('ingredients', '')))]        
    tokens = filter(lambda s: s not in STOPWORDS, tokens)
    tokens = filter(lambda s: len(s) > 1, tokens)

    return tokens


def tokenize_dict(j):
    '''Returns a dict with id, tokens and optional usage_name and product_id'''
    d = {'id': j['id'], 'tokens': tokenize(j)}
    if 'usage'      in j: d['usage']      = j['usage']
    if 'product_id' in j: d['product_id'] = j['product_id']

    return d


if __name__ == '__main__':
    for line in map(str.rstrip, sys.stdin):
        j = json.loads(line)
        d = tokenize_dict(j)
        print(json.dumps(d))
        
    
# added this because otherwise this doesnt work. not sure if its the same as you want it.
def tokenize_all(data):
    '''Returns a dict including the tokens, usage and product_id for all products nuts'''
    id_tokens = []
    for j in tqdm_notebook(data):
        
        id_tokens.append(tokenize_dict(j))
        
    return id_tokens

