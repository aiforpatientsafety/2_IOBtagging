# IOB tagger for Medical Incident Reports

This folder contains a script that allows it's users to sentencePiece tokenizing then IOB tagging Medical Incident Reports (MIR). SentencePiece tokenization can be found in [this GitHub repository](https://github.com/google/sentencepiece).

## Files

In the `iob` folder, you should have the following files : 

	- `iob_processing_corpus.py` which is the script IOB tagging corpus data.
	- `iob_processing.py` which is the script IOB tagging 58K medical reports data.
	- `./data/in/corpus517_labeled_finalized.xlsx` Excel file containing the corpus data preprocessed from .ann files (pilot 49, final 502).
	- `./data/in/medical_accidents` folder containing 58k report data.
	

## Dowloads and installations

1. Make virtual environment by `python3 -m venv envname` command.
2. Install necessary python library dependencies by `pip install -r requirements.txt` command.

## How to use the script ?

You can simply run script (`iob_processing_corpus.py`) by following command: `python iob_processing_corpus.py`. It goes same logic by `iob_processing.py` script too.

	
Usage examples : 

	- `python iob_processing_corpus.py`
	- `python iob_processing.py`
