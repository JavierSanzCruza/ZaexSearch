# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
## @package ZaexEvaluation.Evaluation
# Package that contains classes and methods for evaluating several search engines
## @package ZaexEvaluation.Evaluation.abTest
# Abstract class definition for multileaving tests

from abc import ABCMeta, abstractmethod

### Abstract class that represents an AB Test
class ABTest:
    __metaclass__ = ABCMeta

    ###
    # Interleaves the search results
    # @param linkLists Lists of results coming from each one of the evaluated rankers
    # @returns a ranking with the interleaved results
    @abstractmethod
    def interleaveResults(self, linkLists): pass

    ##
    # Evaluates the different systems evaluating the expected number of clicks for each one
    # @return the evaluated rankers
    @abstractmethod
    def evaluateClicks(self): pass

    ##
    # Evaluates the different systems evaluating the expected number of queries won by each one
    # @return the evaluated rankers
    @abstractmethod
    def evaluateQueries(self): pass