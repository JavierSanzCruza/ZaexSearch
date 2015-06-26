## @package TFGSearch.admin
# Clases para el administrador de la aplicacion TFGSearch
from django.contrib import admin
from TFGSearch.models import Client, Session, Search, SearchResult, ClickedLink

## Clase para mostrar los datos de las busquedas en el administrador de Sesiones
class SearchInLine(admin.StackedInline):
    ## Modelo a utilizar (Search)
    model=Search
    ## Elementos adicionales para crear mostrados en el administrador
    extra = 0

## Clase para mostrar los datos de las sesiones en el administrador de Clientes
class SessionInLine(admin.TabularInline):
    ## Modelo a utilizar (Session)
    model=Session
    ## Elementos adicionales para crear mostrados en el administrador
    extra = 0

## Clase para mostrar los resultados de las busquedas en el administrador de Busqueda
class SearchResultInLine(admin.StackedInline):
    ## Modelo a utilizar (SearchResult)
    model=SearchResult
    ## Elementos adicionales para crear mostrados en el administrador
    extra = 0

## Clase para mostrar los links clickados en el administrador de Sesiones y en el de Resultados
class ClickedLinkInLine(admin.StackedInline):
    ## Modelo a utilizar (ClickedLink)
    model=ClickedLink
    ## Elementos adicionales para crear mostrados en el administrador
    extra = 0

## Clase para mostrar los datos de los clientes en el administrador de la aplicacion
class ClientAdmin(admin.ModelAdmin):
    ## Configuracion de los campos de Cliente a mostrar en el administrador
    fieldsets = [
        ('Client data', {'fields': ['clientIP', 'userAgent']}),
    ]
    ## Configuracion de los campos a mostrar en lista
    list_display = ('clientID', 'clientIP', 'userAgent')
    ## Campos de busqueda en el buscador del administrador
    search_fields =  ['clientID']
    ## Sesiones del cliente
    inlines = [SessionInLine]

## Clase para mostrar los datos de las sesiones en el administrador de la aplicacion
class SessionAdmin(admin.ModelAdmin):
    ## Configuracion de los campos de Session a mostrar en el administrador
    fieldsets = [
        ('Client', {'fields': ['clientID',]}),
        ('Session data', {'fields': ['timestamp', 'active']})
    ]

    ## Configuracion de los campos a mostrar en lista
    list_display = ('sessionID', 'clientID', 'timestamp', 'active')
    ## Campos de busqueda en el buscador del administrador
    search_fields = ['sessionID', 'clientID__clientID']
    ## Busquedas realizadas en la sesion, y links clickados en la misma
    inlines = [SearchInLine, ClickedLinkInLine]

## Clase para mostrar los datos de las busquedas en el administrador de la aplicacion
class SearchAdmin(admin.ModelAdmin):
    #Configuracion de los campos de Search a mostrar en el administrador
    fieldsets = [
        ('Session', {'fields': ['sessionID',]}),
        ('Search Data', {'fields': ['query', 'timestamp', 'numResults']}),
    ]

    ## Configuracion de los campos a mostrar en lista
    list_display = ('searchID', 'sessionID', 'query', 'timestamp', 'numResults')

    ## Campos de busqueda en el buscador del administrador
    search_fields = ['sessionID__sessionID', 'searchID', 'query']
    ## Resultados de la busqueda
    inlines = [SearchResultInLine]

## Clase para mostrar los datos de los resultados de las busquedas en el administrador de la aplicacion
class SearchResultAdmin(admin.ModelAdmin):
    #Configuracion de los campos de SearchResult a mostrar en el administrador
    fieldsets = [
        ('Session', {'fields': ['searchID']}),
        ('Search Result Data', {'fields': ['title', 'descr', 'url', 'rank', 'value']}),
    ]

    ## Configuracion de los campos a mostrar en lista
    list_display = ('resultID', 'searchID', 'url', 'rank')
    ## Campos de busqueda en el buscador del administrador
    search_fields = ('resultID', 'searchID__searchID')
    ## Links Clickados (En este caso, si se ha clickado el link
    inlines = [ClickedLinkInLine]

## Clase para mostrar los datos de los links clickados en el administrador de la aplicacion
class ClickedLinkAdmin(admin.ModelAdmin):
    #Configuracion de los campos de ClickedLink a mostrar en el administrador
    fieldsets = [
        ('Session', {'fields': ['sessionID']}),
        ('Search Result', {'fields': ['searchResult']}),
        ('Clicked Link Data', {'fields': ['title', 'url', 'descr']})
    ]

    ## Campos de busqueda en el buscador del administrador
    search_fields = ('searchResult__resultID', 'sessionID__sessionID')
    ## Configuracion de los campos a mostrar en lista
    list_display = ('sessionID', 'searchResult')

#Registramos los modelos en el servidor
admin.site.register(Client, ClientAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Search, SearchAdmin)
admin.site.register(SearchResult, SearchResultAdmin)
admin.site.register(ClickedLink, ClickedLinkAdmin)
# Register your models here.
