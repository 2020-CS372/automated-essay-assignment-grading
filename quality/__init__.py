from quality.semantics.ambiguous import ambiguous
from quality.semantics.duplicates import duplicates
from quality.syntax.capitalization import capitalization
from quality.syntax.preposition import preposition
from quality.syntax.punctuation import punctuation
from quality.syntax.agreement import agreement
from quality.syntax.sentence_length import sentence_length
from quality.syntax.sample import sample
from quality.syntax.structure import structure
from quality.syntax.typo import typo

QUALITY_DICT = {
    'sample': sample,
    'capitalization': capitalization,
    'preposition': preposition,
    'ambiguous': ambiguous,
    'duplicates': duplicates,
    'punctuation': punctuation,
    'structure': structure,
    'typo': typo,
    'agreement': agreement,
    'sentence_length': sentence_length,
}
