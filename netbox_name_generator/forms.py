from django import forms
from django.urls import reverse

from .name_logic import (
    STANDORTE,
    NETZWERKGERAET_TYPEN,
    NETZWERKGERAET_FUNKTIONEN,
    SERVER_ZWECKE,
    VM_BEREICHE,
    VM_FUNKTIONEN,
    generate_netzwerkgeraet,
    generate_server,
    generate_pc,
    generate_notebook,
    generate_vm,
)


# ---------------------------------------------------------------------------
# Choice-Tupel
# ---------------------------------------------------------------------------

SYSTEM_TYPE_CHOICES = [
    ('', '— Systemtyp wählen —'),
    ('netzwerkgeraet', 'Netzwerkgerät (Switch, Firewall, Storage, AP)'),
    ('server',         'Physischer Server'),
    ('pc',             'Desktop-PC'),
    ('notebook',       'Notebook'),
    ('vm',             'Virtuelle Maschine'),
]

STANDORT_CHOICES = [('', '— Standort —')] + [(s, s) for s in STANDORTE]

NG_TYP_CHOICES = [('', '— Typ —')] + [(t, t) for t in NETZWERKGERAET_TYPEN]

# Alle Funktion-Optionen für Netzwerkgeräte (werden per JS gefiltert)
NG_FUNKTION_CHOICES = [('', '— Funktion —')]
for _typ, _funktionen in NETZWERKGERAET_FUNKTIONEN.items():
    for _f in _funktionen:
        if (_f, _f) not in NG_FUNKTION_CHOICES:
            NG_FUNKTION_CHOICES.append((_f, _f))

SRV_ZWECK_CHOICES = (
    [('', '— Zweck —')]
    + [(z, z) for z in SERVER_ZWECKE]
    + [('__frei__', 'Freitext …')]
)

PC_KENNUNG_TYPE_CHOICES = [
    ('abteilung', 'Abteilungskürzel (mit Auto-Nummerierung)'),
    ('inventar',  'Inventarnummer (direkt)'),
]

VM_BEREICH_CHOICES = [('', '— Bereich —')] + [(b, b) for b in VM_BEREICHE]

VM_FUNKTION_CHOICES = (
    [('', '— Funktion —')]
    + [(f, f) for f in VM_FUNKTIONEN]
    + [('__frei__', 'Freitext …')]
)


# ---------------------------------------------------------------------------
# Formular
# ---------------------------------------------------------------------------

