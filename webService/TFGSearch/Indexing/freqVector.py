# #
# Integration with Apache Lucene 4.10.1
__author__ = 'javier'

##
# @package TFGSearch.Indexing.freqVector
# Definition of a class that manipulates a document Vector
# @author Javier Sanz-Cruzado Puig
from operator import itemgetter
import sys, jcc, os, lucene, unittest
import cookielib, urllib2
from bs4 import BeautifulSoup
import math

from java.io import *
from org.apache.lucene.analysis import Analyzer
from org.apache.lucene.analysis.core import StopAnalyzer, StopFilter
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import *
from org.apache.lucene.index import *
from org.apache.lucene.index import IndexWriterConfig
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import *
from org.apache.lucene.store import *
from org.apache.lucene.util import BytesRef, Version, BytesRefIterator

## Represents a document or session vector
class FreqVector:
    ## Terms
    vector = None
    ## Frequencies
    freqs = None


    def __init__(self):
        vector = []
        freqs = []

    ##
    # Obtains the inner product of two vectors
    # @param vector1 first vector
    # @param vector2 second vector
    def innerProduct(self, vector):
        ip = 0.0
        i = 0
        for term in self.vector:
            if vector.vector.__contains__(term):
                index = vector.vector.index(term)
                ip += self.freqs[i] * vector.freqs[index]
            i = i + 1
        return ip

    ##
    # Updates the freqVector by adding another freqVector
    # @param self The frequency vector
    # @param vect The other frequency vector
    def addFreqVector(self, vect):
        vectVector = vect.vector
        vectFreqs = vect.freqs

        for term in vectVector:
            ind = vectVector.index(term)
            if self.vector.__contains__(term):
                indSelf = self.vector.index(term)
                self.freqs[indSelf] = self.freqs[indSelf] + vectFreqs[ind]
            else:
                self.vector.append(term)
                self.freqs.append(vectFreqs[ind])

        freqVector = zip(self.vector, self.freqs)
        freqVector = sorted(freqVector, key=itemgetter(1), reverse=True)
        self.vector = list()
        self.freqs = list()
        for el in freqVector:
            self.vector.append(el[0])
            self.freqs.append(el[1])

    ##
    # Obtains the cosine similarity of two freqVectors
    #  @param self The frequency vector
    #  @param self The other frequency vector
    def cosineSimilarity(self, vector):
        norm1 = self.norm()
        norm2 = vector.norm()
        inner = self.innerProduct(vector)
        if norm1 > 0 and norm2 > 0:
            cosine = inner / (norm1 * norm2)
        else:
            cosine = 0
        return cosine

    ##
    # Calculates the norm of the vector
    def norm(self):
        nrm = 0.0
        for freq in self.freqs:
            nrm = nrm + freq * freq
        return math.sqrt(nrm)

    ##
    # Updates the freqVector from a given text. The freqVector will be sorted by frequency, from max to min
    # @param self The frequency vector
    # @param text The text to analyze
    def getFreqVectorFromText(self, text):
        # Initialization of Java Virtual Machine with Lucene
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()
        indexDir = "res/index"

        stopWords = []

        stopWordsSet = StopFilter.makeStopSet(Version.LUCENE_CURRENT, stopWords)

        analyzer = StopAnalyzer(Version.LUCENE_CURRENT, stopWordsSet)
        directory = SimpleFSDirectory(File(indexDir))
        conf = IndexWriterConfig(Version.LUCENE_4_10_1, analyzer)
        rebuild = True
        if rebuild:
            conf.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        else:
            conf.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)

        iwriter = IndexWriter(directory, conf)

        doc = Document()
        doc.add(Field("docName", 'url', Field.Store.YES, Field.Index.NOT_ANALYZED))
        doc.add(Field("content", text, Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.YES))
        iwriter.addDocument(doc)
        iwriter.close()

        ireader = IndexReader.open(directory)

        freqVector = []
        docVector = ireader.getTermVector(0, "content")

        termsEnum = docVector.iterator(None)
        for term in BytesRefIterator.cast_(termsEnum):
            text = term.utf8ToString()
            freq = termsEnum.totalTermFreq()
            freqVector.append((text, freq))

        freqVector = sorted(freqVector, key=itemgetter(1), reverse=True)
        self.vector = list()
        self.freqs = list()
        for el in freqVector:
            self.vector.append(el[0])
            self.freqs.append(el[1])