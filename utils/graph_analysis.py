#! /usr/bin/env python3
# coding: utf-8

import pandas as pd


class GraphSpeechs:
    def __init__(self, name):
        self.name = name


    def data_from_csv(self, csv_file):
        self.dataframe = pd.read_csv(csv_file)


def launch_analysis():
        pass


if __name__ == '__main__':
    launch_analysis()
