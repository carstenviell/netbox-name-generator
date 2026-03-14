from netbox.api.viewsets import NetBoxModelViewSet
from netbox_name_generator.models import (
    NetzwerkgeraetFunktion,
    NetzwerkgeraetTyp,
    ServerZweck,
    Standort,
    VmBereich,
    VmFunktion,
)
from .serializers import (
    NetzwerkgeraetFunktionSerializer,
    NetzwerkgeraetTypSerializer,
    ServerZweckSerializer,
    StandortSerializer,
    VmBereichSerializer,
    VmFunktionSerializer,
)


class StandortViewSet(NetBoxModelViewSet):
    queryset = Standort.objects.all()
    serializer_class = StandortSerializer


class NetzwerkgeraetTypViewSet(NetBoxModelViewSet):
    queryset = NetzwerkgeraetTyp.objects.all()
    serializer_class = NetzwerkgeraetTypSerializer


class NetzwerkgeraetFunktionViewSet(NetBoxModelViewSet):
    queryset = NetzwerkgeraetFunktion.objects.select_related('typ')
    serializer_class = NetzwerkgeraetFunktionSerializer


class ServerZweckViewSet(NetBoxModelViewSet):
    queryset = ServerZweck.objects.all()
    serializer_class = ServerZweckSerializer


class VmBereichViewSet(NetBoxModelViewSet):
    queryset = VmBereich.objects.all()
    serializer_class = VmBereichSerializer


class VmFunktionViewSet(NetBoxModelViewSet):
    queryset = VmFunktion.objects.all()
    serializer_class = VmFunktionSerializer
