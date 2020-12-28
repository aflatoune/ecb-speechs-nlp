#! /usr/bin/env python3
# coding: utf-8

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from urllib3.connectionpool import log as urllibLogger

import time
from datetime import datetime

import pandas as pd

import os
import argparse
import logging as lg

lg.basicConfig(level=lg.INFO)
urllibLogger.setLevel(lg.WARNING)


def create_webdriver(active_options=False):
    if active_options:
        options = Options()
        options.add_argument('--headless')
    else:
        options = None

    path_driver = 'C:/Users/Daniel/Documents/geckodriver-v0.28.0-win64/geckodriver'
    pager = webdriver.Firefox(executable_path=path_driver, options=options)
    return pager


def scroll(pager, speed=50):
    last_height = pager.execute_script("return document.body.scrollHeight")
    for i in range(0, last_height, speed):
        pager.execute_script(f"window.scrollTo(0, {i});")
    pager.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)


def get_page_source(url, pager, scrolling=False, close=True):
    lg.info('Launching driver')
    pager.get(url)
    if scrolling:
        scroll(pager)
    page_source = pager.page_source
    if close:
        pager.close()
        lg.info('Closing driver')
    return page_source


def get_urls(url, page_source):
    soup = BeautifulSoup(page_source, 'lxml')
    url_root = url.split('/press')[0]
    contents = soup.find_all('dd')
    dates = soup.find_all("dt")

    d = {}
    index = 0
    for dt, ct in zip(dates, contents):
        all_lang = ct.find_all("a")[1:]
        for lang in all_lang:
            d[index] = {'language': lang['lang'],
                        'url': url_root + lang["href"],
                        'date': dt.text}
            index += 1

    return pd.DataFrame.from_dict(d, orient='index')


def choose(data, languages=None, years=None, drop=['2 August 2007',
                                                   '26 October 2014']):
    if languages is not None:
        data = data[data["language"].isin(languages)]
        data = data.reset_index(drop=True)

    if years is not None:
        data["year"] = pd.to_datetime(data["date"]).dt.year
        if len(years) == 2:
            data = data[data['year'].isin(range(years[0], years[1]))]
        elif len(years) == 1:
            data = data[data['year'].isin(range(years[0]))]
        data = data.reset_index(drop=True).drop(columns=["year"])

    if drop is not None:
        data = data[~data.date.isin(drop)]

    return data


def get_content_article(article):
    end = article.find(id='qa')
    article = BeautifulSoup(str(article).split(str(end))[0], 'lxml')
    all_paragraph = article.find_all('p')
    init = [article.find(class_='external'), article.find(class_='arrow')]
    content = ''
    start = False

    for p in all_paragraph:
        if (any([True for i in init if i in p])):
            try:
                all_paragraph.remove(p.find_next('p'))
            except AttributeError as AE:
                lg.warning(AE)
            start = True
            continue
        if start:
            content += p.text + ' '
    return content


def scrap_content(links, pause=0, balise='article'):
    content = []
    for link in links:
        soup = BeautifulSoup(requests.get(link).text, features='lxml')
        article = soup.select(balise)[0]
        content.append(get_content_article(article))
        time.sleep(pause)
    return content


def export_to_csv(dataframe, file):
    try:
        dataframe.to_csv(f'data/{file}', index=False)
    except FileNotFoundError as e:
        lg.error(e)
    except:
        lg.error('Destination unknown')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', type=str,
                        help='Scrapped data file name')
    parser.add_argument('-l', '--lang', nargs='*', type=str,
                        help='List of languages to scrap')
    parser.add_argument('-y', '--years', nargs='*', type=int,
                        help=('Range of years to scrap. If only one value is',
                              'passed, it is considered as an upper bound.'))
    return parser.parse_args()


def scrap_speechs(lang, years, file_name, write_csv):
    url = 'https://www.ecb.europa.eu/press/pressconf/html/index.en.html'
    driver = create_webdriver(active_options=False)
    page_source = get_page_source(url, pager=driver, scrolling=True)
    data = get_urls(url, page_source)
    data = choose(data, languages=lang, years=years)
    articles = scrap_content(data.url)
    data["speech"] = articles

    if write_csv:
        export_to_csv(data, file_name)
        lg.info(f'### {data.shape[0]} speechs have been scraped ###')
