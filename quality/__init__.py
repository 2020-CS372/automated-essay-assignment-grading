from quality.semantics.ambiguous import ambiguous
from quality.semantics.duplicates import duplicates
from quality.syntax.capitalization import capitalization
from quality.syntax.preposition import preposition
from quality.syntax.punctuation import punctuation
from quality.syntax.sample import sample

QUALITY_DICT = {
    'sample': sample,
    'capitalization': capitalization,
    'preposition': preposition,
    'ambiguous': ambiguous,
    'duplicates': duplicates,
    'punctuation': punctuation,
}
