## @package TFGSearch.serializers
# Serializers for the WebService

from rest_framework import serializers
from TFGSearch.models import *

## Serializes links Link
class LinkSerializer(serializers.ModelSerializer):
    ## Characteristics of the serializer
    class Meta:
        ## Model (SearchResult)
        model = SearchResult
        ## Fields to serialize
        fields = ('title', 'url', 'snippet', 'rank', 'source', 'value')

## Serializer for clicked links
class ClickedLinkSerializer(serializers.ModelSerializer):
    ## Caracteristicas del serializador
    class Meta:
        ## Modelo del serializador (Clicked Link)
        model = ClickedLink
        ## Campos a serializar (titulo, URL y snippet)
        fields = ('title', 'url', 'snippet')

## Serializer for saved links
class SavedLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedLink
        fields = ('title', 'url', 'snippet', 'query', 'rank')

## Serializer for rankers
class RankerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranker
        fields = ('name', 'evaluation')

## Serializer for evaluated rankers
class EvaluatedRankerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluatedRanker
        fields = ('name', 'evaluation')