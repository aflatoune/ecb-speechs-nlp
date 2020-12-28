#! /usr/bin/env python3
# coding: utf-8

import os
import logging as lg

import pandas as pd
import numpy as np

import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

lg.basicConfig(level=lg.INFO)


def data_from_csv(csv_file):
    dataframe = pd.read_csv(csv_file)
    return dataframe


def specific_adjustment(data):
    mask = (data.date == '6 October 2011')
    obj = data.loc[mask, 'speech']
    obj = obj.map(lambda x: x.split('Rehn.')[1].strip())
    data.loc[mask, 'speech'] = obj.map(
        lambda x: x.split('Let me close')[0].strip())
    return data


def prune_head_tail(speech):
    speech = speech.strip().split('* * *')[0].strip()
    speech = speech.lower()
    speech = speech.strip().rsplit('. ', 1)[0].strip()
    try:
        speech = speech.split('s meeting.')[1].strip()
    except IndexError:
        try:
            speech = speech.split('commissioner almunia.')[1].strip()
        except IndexError:
            try:
                speech = speech.split('prime minister juncker.')[1].strip()
            except IndexError:
                pass
    return speech


def hasNumbers(string):
    return bool(re.search(r'\d', string))


def add_stopwords():
    sp = spacy.load("en_core_web_sm")
    spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
    add = ['ecb', 'basis', 'cet', 'utc', 'gmt', 'governing', 'council', 'let',
           'say', 'draghi', 'lagarde', 'trichet', 'mr', 'ms', 'papademos',
           'junker', 'euro', 'area', 'january', 'february', 'march', 'april',
           'june', 'july', 'august', 'september', 'october', 'november',
           'december', 'meeting', 'ii', 'iii', 'iv']
    spacy_stopwords.update(add)
    return spacy_stopwords


def preprocess_speech(speech):
    stopwords = add_stopwords()
    sp = spacy.load("en_core_web_sm")
    select = ' '.join(word.lemma_.lower() for word in sp(speech)
                      if not hasNumbers(str(word.lemma_))
                      if word.lemma_.lower() not in stopwords
                      and word.lemma_ not in ["-PRON-"]
                      and (len(word.text) > 1))
    return select


def select_ngrams(speechs, ngrams, min_df):
    ngrams = tuple(ngrams)
    tfidf_vectorizer = TfidfVectorizer(
        stop_words=None, ngram_range=ngrams, min_df=0.95)
    tfidf = tfidf_vectorizer.fit_transform(speechs)
    selected_ngrams = tfidf_vectorizer.get_feature_names()
    return selected_ngrams


def union_ngrams(*args):
    selected_ngrams = []
    for arg in args:
        selected_ngrams = list(set(selected_ngrams).union(set(arg)))
    return selected_ngrams


def add_ngrams(speech, selected_ngrams):
    for ngram in selected_ngrams:
        speech = re.sub(ngram.split()[0] + ' ' + ngram.split()[1],
                        ngram.split()[0] + '_' + ngram.split()[1], speech)
    return speech


def export_to_csv(dataframe, file):
    try:
        dataframe.to_csv(f'data/{file}', index=False)
    except FileNotFoundError as e:
        lg.error(e)
    except:
        lg.error('Destination unknown')


def process_speechs(inputs, output, ngrams, min_df, write_csv):
    dataframe = data_from_csv(os.path.join('data', inputs))
    dataframe = specific_adjustment(dataframe)
    dataframe.speech = dataframe.speech.map(lambda x: prune_head_tail(x))
    processed_speechs = dataframe.speech.map(lambda x: preprocess_speech(x))

    selected_ngrams = select_ngrams(
        processed_speechs, ngrams=ngrams, min_df=min_df)

    processed_speech = processed_speechs.map(
        lambda x: add_ngrams(x, selected_ngrams))
    dataframe['processed_speech'] = processed_speech

    if write_csv:
        export_to_csv(dataframe, output)

    lg.info(f'### Preprocessing is over, a file {output} has been created ###')
