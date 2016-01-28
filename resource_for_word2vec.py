import re
from datetime import date, timedelta

from redis import Redis
import newspaper
from newspaper import Article
from gensim.models.word2vec import Word2Vec
import nltk
from nltk.corpus import stopwords
from nltk.tag import pos_tag

redis = Redis()

class NewspaperRosource:
    def __init__(self, title, 
                        url, 
                        last=4,
                        fetch=True,
                        save=False,
                        exper=False):
        self.title = title
        self.url = url
        self.last = last
        self.save = save
        self.exper = exper
        self.narticles = 0
        self.stopword = set(stopwords.words("english"))

        if fetch:
            self.fetch_article_url()


    def fetch_article_url(self, memoize=False):
        paper = newspaper.build(self.url, memoize_articles=memoize) or []
        self.narticles = paper.size()
        print 'article count:%s' % self.narticles
        pipe = redis.pipeline()
        date_fmt = r'\d{4}[-/]\d{2}[-/]\d{2}'
        for article in paper.articles:
            url = article.url
            print url
            date_keys = re.findall(date_fmt, url)
            if not date_keys:
                continue

            date_key = date_keys[0]
            key = self.key(date_key)

            pipe.sadd(key, url)

            if self.save and date_key in self.get_valid_days():
                print 'processing....'
                try:
                    article.download()
                    article.parse()
                    key = self.key(date_key, article.title)
                    pipe.set(key, article.text)
                except:
                    pass
               
        pipe.execute()

    def key(self, date_key, article_title=None):
        if not article_title:
            return '{}:{}'.format(self.title, date_key)
        return '{}:{}:{}'.format(self.title, date_key, article_title)

    def get_valid_days(self):
        t = lambda d: date.today() - timedelta(days=d) 
        return [t(d).strftime('%Y-%m-%d') for d in range(self.last)]

    def get_line_from_url(self):
        for date_key in self.get_valid_days():
            key = self.key(date_key)
            paper_urls = redis.lrange(key, 0, -1) or []

            for url in paper_urls:
                try:
                    article = Article(url)
                    article.download()
                    article.parse()
                    key = self.key(date_key, article.title)
                    for line in article.text.replace('\n\n', '\n').split('\n'):
                        yield line.split()
                except e:
                    print e

            # pipe.execute()

    def get_line_from_saved(self):
        for date_key in self.get_valid_days():

            keys = self.key(date_key, '*')
            # print '###################'
            # print keys
            title_keys = redis.keys(keys)
            # print len(title_keys)

            for title_key in title_keys:
                text = redis.get(title_key)
                # self.tokenizer.tokenize(text.strip()) # do not use.
                for sent in text.replace('\n\n', '\n').split('\n'):
                    yield self.get_wordlist(sent)

        
    def get_wordlist(self, sent):
        sent = re.sub("[^a-zA-Z]", " ", sent)
        if self.exper == True:
            tagged_sent = pos_tag(sent.lower().split())
            nouns = [word for word, pos in tagged_sent \
                        if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
            return [n for n in nouns if not n in self.stopword]
        
        words = sent.lower().split()
        return [w for w in words if not w in self.stopword]


    def get_sentences(self):
        raw_sentences = self.tokenizer.tokenize(text.replace('\n\n', '\n').split('\n'))
        for raw_sentence in raw_sentences:
            if len(raw_sentence) > 0:
                yield self.get_wordlist(raw_sentence)

    
    def __iter__(self):
        if self.save:
            return self.get_line_from_saved()
        return self.get_line_from_url()

def query(model, keyword):
    print keyword
    try:
        print model.most_similar(keyword)
    except:
        print 'Can not support.'

def create_model():
    NR = NewspaperRosource('abc', 'http://www.abc.com.au', fetch=False, save=True)
    model = Word2Vec(NR)
    query(model, 'uber')
    query(model, 'france')
    
    print 'Appling stopword @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
    NR = NewspaperRosource('abc', 'http://www.abc.com.au', fetch=False, save=True, exper=True)
    model = Word2Vec(NR)
    query(model, 'uber')
    query(model, 'france')
    
if __name__ == '__main__':
    NR = NewspaperRosource('abc', 'http://www.abc.com.au', fetch=False, save=True, exper=True)
    for line in NR.get_line_from_saved():
        print ' '.join(line)

