# ecb-speechs-nlp

## Description

In this repo, you'll find three scripts to scrap, process and (briefly) analyze the content of the European Central Bank (ECB) communication. We focus on the introductory statement of the President of the ECB. This statement is given during the press conferences following the Governing Council's meetings. All the press conferences can be found [here](https://www.ecb.europa.eu/press/pressconf/html/index.en.html).

Note that until December 4, 2014, statements are only available in English.

## Usage

* `utils/scraping.py` contains the code needed to scrap the statements (thanks to [titigmr](https://github.com/titigmr/) for his help);
* `utils/process_speechs.py` proposes a processing of the statements (only if the statements are in English);

To scrap all English statements between 2006 and 2020 and store them in a file named `raw_data.csv` containing the dates, the language(s), the urls and the content of the statements:

```shell
python main.py --scrap -n raw_data.csv -l en -y 2006 2021
```

To process `raw_data.csv` and store the result in a file named `processed_data.csv` containing an additional column for processed statements:

```shell
python main.py --prep -i raw_data.csv -o processed_data.csv
```

## Analysis

`utils/base_analysis.py` contains the code to conduct a summary analysis of statements content (words count, top words, readability scores). The notebook `basic_analysis.ipynb` provides an illustration.
