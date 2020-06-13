import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUALITY_DATA_DIR = os.path.join(BASE_DIR, 'data', 'quality_data')
PLAGIARISM_DATA_DIR = os.path.join(BASE_DIR, 'data', 'plagiarism_data')
CORENLP_PATH = os.path.join(BASE_DIR, 'data', 'corenlp', 'stanford-corenlp-4.0.0.jar')
CORENLP_MODEL_PATH = os.path.join(BASE_DIR, 'data', 'corenlp', 'stanford-corenlp-4.0.0-models.jar')
CORENLP_URL = 'http://localhost:9000'
STANFORD_NER_JAR = os.path.join(BASE_DIR, 'data', 'stanford_ner', 'stanford-ner.jar')
STANFORD_NER_MODEL = os.path.join(BASE_DIR, 'data', 'stanford_ner', 'english.all.3class.distsim.crf.ser.gz')