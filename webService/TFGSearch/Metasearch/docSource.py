__author__ = 'javier'


class DocSource:
    docRank = 0
    sourcesList = []
    sourcesRanks = []

    def __init__(self, docRank, sourcesList, sourcesRanks):
        self.docRank = docRank
        self.sourcesList = sourcesList
        self.sourcesRanks = sourcesRanks