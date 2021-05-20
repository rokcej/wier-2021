# Programming Assignment 3

## Prerequisites

Python >=3.6 is required. Furthermore, Git LFS is used for `inverted-index.db` storage.

Installing Python modules:
```bash
pip install nltk
pip install beautifulsoup4
pip install tqdm
```

You may need to download some nltk data using Python:
```python
import nltk
nltk.download("stopwords")
nltk.download("punkt")
```

You may also need to enable Git LFS:
```bash
git lfs install
```


## Usage

### Data processing and indexing

```bash
cd implementation-indexing
python run-index.py
```

### Data retrieval

* Search using SQLite index

```bash
cd implementation-indexing
python run-sqlite-search.py "SEARCH QUERY"
```

* Search without an inverted index

```bash
cd implementation-indexing
python run-basic-search.py "SEARCH QUERY"
```


## Word preprocessing

A short description of how word preprocessing is performed, and why. Only read if you're interested.

1. Split text by whitespace (`string.split`)
	* This is to enforce consistency, as the tokenizer can behave differently before newline characters. For example, `"a' b"` -> `["a", "'", "b"]`, but `"a'\nb"` -> `["a'", "b"]`.
2. Tokenize words (`nltk.tokenize.word_tokenize`)
3. Convert tokens to lower case (`string.lower`)
4. Remove stopwords and punctuation marks (`stopwords.STOPWORDS_SLOVENE`, `stopwords.PUNCTUATION_MARKS`)
5. Remove dot sequences (`".."`, `"..."`, `"...."`, etc.)
	* The tokenizer splits groups of symbols (`"!!!"` -> `["!", "!", "!"]`), however, dots always stay grouped (`"..."` -> `["..."]`), so they need to be handled separately
6. Remove leading apostrophes (`"'word"` -> `"word"`)
	* The tokenizer only splits trailing apostrophes, which can cause issues with quoted words (`"'quote'"` -> `["'quote", "'"]`)


## Notes

Just some personal notes, please ignore.

* Inconsistent contractions (`"prjat'li"` -> `["prjat'li"]`, `"prjat'u"` -> `["prjat", "u"]`)
	* Try using a different tokenizer?
* Normalize dates, currencies (`"€"`, `"EUR"`, `"eur"` -> `"eur"`)
* Is this okay? `"gov.si.,"` -> `"gov.si."` [e-uprava.gov.si/e-uprava.gov.si.5.html]
* What if all words in the query get removed during preprocessing?

