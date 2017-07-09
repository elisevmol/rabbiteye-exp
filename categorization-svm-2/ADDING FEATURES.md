# Adding Features

In the hope to improve accuracy, more features are added to the model in this step. The methods and results are discussed in this blog update. 

Most of the changes are added in the featurize.py code. The adapted version of the featurize.py code can be found in featurize_more_features.py. 
The first two small adaptions are extending the stopwords and removing the labels attached to ingredients, brands etc. The grander steps include adding the four most common words in the descriptions (those that are not stopwords). 

```
def f_description(j):
    'Includes the four most common words in the description that are not stopwords'
    f = word_tokenize(clean(j.get('desciption', '')).strip().lower())
    
    words = []
    for word in f:
        if word not in STOPWORDS and word.isalpha():
            words.append(word)
            
    return [word[0] for word in list(Counter(words).most_common(4)) if x[1] > 1]
```

Furthermore all ingredients are added to the tokens in the following manner.

```
def f_ingredients(j):
    'Includes all ingredients and splits them.'
    fs = [x.strip().lower() for x in j.get('ingredients', '') if len(j['ingredients']) != 0]
    fs = [clean(f) for f in fs if f != '']
    fs = [x for x in ' '.join(fs).split(' ') if x.isalpha() and not x.isspace()]
    return fs
```

And utimately the amount of ingredients is added as a seperate token.

```
tokens = f_name(j) + [f_brand(j)] + f_ingredients(j) + f_description(j) + [str(len(j.get('ingredients', '')))]        
```

After transforming applying the same method devised in earlier steps of this project (removing doubles, making sure the threshold of 3 products per usage is met and adding labels for the 'bubble' implementation), the accuracy one 100% of the features is calculated. This accuracy is:

```
Accuracy Linear SVC 100: 0.63 (+/- 0.03)
```

This is lower than the accuracy on 100 percent of the original features. Because the amount of features is increased, this could be explained by adding too many features, which is why feature reduction is a crucial step in this method. After implementing feature reduction with the default score function: ANOVA F-value, the following graphs depicting accuracy against percentage of the features is found. 

![](feature_reduction_more_features.png)

Because this graph does not show an increase of accuracy when the number of features are reduced, another scoring function is implemented: chi2. This scoring function resulted in the same scores. 

On the validation set with 60% of the features the final recall scores are the following:

```
micro recall score:  0.703229137332
macro recall score:  0.577158145065
```

60% of the features is selected because up till 60% the accuracy is the 63%.
These recall scores are not optimal leading me to believe adding features is counter productive.  


Another possible improvement had to do with the binary nature of how features were represented. In the current code a feature is either present or not, while this could also be switched to the number of times a feature is present. After implementing this by switching 

```
vectorizer = CountVectorizer(min_df=1, binary=True)
X_TRAIN = vectorizer.fit_transform(text_per_item_pn_TRAIN)
```

to 

```
vectorizer = CountVectorizer(min_df=1, binary=False)
X_TRAIN = vectorizer.fit_transform(text_per_item_pn_TRAIN)
```

the accuracy did not improve. 