class NameGeneratorForm(forms.Form):
    # Haupt-Selektor
    system_type = forms.ChoiceField(
        choices=SYSTEM_TYPE_CHOICES,
        label='Systemtyp',
    )

    # --- Netzwerkgerät ---
    ng_standort = forms.ChoiceField(
        choices=STANDORT_CHOICES,
        label='Standort',
        required=False,
    )
    ng_typ = forms.ChoiceField(
        choices=NG_TYP_CHOICES,
        label='Gerätetyp',
        required=False,
    )
    ng_funktion = forms.ChoiceField(
        choices=NG_FUNKTION_CHOICES,
        label='Funktion',
        required=False,
    )
    ng_rackid = forms.CharField(
        label='Rack-ID',
        max_length=6,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'z. B. NGV'}),
    )

    # --- Server ---
    srv_standort = forms.ChoiceField(
        choices=STANDORT_CHOICES,
        label='Standort',
        required=False,
    )
    srv_zweck = forms.ChoiceField(
        choices=SRV_ZWECK_CHOICES,
        label='Zweck',
        required=False,
    )
    srv_zweck_frei = forms.CharField(
        label='Zweck (Freitext, max. 4 Zeichen)',
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'z. B. BKUP'}),
    )

    # --- Desktop-PC ---
    pc_standort = forms.ChoiceField(
        choices=STANDORT_CHOICES,
        label='Standort',
        required=False,
    )
    pc_kennung_type = forms.ChoiceField(
        choices=PC_KENNUNG_TYPE_CHOICES,
        label='Kennungstyp',
        required=False,
    )
    pc_kennung = forms.CharField(
        label='Kürzel / Inventarnummer',
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'z. B. MARK oder INV0042'}),
    )

    # --- Notebook ---
    nb_kuerzel = forms.CharField(
        label='Benutzerkürzel',
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'z. B. SCHMIDTH'}),
    )

    # --- Virtuelle Maschine ---
    vm_bereich = forms.ChoiceField(
        choices=VM_BEREICH_CHOICES,
        label='Bereich',
        required=False,
    )
    vm_funktion = forms.ChoiceField(
        choices=VM_FUNKTION_CHOICES,
        label='Funktion',
        required=False,
    )
    vm_funktion_frei = forms.CharField(
        label='Funktion (Freitext, max. 3 Zeichen)',
        max_length=3,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'z. B. MON'}),
    )

    # Ergebnis-Attribute (werden in clean() gesetzt)
    generated_name: str = ''
    target_url: str = ''

    def clean(self):
        cleaned = super().clean()
        system_type = cleaned.get('system_type')

        if not system_type:
            raise forms.ValidationError('Bitte einen Systemtyp auswählen.')

        # Lazy Import hier, damit name_logic testbar ohne Django bleibt
        from dcim.models import Device
        from virtualization.models import VirtualMachine

        existing_names: set[str] = (
            set(Device.objects.values_list('name', flat=True))
            | set(VirtualMachine.objects.values_list('name', flat=True))
        )

        try:
            if system_type == 'netzwerkgeraet':
                name = self._clean_netzwerkgeraet(cleaned, existing_names)
                url_base = reverse('dcim:device_add')

            elif system_type == 'server':
                name = self._clean_server(cleaned, existing_names)
                url_base = reverse('dcim:device_add')

            elif system_type == 'pc':
                name = self._clean_pc(cleaned, existing_names)
                url_base = reverse('dcim:device_add')

            elif system_type == 'notebook':
                name = self._clean_notebook(cleaned)
                url_base = reverse('dcim:device_add')

            elif system_type == 'vm':
                name = self._clean_vm(cleaned, existing_names)
                url_base = reverse('virtualization:virtualmachine_add')

            else:
                raise forms.ValidationError(f'Unbekannter Systemtyp: {system_type}')

        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc

        self.generated_name = name
        self.target_url = f'{url_base}?name={name}'
        return cleaned

    # --- Typ-spezifische clean-Methoden ---

    def _clean_netzwerkgeraet(self, cleaned: dict, existing_names: set) -> str:
        standort = cleaned.get('ng_standort', '')
        typ      = cleaned.get('ng_typ', '')
        funktion = cleaned.get('ng_funktion', '')
        rackid   = cleaned.get('ng_rackid', '').upper().strip()

        if not standort:
            raise forms.ValidationError('Bitte einen Standort für das Netzwerkgerät wählen.')
        if not typ:
            raise forms.ValidationError('Bitte einen Gerätetyp wählen.')
        if not rackid:
            raise forms.ValidationError('Bitte eine Rack-ID eingeben.')

        # AP hat keine Funktion
        if typ == 'AP':
            funktion = ''
        else:
            if not funktion:
                raise forms.ValidationError('Bitte eine Funktion für das Netzwerkgerät wählen.')

        return generate_netzwerkgeraet(standort, typ, funktion, rackid, existing_names)

    def _clean_server(self, cleaned: dict, existing_names: set) -> str:
        standort   = cleaned.get('srv_standort', '')
        zweck      = cleaned.get('srv_zweck', '')
        zweck_frei = cleaned.get('srv_zweck_frei', '').upper().strip()

        if not standort:
            raise forms.ValidationError('Bitte einen Standort für den Server wählen.')

        if zweck == '__frei__':
            if not zweck_frei:
                raise forms.ValidationError('Bitte einen Freitext-Zweck eingeben.')
            zweck = zweck_frei
        elif not zweck:
            raise forms.ValidationError('Bitte einen Zweck für den Server wählen.')

        return generate_server(standort, zweck, existing_names)

    def _clean_pc(self, cleaned: dict, existing_names: set) -> str:
        standort     = cleaned.get('pc_standort', '')
        kennung_type = cleaned.get('pc_kennung_type', 'abteilung')
        kennung      = cleaned.get('pc_kennung', '').upper().strip()

        if not standort:
            raise forms.ValidationError('Bitte einen Standort für den PC wählen.')
        if not kennung:
            raise forms.ValidationError('Bitte ein Kürzel oder eine Inventarnummer eingeben.')

        return generate_pc(standort, kennung_type, kennung, existing_names)

    def _clean_notebook(self, cleaned: dict) -> str:
        kuerzel = cleaned.get('nb_kuerzel', '').upper().strip()

        if not kuerzel:
            raise forms.ValidationError('Bitte ein Benutzerkürzel eingeben.')

        return generate_notebook(kuerzel)

    def _clean_vm(self, cleaned: dict, existing_names: set) -> str:
        bereich       = cleaned.get('vm_bereich', '')
        funktion      = cleaned.get('vm_funktion', '')
        funktion_frei = cleaned.get('vm_funktion_frei', '').upper().strip()

        if not bereich:
            raise forms.ValidationError('Bitte einen Bereich für die VM wählen.')

        if funktion == '__frei__':
            if not funktion_frei:
                raise forms.ValidationError('Bitte eine Freitext-Funktion eingeben.')
            funktion = funktion_frei
        elif not funktion:
            raise forms.ValidationError('Bitte eine Funktion für die VM wählen.')

        return generate_vm(bereich, funktion, existing_names)
