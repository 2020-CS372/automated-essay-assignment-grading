import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUALITY_DATA_DIR = os.path.join(BASE_DIR, 'data', 'quality_data')
PLAGIARISM_DATA_DIR = os.path.join(BASE_DIR, 'data', 'plagiarism_data')
CORENLP_PATH = os.path.join(BASE_DIR, 'data', 'corenlp', 'stanford-corenlp-4.0.0.jar')
CORENLP_MODEL_PATH = os.path.join(BASE_DIR, 'data', 'corenlp', 'stanford-corenlp-4.0.0-models.jar')
CORENLP_URL = None
