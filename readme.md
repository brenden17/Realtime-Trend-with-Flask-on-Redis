# Realtime trend with redis based on abc.net.au

It implements keyword suggestion like google with Redis based on article's titles of abc.net.au.

## Requirements

* Redis server
* Python library

~~~
pip install newspaper
pip install nltk
pip install redis
pip install gensim
~~~

* Tokenizing Autocomplete (http://loopj.com)

## How to get keyword
The system clusters words of titles from abc.net.au, then counts each words. It suggests the highest scored word according to given word.

NewspaperRosource fetchs new atitle's titles every one hours. It weights word appearance occurrence.

![alt text](https://github.com/brenden17/Realtime-Trend-with-Flask-on-Redis/blob/master/img/result.png "image")
27/Jan/2016 

![alt text](https://github.com/brenden17/Realtime-Trend-with-Flask-on-Redis/blob/master/img/result2.png "image")
27/Jan/2016 

## Word2Vec

Original system was developed in word2vec. But It did not work properly. It was changed to clustering word of article's title.
resource_for_word2vec.py, test.py, 26-27.txt, 26-27_words.txt and 28-19_noun.txt are for word2vec. 