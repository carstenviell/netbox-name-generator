from django.urls import path

from .views import (
    NameGeneratorView,
    NetzwerkgeraetFunktionChangeLogView,
    NetzwerkgeraetFunktionDeleteView,
    NetzwerkgeraetFunktionEditView,
    NetzwerkgeraetFunktionListView,
    NetzwerkgeraetTypChangeLogView,
    NetzwerkgeraetTypDeleteView,
    NetzwerkgeraetTypEditView,
    NetzwerkgeraetTypListView,
    ServerZweckChangeLogView,
    ServerZweckDeleteView,
    ServerZweckEditView,
    ServerZweckListView,
    StandortChangeLogView,
    StandortDeleteView,
    StandortEditView,
    StandortListView,
    VmBereichChangeLogView,
    VmBereichDeleteView,
    VmBereichEditView,
    VmBereichListView,
    VmFunktionChangeLogView,
    VmFunktionDeleteView,
    VmFunktionEditView,
    VmFunktionListView,
)

app_name = 'netbox_name_generator'

urlpatterns = [
    # Name Generator (Hauptseite)
    path('', NameGeneratorView.as_view(), name='index'),

    # Standorte
    path('standorte/', StandortListView.as_view(), name='standort_list'),
    path('standorte/add/', StandortEditView.as_view(), name='standort_add'),
    path('standorte/<int:pk>/edit/', StandortEditView.as_view(), name='standort_edit'),
    path('standorte/<int:pk>/delete/', StandortDeleteView.as_view(), name='standort_delete'),
    path('standorte/<int:pk>/changelog/', StandortChangeLogView.as_view(), name='standort_changelog'),

    # Netzwerkgerät-Typen
    path('ng-typen/', NetzwerkgeraetTypListView.as_view(), name='netzwerkgeraettyp_list'),
    path('ng-typen/add/', NetzwerkgeraetTypEditView.as_view(), name='netzwerkgeraettyp_add'),
    path('ng-typen/<int:pk>/edit/', NetzwerkgeraetTypEditView.as_view(), name='netzwerkgeraettyp_edit'),
    path('ng-typen/<int:pk>/delete/', NetzwerkgeraetTypDeleteView.as_view(), name='netzwerkgeraettyp_delete'),
    path('ng-typen/<int:pk>/changelog/', NetzwerkgeraetTypChangeLogView.as_view(), name='netzwerkgeraettyp_changelog'),

    # Netzwerkgerät-Funktionen
    path('ng-funktionen/', NetzwerkgeraetFunktionListView.as_view(), name='netzwerkgeraetfunktion_list'),
    path('ng-funktionen/add/', NetzwerkgeraetFunktionEditView.as_view(), name='netzwerkgeraetfunktion_add'),
    path('ng-funktionen/<int:pk>/edit/', NetzwerkgeraetFunktionEditView.as_view(), name='netzwerkgeraetfunktion_edit'),
    path('ng-funktionen/<int:pk>/delete/', NetzwerkgeraetFunktionDeleteView.as_view(), name='netzwerkgeraetfunktion_delete'),
    path('ng-funktionen/<int:pk>/changelog/', NetzwerkgeraetFunktionChangeLogView.as_view(), name='netzwerkgeraetfunktion_changelog'),

    # Server-Zwecke
    path('server-zwecke/', ServerZweckListView.as_view(), name='serverzweck_list'),
    path('server-zwecke/add/', ServerZweckEditView.as_view(), name='serverzweck_add'),
    path('server-zwecke/<int:pk>/edit/', ServerZweckEditView.as_view(), name='serverzweck_edit'),
    path('server-zwecke/<int:pk>/delete/', ServerZweckDeleteView.as_view(), name='serverzweck_delete'),
    path('server-zwecke/<int:pk>/changelog/', ServerZweckChangeLogView.as_view(), name='serverzweck_changelog'),

    # VM-Bereiche
    path('vm-bereiche/', VmBereichListView.as_view(), name='vmbereich_list'),
    path('vm-bereiche/add/', VmBereichEditView.as_view(), name='vmbereich_add'),
    path('vm-bereiche/<int:pk>/edit/', VmBereichEditView.as_view(), name='vmbereich_edit'),
    path('vm-bereiche/<int:pk>/delete/', VmBereichDeleteView.as_view(), name='vmbereich_delete'),
    path('vm-bereiche/<int:pk>/changelog/', VmBereichChangeLogView.as_view(), name='vmbereich_changelog'),

    # VM-Funktionen
    path('vm-funktionen/', VmFunktionListView.as_view(), name='vmfunktion_list'),
    path('vm-funktionen/add/', VmFunktionEditView.as_view(), name='vmfunktion_add'),
    path('vm-funktionen/<int:pk>/edit/', VmFunktionEditView.as_view(), name='vmfunktion_edit'),
    path('vm-funktionen/<int:pk>/delete/', VmFunktionDeleteView.as_view(), name='vmfunktion_delete'),
    path('vm-funktionen/<int:pk>/changelog/', VmFunktionChangeLogView.as_view(), name='vmfunktion_changelog'),
]
