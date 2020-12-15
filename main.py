#! /usr/bin/env python3
# coding: utf-8

import utils.process_speechs as process
import utils.scraping as scraping
import argparse
import logging as lg
import os

lg.basicConfig(level=lg.INFO)


def check_availability(file):
    path_data_dir = os.path.join(os.getcwd(), 'data')
    try:
        if os.path.isfile(f'{path_data_dir}/{file}'):
            lg.warning(
                f'{file} is already existing. Do you want to erase it?')
            choice = input('y/n? ')
            while choice not in ['y', 'n']:
                choice = input('You must type y or n: ')
            if choice == 'y':
                return True
            else:
                return False
        else:
            return False
    except FileNotFoundError as e:
        lg.error(e)
    except:
        lg.error('Destination unknown')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scrap', action='store_true',
                        help='Decide whether to scrap data or not')
    parser.add_argument('--prep', action='store_true',
                        help='Decide wheter to process some data or not')
    parser.add_argument('-n', '--file_name', type=str,
                        help='Scrapped data file name')
    parser.add_argument('-l', '--lang', nargs='*', type=str,
                        help='List of languages to scrap')
    parser.add_argument('-y', '--years', nargs='*', type=int,
                        help=('Range of years to scrap. If only one value is',
                              'passed, it is considered as an upper bound.'))
    parser.add_argument('-i', '--inputs', type=str,
                        help='CSV file containing the scrapped speechs')
    parser.add_argument('-o', '--output', type=str,
                        default='processed_data.csv',
                        help='Processed data file name')
    parser.add_argument('--ngrams', nargs=2, type=int, default=[2, 2],
                        help=('The lower and upper boundary of the range of',
                              'n-values for different n-grams to be extracted'))
    parser.add_argument('--min_df', type=float, default=.8,
                        help=('When building the vocabulary of ngrams ignore',
                              'terms that have a document frequency strictly',
                              'lower than the given threshold'))
    return parser.parse_args()


def main():
    args = parse_arguments()
    scrap = args.scrap
    prep = args.prep
    file_name = args.file_name
    lang = args.lang
    years = args.years
    inputs = args.inputs
    output = args.output
    ngrams = args.ngrams
    min_df = args.min_df

    if (scrap == False) and (prep == False):
        lg.warning('Please indicate an action: --scrap or --prep')

    if scrap:
        try:
            if file_name == None:
                raise Warning('You must indicate a file name')
        except Warning as e:
            lg.warning(e)
        else:
            if len(years) > 2:
                raise ValueError('You cannot enter more than two dates')
            else:
                if check_availability(file_name):
                    scraping.scrap_speechs(lang, years, file_name, True)
                else:
                    lg.info(('Please relaunch the program with an available',
                             'file name.'))

    if prep:
        try:
            if inputs == None:
                raise Warning('You must indicate a file to process')
        except Warning as e:
            lg.warning(e)
        else:
            if check_availability(output):
                process.process_speechs(inputs, output, ngrams, min_df, True)
            else:
                lg.info(('Please relaunch the program with an available',
                         'file name.'))


if __name__ == '__main__':
    main()
