import re
from datetime import date, timedelta
from itertools import combinations_with_replacement

from redis import Redis
import newspaper
from newspaper import Article
import nltk
from nltk.corpus import stopwords
from nltk.tag import pos_tag
# from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer

redis = Redis()

class NewspaperRosource:
    def __init__(self, title, 
                        url, 
                        last=10,
                        candidate=10,
                        fetch=True,
                        save=False,
                        exper=False):
        self.title = title
        self.url = url
        self.last = last
        self.candidate = candidate
        self.save = save
        self.exper = exper
        self.narticles = 0
        self.stopword = set('abc,news,australian,corporation,s'.split(','))

        if fetch:
            self.fetch_article_url()

    def fetch_article_url(self, memoize=False):
        paper = newspaper.build(self.url, memoize_articles=memoize) or []
        self.narticles = paper.size()
        # print 'article count:%s' % self.narticles
        date_fmt = r'\d{4}[-/]\d{2}[-/]\d{2}'
        # stemmer = SnowballStemmer("english")
        wordnet_lemmatizer = WordNetLemmatizer()
        
        for article in paper.articles:
            url = article.url
            # print url
            date_keys = re.findall(date_fmt, url)
            if not date_keys:
                continue

            date_key = date_keys[0]
            key = self.date_key(date_key)
            redis.sadd(key, url)

            if self.save and date_key in self.get_valid_days():
                try:
                    article.download()
                    article.parse()
                    title = article.title
                    title = re.sub("[^a-zA-Z]", " ", title)
                    # stem_words = [stemmer.stem(word) for word in title.lower().split()]
                    tagged_sent = pos_tag(title.lower().split())
                    nouns = [wordnet_lemmatizer.lemmatize(word) for word, pos in tagged_sent \
                        if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
                    
                    nouns = self.filter_stopword(nouns)
                    # title
                    self.count_words(nouns)

                    # tag
                    tags = article.tags
                    self.count_tag_words(tags, nouns)

                except Exception as e:
                    print e 

        # update words based on tags
        self.update_words()

    def filter_stopword(self, words):
        return [w for w in words if not w in self.stopword]

    def count_words(self, words):
        pipe = redis.pipeline()

        for word1 in words:
            for word2 in words:
                if word1 != word2:
                    word_key = self.word_key(word1)
                    pipe.zincrby(word_key, word2)
        pipe.execute()

    def count_tag_words(self, tags, words):
        pipe = redis.pipeline()
        
        for tag in tags:
            tag_key = self.tag_key(tag)
            for word in words:
                pipe.zincrby(tag_key, word)
        pipe.execute()

    def update_words(self):
        for tag in redis.keys(self.tag_key('*')):
            word_count = redis.zrange(tag, 0, -1, withscores=True)

            for word1, _ in word_count:
                for word2, count in word_count:
                    if word1 != word2:
                        word_key = self.word_key(word1)
                        redis.zincrby(word_key, word2, count)


    def query(self, keyword):
        word_key = self.word_key(keyword)
        return [w for w, c in redis.zrange(word_key, 0, -1, withscores=True)[-self.candidate:]]

    def date_key(self, date_key):
        return self.create_key('date', date_key)

    def word_key(self, word):
        return self.create_key('word', word)
    
    def tag_key(self, tag):
        return self.create_key('tag', tag)
    
    def create_key(self, identity, target):
        return '{}:{}:{}'.format(self.title, identity, target)

    def get_valid_days(self):
        t = lambda d: date.today() - timedelta(days=d) 
        return [t(d).strftime('%Y-%m-%d') for d in range(self.last)]

def suggest_keyword(keyword):
    word_key = '{}:{}:{}'.format('abc', 'word', keyword)
    return [{'id':w, 'name':keyword+' '+w}  for w, c in redis.zrange(word_key, 0, -1, withscores=True)[-10:][::-1]]



if __name__ == '__main__':
    NR = NewspaperRosource('abc', 'http://www.abc.net.au', fetch=True, save=True)
    print NR.query('lewd')
    print '#####################'
    print NR.query('queensland')
