from collections import Counter
from nltk.corpus import stopwords
from nltk.collocations import *
from nltk import BigramCollocationFinder
from textblob import TextBlob
import articles
import nltk

stops = [unicode(word) for word in stopwords.words('english')]


def remove_stop_words(text):
    meaningful_words = [sword.strip() for sword in text.split(' ') if sword.lower().strip() not in stops]
    return meaningful_words


def common_words(word_list):
    return Counter(word_list).most_common()[:20]


def find_bigrams(word_list):
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    bigram_finder = BigramCollocationFinder.from_words(word_list)
    print 'finding bigrams...'
    # Filter to top 20 results; otherwise this will take a LONG time to analyze
    bigram_finder.apply_freq_filter(20)
    for bigram in bigram_finder.score_ngrams(bigram_measures.raw_freq)[:10]:
        print bigram

def find_bigrams_span(word_list, span=20):
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(word_list, window_size=span)
    finder.apply_freq_filter(2)
    for bigram in finder.nbest(bigram_measures.likelihood_ratio, 10):
        print bigram

def score_feels(word_list):
    text = TextBlob(' '.join(word_list))
    return text.sentiment.polarity, text.sentiment.subjectivity


if __name__ == '__main__':
    cleaned = remove_stop_words(articles.sample_article)
    print common_words(cleaned)
    #not very interesting, probably need to do this over an entire colleciton of documents using pandas or somehting?
    find_bigrams(cleaned)

    print score_feels(cleaned)
