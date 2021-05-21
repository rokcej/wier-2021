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
	* This is to enforce consistency, as the tokenizer can behave differently before newline characters
	* For example, `"a' b"` -> `["a", "'", "b"]`, but `"a'\nb"` -> `["a'", "b"]`
2. Tokenize words (`nltk.tokenize.word_tokenize`)
3. Convert tokens to lower case (`string.lower`)
4. Remove stopwords and punctuation marks (`stopwords.STOPWORDS_SLOVENE`, `stopwords.PUNCTUATION_MARKS`)
5. Remove dot sequences (`".."`, `"..."`, `"...."`, etc.)
	* The tokenizer splits groups of symbols (`"!!!"` -> `["!", "!", "!"]`), however, dots always stay grouped (`"..."` -> `["..."]`), so they need to be handled separately
6. Remove leading apostrophe (`"'word"` -> `"word"`)
	* The tokenizer only splits trailing apostrophes, which can cause issues with quoted words (`"'quote'"` -> `["'quote", "'"]`)
7. Remove trailing dot
	* The tokenizer can sometimes leave a dot at the end of a word (`"gov.si.,"` -> `"gov.si."`), so it needs to be manually removed
8. Map words to their normalized version
	* This allows one word to match multiple words with the same meaning
	* For example, `["eur", "evrov" "€"]` -> `"eur"`


## TODO

* (IMPORTANT) Remove repeated tokens in query


## Notes

Just some personal notes, please ignore.

* Inconsistent contractions (`"prjat'li"` -> `["prjat'li"]`, `"prjat'u"` -> `["prjat", "u"]`)
	* Try using a different tokenizer?

