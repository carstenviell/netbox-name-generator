from dcim.models import Site
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField

from .models import (
    NetzwerkgeraetFunktion,
    NetzwerkgeraetTyp,
    ServerZweck,
    Standort,
    VmBereich,
    VmFunktion,
)


class StandortForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='NetBox-Site',
        help_text='Verknüpfung mit dem NetBox-Standort – wird beim Gerät-Anlegen vorausgefüllt.',
    )

    class Meta:
        model = Standort
        fields = ('kuerzel', 'beschreibung', 'site', 'tags')


class NetzwerkgeraetTypForm(NetBoxModelForm):
    class Meta:
        model = NetzwerkgeraetTyp
        fields = ('kuerzel', 'beschreibung', 'hat_funktion', 'tags')


class NetzwerkgeraetFunktionForm(NetBoxModelForm):
    class Meta:
        model = NetzwerkgeraetFunktion
        fields = ('typ', 'kuerzel', 'beschreibung', 'tags')


class ServerZweckForm(NetBoxModelForm):
    class Meta:
        model = ServerZweck
        fields = ('kuerzel', 'beschreibung', 'tags')


class VmBereichForm(NetBoxModelForm):
    class Meta:
        model = VmBereich
        fields = ('kuerzel', 'beschreibung', 'tags')


class VmFunktionForm(NetBoxModelForm):
    class Meta:
        model = VmFunktion
        fields = ('kuerzel', 'beschreibung', 'tags')
