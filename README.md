# IOB tagger for Incident Reports of Medication Errors

This folder contains a script that allows it's users to sentencePiece tokenizing then IOB tagging Medical Incident Reports (MIR). SentencePiece tokenization can be found in [this GitHub repository](https://github.com/google/sentencepiece).

## Direct Download Link
Please access to program from the following DDL. 
https://drive.google.com/file/d/1TbESHGVpl9__-1pU71gp9ZOlaNggtcO8/view?usp=sharing

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
