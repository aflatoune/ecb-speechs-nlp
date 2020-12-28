#! /usr/bin/env python3
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
from nltk import FreqDist
from readability import Readability

import re
import os


class BaseAnalysis:
    def __init__(self, name):
        self.name = name

    def data_from_csv(self, csv_file):
        self.dataframe = pd.read_csv(os.path.join('data', csv_file))

    def data_from_dataframe(self, dataframe):
        self.dataframe = dataframe

    def __tokenize(self, column):
        return self.dataframe[column].map(lambda x: re.findall(r'\w+', x))

    def count_word(self):
        d = {}
        d['date'] = self.dataframe.date.tolist()
        raw_counts = []
        processed_counts = []
        for x in zip(self.__tokenize('speech'), self.__tokenize('processed_speech')):
            raw_counts.append(len(x[0]))
            processed_counts.append(len(x[1]))
        d['counts_raw_speech'] = raw_counts
        d['counts_processed_speech'] = processed_counts
        return pd.DataFrame.from_dict(d, orient='columns')

    def graph_count_word(self):
        df = self.count_word()
        x = pd.to_datetime(df.date)
        fix, ax = plt.subplots()
        ax.plot(x, df.iloc[:, 1], label='row')
        ax.plot(x, df.iloc[:, 2], label='processed', c='r')
        plt.title('Word counts')
        plt.xlabel('Year')
        plt.xticks(rotation=90)
        plt.ylabel('Counts')
        plt.legend()
        plt.show()

    def get_top_words(self, processed, n_words=20, graph=True):
        if processed:
            all_speechs = self.__tokenize('processed_speech')
        else:
            all_speechs = self.__tokenize('speech')
        top_words = FreqDist([word for speech
                              in all_speechs
                              for word
                              in speech]).most_common(n_words)
        if not graph:
            return top_words
        else:
            plt.figure()
            plt.bar([_[0] for _ in top_words], [_[1] for _ in top_words],
                    color='darkblue', alpha=0.6)
            plt.plot(range(n_words), [_[1] for _ in top_words], linestyle='-',
                     marker='.', color='darkorange')
            plt.xlabel('Words')
            plt.xticks(rotation=90)
            plt.ylabel('Counts')
            plt.show()

    def graph_readability(self):
        x = pd.to_datetime(self.dataframe.date)
        y = self.dataframe.speech.map(
            lambda u: Readability(u).ari().score)
        z = self.dataframe.speech.map(
            lambda u: Readability(u).flesch().score)
        t = self.dataframe.speech.map(
            lambda u: Readability(u).gunning_fog().score)
        plt.figure()
        plt.plot(x, y, label='Coleman-Biau index')
        plt.plot(x, z, label='Flesch-Kincaid index')
        plt.plot(x, t, label='Gunning- Fog index')
        plt.xlabel('Year')
        plt.xticks(rotation=90)
        plt.ylabel('Readability')
        plt.legend()
        plt.show()
