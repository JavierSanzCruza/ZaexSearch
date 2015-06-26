# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-

## @package TFGSearch.SessionDetection
__author__ = 'javier'


from TFGSearch.SessionDetection.sessionDetector import *
from TFGSearch.models import *
from TFGSearch.Indexing.freqVector import FreqVector

##
# Dictionary that represents an enumeration. Shows the different kinds of search patterns
SearchPattern = {'REPETITION' :0, 'REORDERING': 1, 'GENERALISATION' : 2, 'SPECIALISATION' : 3, 'REFORMULATION' : 4, 'NEW' : 5, 'OTHERS' : 6}

class SearchPatternDetector(SessionDetector):

    def detectSession(self, client, query, oldSession):
        #obtenemos la sesion activa, o, en caso de no existir, creamos otra.

	query = query
        if oldSession is None:
            newSession = Session()
            newSession.timestamp = timezone.now()
            newSession.active = True
            newSession.clientID = client
            return newSession
        else:
            searchList = Search.objects.filter(sessionID__exact = oldSession).order_by('-timestamp')
            #Si se acaba de crear la sesion
            if searchList is None or searchList.__len__() == 0:
                return oldSession

            oldQuery = searchList.first().query

            pattern = SearchPatternDetector.searchPatternDetection(oldQuery, query)

            if pattern == SearchPattern['NEW'] or pattern == SearchPattern['OTHERS']:
                newSession = Session()
                newSession.timestamp = timezone.now()
                newSession.active = True
                newSession.clientID = client
            else:
                newSession = oldSession

            return newSession

    ##
    # Analizes two query strings to determinate the relationship between them
    # @param self The class SearchPatternDetector
    # @param oldQuery The oldest query string
    # @param newQuery The newest query string
    # @return The corresponding search pattern.
    #         REPETITION if both queries are the same
    #         REORDERING if both queries have the same terms, but in different order
    #         GENERALISATION if the old query is more specialised than the new one
    #         SPECIALISATION if the new query is more specialised than the old one
    #         NEW if both queries do not have terms in common
    #         OTHERS if error
    @staticmethod
    def searchPatternDetection(oldQuery, newQuery):

        oldQueryFreqVector = FreqVector()
        oldQueryFreqVector.getFreqVectorFromText(oldQuery)
        newQueryFreqVector = FreqVector()
        newQueryFreqVector.getFreqVectorFromText(newQuery)

        oldQuerySet = oldQueryFreqVector.vector
        newQuerySet = newQueryFreqVector.vector
        commonTermsSet = set()
        onlyOldTermsSet = set()
        onlyNewTermsSet = set()

        trimOld = ''.join(oldQuerySet)
        trimNew = ''.join(newQuerySet)

        for word in oldQuerySet:
            if newQuerySet.__contains__(word):
                commonTermsSet.add(word)
            else:
                onlyOldTermsSet.add(word)

        for word in newQuerySet:
            if commonTermsSet.__contains__(word) == False:
                onlyNewTermsSet.add(word)

        pattern = SearchPattern['OTHERS']
        if onlyOldTermsSet.__len__() == 0 and onlyNewTermsSet.__len__() == 0:
            pattern = SearchPattern['REPETITION']
        elif commonTermsSet.__len__() > 0 and onlyOldTermsSet.__len__() == 0 and onlyNewTermsSet.__len__() == 0:
            pattern = SearchPattern['REORDERING']
        elif commonTermsSet.__len__() > 0 and onlyOldTermsSet.__len__() > 0 and onlyNewTermsSet.__len__() == 0:
            pattern = SearchPattern['GENERALISATION']
        elif commonTermsSet.__len__() > 0 and onlyOldTermsSet.__len__() == 0 and onlyNewTermsSet.__len__() > 0:
            pattern = SearchPattern['SPECIALISATION']
        elif commonTermsSet.__len__() > 0 and onlyOldTermsSet.__len__() > 0 and onlyNewTermsSet.__len__() > 0:
            pattern = SearchPattern['REFORMULATION']
        elif commonTermsSet.__len__() == 0:
            pattern = SearchPattern['NEW']

        return pattern
