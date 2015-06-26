##
# @package TFGSearch.Metasearch.searcher
# Definition of an abstract class for the classes that call a Search Engine API outside the application
# @author Javier Sanz-Cruzado Puig
from abc import ABCMeta, abstractmethod
__author__ = 'javier'

##
# Calls a Search Engine API
class Searcher:
    __metaclass__ = ABCMeta

    ##Searcher name
    name = None;


    ##
    # Calls a search engine
    # @param query query
    # @param search Search to associate the results
    # @returns a ranking of searchResults
    @abstractmethod
    def doSearch(self, query, search): pass

    def __init__(self, name):
        self.name = name;

