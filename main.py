from twit_creds import *
import os
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import collections
import tweepy as tw
import re
from textblob import TextBlob
import networkx as nx
import nltk
from nltk import bigrams
import datetime
from datetime import timedelta


auth = tw.OAuthHandler(cons_key, cons_secrt)
auth.set_access_token(accs_tokn, accs_tokn_scrt)
api = tw.API(auth, wait_on_rate_limit=True)

search_words = ["#denial+service -filter:retweets"]

today = datetime.date.today()
last_week = today + datetime.timedelta(days=-today.weekday(), weeks=-0.2)
date_since = str(last_week)

tweets = api.search_tweets(q=search_words, lang="en")
all_tweets = [tweet.text for tweet in tweets]

users_locs = [[tweet.user.screen_name, tweet.user.location]
              for tweet in api.search_tweets(q=search_words, lang="en", until=date_since)]
tweet_text = pd.DataFrame(data=users_locs, columns=['user', "location"])
print(tweet_text)


def remove_urls(txt):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    no_url = url_pattern.sub(r'', txt)
    return no_url


def remove_url(txt):
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())


tweets_no_urls = [remove_urls(tweet.text) for tweet in tweets]
words_in_tweet = [tweet.lower().split() for tweet in tweets_no_urls]


def sentiments():
    query = '#denialofservice -is:retweet lang:en'
    tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
                                         max_results=100)
    polarity_sum = 0
    subjectivity_sum = 0
    count = 0
    for tweet in tweets.data:
        print(tweet.text)
        analysis = TextBlob(tweet.text)
        print(analysis.sentiment)

        polarity_sum = polarity_sum + analysis.sentiment.polarity
        subjectivity_sum = subjectivity_sum + analysis.sentiment.subjectivity
        count = count + 1

    print("\n\nPolarity Average: ", polarity_sum / count)
    print("Subjectivity Average: ", subjectivity_sum / count)


def word_count_chart():
    all_words_no_urls = list(itertools.chain(*words_in_tweet))
    counts_no_urls = collections.Counter(all_words_no_urls)
    clean_tweets_no_urls = pd.DataFrame(counts_no_urls.most_common(15),
                                        columns=['words', 'count'])
    print(clean_tweets_no_urls.head())
    fig, ax = plt.subplots(figsize=(8, 8))
    clean_tweets_no_urls.sort_values(by='count').plot.barh(x='words',
                                                           y='count',
                                                           ax=ax,
                                                           color="orange")
    ax.set_title("Common Words Found in Tweets")
    plt.show()


def sentiment_graph(bigrams):
    collection_words = ['&amp', '&amp;', 'they', 'service.', 'denialofservice', 'denial',
                        'service', 'a', 'dos', 'with', 'the', 'of', 'rt', 'i', '#']
    tweets_nc = [[w for w in word if not w in collection_words]
                 for word in words_in_tweet]
    terms_bigram = [list(bigrams(tweet)) for tweet in tweets_nc]
    bigrams = list(itertools.chain(*terms_bigram))
    bigram_counts = collections.Counter(bigrams)
    bigram_df = pd.DataFrame(bigram_counts.most_common(20),
                             columns=['bigram', 'count'])
    print(bigram_df)
    # Create dictionary of bigrams and their counts
    d = bigram_df.set_index('bigram').T.to_dict('records')
    # Create network plot
    G = nx.Graph()
    # Create connections between nodes
    for k, v in d[0].items():
        G.add_edge(k[0], k[1], weight=(v * 10))
    ig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, k=2)
    nx.draw_networkx(G, pos,
                     font_size=16,
                     width=3,
                     edge_color='grey',
                     node_color='orange',
                     with_labels=False,
                     ax=ax)
    for key, value in pos.items():
        x, y = value[0] + .135, value[1] + .045
        ax.text(x, y,
                s=key,
                bbox=dict(facecolor='orange', alpha=0.25),
                horizontalalignment='center', fontsize=13)
    plt.show()


def sentiment_histogram():
    all_tweets_no_urls = [remove_url(tweet) for tweet in all_tweets]
    sentiment_objects = [TextBlob(tweet) for tweet in all_tweets_no_urls]
    sentiment_values = [[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects]
    sentiment_df = pd.DataFrame(sentiment_values, columns=["polarity", "tweet"])

    fig, ax = plt.subplots(figsize=(8, 6))
    sentiment_df.hist(bins=[-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1],
                 ax=ax,
                 color="orange")

    plt.title("Sentiments from Tweets on Denial-of-Service attacks")
    plt.show()


sentiment_graph(bigrams)
sentiment_histogram()
word_count_chart()
sentiments()