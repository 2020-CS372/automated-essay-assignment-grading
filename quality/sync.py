from quality.semantics.sync import semantics_sync
from quality.syntax.sync import syntax_sync


def quality_sync():
    syntax_sync()
    semantics_sync()

