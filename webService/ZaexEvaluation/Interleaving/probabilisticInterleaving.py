# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-

__author__ = 'javier'

##
# @package ZaexEvaluation.Interleaving.probabilisticInterleaving
# Definition for a interleaver that implements the probabilistic method.
# @author Javier Sanz-Cruzado Puig

from ZaexEvaluation.Interleaving.evaluationInterleaver import *
import re
import random

##
# Interleaver that uses the probabilistic method (For Evaluation)
class ProbabilisticInterleaving(EvaluationInterleaver):


    ## Constant for the softmax functions
    tau = 3

    ##
    # Constructor
    def __init__(self):
        super(Metasearcher, self).__init__()
        self.searcherList = list()

    ## Given some link lists, and the next document in the unified ranking, deletes the document from all the
    # rankings and normalizes them
    # @param self Interleaver
    # @param initializedLists Lists with the previous calculations
    # @param dnext Document to delete
    # @param saveSource Indicates if source must be saved
    # @returns Renormalized link lists
    def removeAndRenormalize(self, initializedLists, dnext, saveSource):
        searcherList = initializedLists.keys()

        newInitializedLists = {}
        for name in searcherList:
            deletion = None
            for entry in initializedLists[name]:
                if entry[0].url == dnext.url:
                    deletion = entry
                    break
            if(deletion is not None):
                ls = []
                if(saveSource is True):
                    dnext.addSource(name, deletion[0].rank)
                dnext.addInterleavingSource(name, deletion[0].rank)
                initializedLists[name].remove(deletion)
                denominator = sum(entry[1] for entry in initializedLists[name])
                for entry in initializedLists[name]:
                    ls.append((entry[0], entry[1], entry[1]/denominator))
                newInitializedLists[name] = ls
            else:
                newInitializedLists[name] = initializedLists[name]
        return newInitializedLists

    ## Given several lists of links, fuses them into a unique list, by using probabilistic interleaving
    # @param self The interleaver
    # @param linkLists List of MetaSearchLinks
    # @returns Ordered SearchResult list if OK, None si ERROR or there are no results
    def doMetaSearch(self, linkLists, search, values={}):
        if(linkLists is None):
            return None

        numBuscadores = linkLists.__len__()
        if(numBuscadores == 0):
            return None

        listSearchers = linkLists.keys()
        numSearchers = listSearchers.__len__()

        defLinkLists = {}
        for key in linkLists:
            ls = []
            for res in linkLists[key]:
                if res.searchID == search:
                    ls.append(res)
            defLinkLists[key] = ls

        linkLists = defLinkLists
        #Initializing the values of the softmax function:
        initializedLists = {}
        for name in listSearchers:
            ls = []
            n = linkLists[name].__len__()

            denominator = sum([1.0/pow(j, self.tau) for j in range(1,n+1)])

            for j in range(n):
                ls.append((linkLists[name][j], (1.0/pow(j+1, self.tau)), (1.0/pow(j+1, self.tau))/denominator))

            initializedLists[name] = ls

        results = list()
        sources = list()
        flag = False
        while flag is False:
            flag = True
            for name in listSearchers:
                if(initializedLists[name].__len__() > 0):
                    flag = False

            if(flag is False):
                #We select the ranking from which we are taking the result
                nonemptyList = False
                while nonemptyList is False:
                    selectedRank = random.randint(0,numSearchers-1)
                    selectedName = listSearchers[selectedRank]
                    if(initializedLists[selectedName].__len__() > 0):
                        nonemptyList = True

                #We save the source to which we associate the result
                sources.append(selectedName)

                # Generation of a random number between 0 and 1. The next entry will be selected depending on this number
                rnd = random.random()
                accumulatedSum = 0.0
                dnext = None
                sourceRank = 0
                for entry in initializedLists[selectedName]:
                    accumulatedSum += entry[2]
                    if(accumulatedSum >= rnd):
                        dnext = entry[0]

                        break

                if(dnext is None):
                    dnext = initializedLists[selectedName][0][0]


                dnext.value = 2
                if dnext.snippet is not None:
                    cad = dnext.snippet.split()
                dnext.snippet = ''
                for c in cad:
                    dnext.snippet += re.sub(r'[^\w.,-áéíóúàèìòùñäëïöü]', '', c) + ' '
                dnext.save()
                results.append(dnext)

                initializedLists = self.removeAndRenormalize(initializedLists, dnext, True)

        if results.__len__() == 0:
            return None

        i = 0
        for metaLnk in results:
            i += 1
            metaLnk.rank = i
            metaLnk.save()

        return results

   ## Given several lists of links, fuses them into a unique list, by using probabilistic interleaving. Assumes
    # that the evaluated systems are not the origin systems, so it does not save sources (only interleaving ones)
    # @param self The interleaver
    # @param linkLists List of MetaSearchLinks
    # @returns Ordered SearchResult list if OK, None si ERROR or there are no results
    def doMetaSearchNotSaveSource(self, linkLists):
        if(linkLists is None):
            return None

        numBuscadores = linkLists.__len__()
        if(numBuscadores == 0):
            return None

        listSearchers = linkLists.keys()
        numSearchers = listSearchers.__len__()
        #Initializing the values of the softmax function:
        initializedLists = {}
        for name in listSearchers:
            ls = []
            n = linkLists[name].__len__()

            denominator = sum([1.0/pow(j, self.tau) for j in range(1,n+1)])

            for j in range(n):
                ls.append((linkLists[name][j], (1.0/pow(j+1, self.tau)), (1.0/pow(j+1, self.tau))/denominator))

            initializedLists[name] = ls

        results = list()
        sources = list()
        flag = False
        while flag is False:
            flag = True
            for name in listSearchers:
                if(initializedLists[name].__len__() > 0):
                    flag = False

            if(flag is False):
                #We select the ranking from which we are taking the result
                nonemptyList = False
                while nonemptyList is False:
                    selectedRank = random.randint(0,numSearchers-1)
                    selectedName = listSearchers[selectedRank]
                    if(initializedLists[selectedName].__len__() > 0):
                        nonemptyList = True

                #We save the source to which we associate the result
                sources.append(selectedName)

                # Generation of a random number between 0 and 1. The next entry will be selected depending on this number
                rnd = random.random()
                accumulatedSum = 0.0
                dnext = None
                sourceRank = 0
                for entry in initializedLists[selectedName]:
                    accumulatedSum += entry[2]
                    if(accumulatedSum >= rnd):
                        dnext = entry[0]

                        break

                if(dnext is None):
                    dnext = initializedLists[selectedName][0][0]


                dnext.value = 2
                if dnext.snippet is not None:
                    cad = dnext.snippet.split()
                dnext.snippet = ''
                for c in cad:
                    dnext.snippet += re.sub(r'[^\w, ",","."]', '',c) + ' '
                dnext.save()
                results.append(dnext)

                initializedLists = self.removeAndRenormalize(initializedLists, dnext, False)

        if results.__len__() == 0:
            return None

        i = 0
        for metaLnk in results:
            i += 1
            metaLnk.rank = i
            metaLnk.save()

        return results
