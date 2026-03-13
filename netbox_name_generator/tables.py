import django_tables2 as tables
from netbox.tables import NetBoxTable

from .models import (
    NetzwerkgeraetFunktion,
    NetzwerkgeraetTyp,
    ServerZweck,
    Standort,
    VmBereich,
    VmFunktion,
)


class StandortTable(NetBoxTable):
    kuerzel = tables.Column(linkify=True)
    site = tables.Column(linkify=True, verbose_name='NetBox-Site')

    class Meta(NetBoxTable.Meta):
        model = Standort
        fields = ('pk', 'kuerzel', 'beschreibung', 'site', 'actions')
        default_columns = ('kuerzel', 'beschreibung', 'site', 'actions')


class NetzwerkgeraetTypTable(NetBoxTable):
    kuerzel = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = NetzwerkgeraetTyp
        fields = ('pk', 'kuerzel', 'beschreibung', 'hat_funktion', 'actions')
        default_columns = ('kuerzel', 'beschreibung', 'hat_funktion', 'actions')


class NetzwerkgeraetFunktionTable(NetBoxTable):
    kuerzel = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = NetzwerkgeraetFunktion
        fields = ('pk', 'typ', 'kuerzel', 'beschreibung', 'actions')
        default_columns = ('typ', 'kuerzel', 'beschreibung', 'actions')


class ServerZweckTable(NetBoxTable):
    kuerzel = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = ServerZweck
        fields = ('pk', 'kuerzel', 'beschreibung', 'actions')
        default_columns = ('kuerzel', 'beschreibung', 'actions')


class VmBereichTable(NetBoxTable):
    kuerzel = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = VmBereich
        fields = ('pk', 'kuerzel', 'beschreibung', 'actions')
        default_columns = ('kuerzel', 'beschreibung', 'actions')


class VmFunktionTable(NetBoxTable):
    kuerzel = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = VmFunktion
        fields = ('pk', 'kuerzel', 'beschreibung', 'actions')
        default_columns = ('kuerzel', 'beschreibung', 'actions')
