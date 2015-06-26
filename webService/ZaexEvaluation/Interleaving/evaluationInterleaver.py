## @package ZaexEvaluation.Interleaving
# Package that contains classes and methods for interleaving search results in a unified ranking for evaluation
# of several search systems.
# @author Javier Sanz-Cruzado Puig

##
# @package ZaexEvaluation.Interleaving.evaluationInterleaver
# Definition for abstract class EvaluationInterleaver
# @file TFGSearch.Metasearch.metasearcher.py
# @author Javier Sanz-Cruzado Puig

from TFGSearch.Metasearch.metasearcher import *

## Abstract class for interleaving results coming from several sources
class EvaluationInterleaver (Metasearcher):
    __metaclass__ = ABCMeta

    ##
    # Searcher list
    searcherList = list()

    ##
    # Constructor
    def __init__(self):
        searcherList = list()

    ## Given a list of links from a search API, combines results and reorders them for evaluation
    # @param linkLists Lists of links coming from each source
    # @param values NOT USED
    # @returns Lista de SearchResult ordenados si OK, None si ERROR, o no hay resultados
    @abstractmethod
    def doMetaSearch(self, linkLists, values={}): pass

    ## Given a list of links from a search API, combines results and reorders them for evaluation. This function
    # does not save sources in the database
    # @param linkLists Lists of links coming from each source
    # @param values NOT USED
    # @returns Lista de SearchResult ordenados si OK, None si ERROR, o no hay resultados
    @abstractmethod
    def doMetaSearchNotSaveSource(self, linkLists): pass