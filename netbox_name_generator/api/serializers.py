from netbox.api.serializers import NetBoxModelSerializer
from netbox_name_generator.models import (
    NetzwerkgeraetFunktion,
    NetzwerkgeraetTyp,
    ServerZweck,
    Standort,
    VmBereich,
    VmFunktion,
)


class StandortSerializer(NetBoxModelSerializer):
    class Meta:
        model = Standort
        fields = ('id', 'url', 'display', 'kuerzel', 'beschreibung', 'site', 'created', 'last_updated')


class NetzwerkgeraetTypSerializer(NetBoxModelSerializer):
    class Meta:
        model = NetzwerkgeraetTyp
        fields = ('id', 'url', 'display', 'kuerzel', 'beschreibung', 'hat_funktion', 'created', 'last_updated')


class NetzwerkgeraetFunktionSerializer(NetBoxModelSerializer):
    class Meta:
        model = NetzwerkgeraetFunktion
        fields = ('id', 'url', 'display', 'typ', 'kuerzel', 'beschreibung', 'created', 'last_updated')


class ServerZweckSerializer(NetBoxModelSerializer):
    class Meta:
        model = ServerZweck
        fields = ('id', 'url', 'display', 'kuerzel', 'beschreibung', 'created', 'last_updated')


class VmBereichSerializer(NetBoxModelSerializer):
    class Meta:
        model = VmBereich
        fields = ('id', 'url', 'display', 'kuerzel', 'beschreibung', 'created', 'last_updated')


class VmFunktionSerializer(NetBoxModelSerializer):
    class Meta:
        model = VmFunktion
        fields = ('id', 'url', 'display', 'kuerzel', 'beschreibung', 'created', 'last_updated')
