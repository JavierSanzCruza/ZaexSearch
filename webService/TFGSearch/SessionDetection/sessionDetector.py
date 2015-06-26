__author__ = 'javier'
from abc import ABCMeta, abstractmethod

class SessionDetector:
    __metaclass__= ABCMeta


    ##
    # Devuelve la sesion a la que pertenece una query
    # @param self El detector de sesion
    # @param client Cliente que ha realizado la busqueda
    # @param query Consulta realizada al metabuscador
    @abstractmethod
    def detectSession(self, client, query): pass