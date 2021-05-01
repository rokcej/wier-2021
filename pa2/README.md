# Programming Assignment 2

The goal of this assignment is to use three different approaches for HTML data extraction: regular expressions, XPath and RoadRunner.

The data is extracted from three chosen websites: overstock.com, rtvslo.si and manazara.si.

## Prerequisites

Install Python 3 and the following packages:

```bash
pip install beautifulsoup4
pip install lxml
pip install unidecode
```

## Usage

To run the program, move into the `input-extraction` directory, then run `run-extraction.py` with different parameters.

```bash
cd input-extraction
python ./run-extraction.py A # Regex extraction
python ./run-extraction.py B # XPath extraction
python ./run-extraction.py C # RoadRunner extraction
```

