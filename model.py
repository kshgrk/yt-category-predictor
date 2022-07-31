import pandas as pd
import numpy as np
import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier
import os

def setup():
    train = pd.read_csv('train.csv')
    test = pd.read_csv('test.csv') 

    target = train['category_id']
    limit = train.shape[0]

    stop_words = set(stopwords.words('english'))
    stemmer = SnowballStemmer('english')

    def cleaning(s):
        string = ""
        s = re.sub('[^a-zA-Z0-9\n]', ' ', s)
        s = re.sub('\s+', ' ', s)
        s = s.lower()

        for word in s.split():
            if not word in stop_words:
                word = (stemmer.stem(word))
                string += word+" "
        return string

    train['description'] = train['description'].apply(cleaning)
    test['description'] = test['description'].apply(cleaning)

    vec = CountVectorizer (ngram_range=(1,2))
    buf = pd.concat ([train['description'], test['description']])
    buf_vec = vec.fit_transform (buf)
    x_train = buf_vec[:limit]
    x_test = buf_vec[limit:]

    clf = SGDClassifier(max_iter = 100)

    clf.fit(x_train, target)

    y_pred = clf.predict(x_test)

    submission = pd.DataFrame(columns=['video_id', 'category_id'])

    submission['video_id'] = test['video_id']
    submission['category_id'] = y_pred

    submission['category_id'] = submission['category_id'].astype(int)
    submission.to_csv('submission.csv', index=False)

