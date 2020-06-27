# EssayCare
An automated way to grade your essay

## Prerequisite
* Python (>= 3.7)

## Usage
To install EssayCare and its dependencies, please run following commands:
```console
$ git clone https://github.com/2020-CS372/automated-essay-assignment-grading.git    # Clone Repository
$ cd automated-assignment-grading
$ pip3 install -r requirements.txt                                                  # Install Dependencies
```

To use EssayCare, you should need CoreNLP to be installed. You can install by running following commands:
```console
$ make setup        # Setup Stanford CoreNLP
$ make run-server   # Start CoreNLP Server
```

Once the server is running, you can run the EssayCare in another terminal.

Copy and Paste your essay to `data/input.txt` and then run the command,
```console
$ python main.py score --corenlp-url=http://localhost:9000
```

You can also test EssayCare with our pre-prepared dataset.
```console
$ python main.py sample --corenlp-url=http://localhost:9000
```

The `sample` runs with at most 10 essays. If you want to run with all essays, you can use `all` instead of `sample`.

## Features
### Semantics
* `ambiguous`: Detects ambiguous sentences.
* `duplicates`: Detects too frequently used words.

### Syntax
* `agreement`: Detects wrong tense, plural/singular or third person verb.
* `capitalization`: Detects misplaced upper case or lower case letters.
* `preposition`: Detects misplaced or missing prepositions.
* `punctuation`: Detects misplaced or missing punctuations.
* `sentence_length`: Detects too long sentences.
* `structure`: Detects wrong sentence structure.
* `typo`: Detects misspelled words.

### Plagiarism
* `plagiarism`: Detects plagiarism against `data/plagiarism_data/source`
