# Realtime trend with redis based on abc.net.au

It implements keyword suggestion like google with Redis based on article's titles of abc.net.au.

## Reqirements

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
The system clusters words of titles, then counts each words. It suggests the highest score word according to given word.

![alt text](https://github.com/brenden17/Realtime-Trend-with-Flask-on-Redis/blob/master/img/result.png "image")

![alt text](https://github.com/brenden17/Realtime-Trend-with-Flask-on-Redis/blob/master/img/result2.png "image")
