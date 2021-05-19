# Programming Assignment 3

## Prerequisites

Installing Python modules:
```bash
pip install nltk
pip install beautifulsoup4
pip install tqdm
```

You may need to download nltk stopwords data using Python:
```python
import nltk
nltk.download("stopwords")
```


## Word preprocessing

1. Split text by whitespace (`string.split`)
2. Tokenize words (`nltk.tokenize.word_tokenize`)
3. Convert tokens to lower case (`string.lower`)
4. Remove stopwords and punctuation marks (`stopwords.STOPWORDS_SLOVENE`, `stopwords.PUNCTUATION_MARKS`)
5. Remove dot sequences (`..`, `...`, `....`, etc.)
6. Remove leading apostrophes (`"'beseda"` -> `"beseda"`)


## Notes

* Inconsistent contractions (`"prjat'li"` -> `["prjat'li"]`, `"prjat'u"` -> `["prjat", "u"]`)
	* Try using a different tokenizer?
* Normalize dates, currencies (`"€"`, `"EUR"`, `"eur"` -> `"eur"`)
* Is this okay? `"gov.si.,"` -> `"gov.si."` [e-uprava.gov.si/e-uprava.gov.si.5.html]
* What if all words in the query get removed during preprocessing?
