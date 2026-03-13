import json

from django import forms
from django.urls import reverse

from .name_logic import (
    generate_netzwerkgeraet,
    generate_notebook,
    generate_pc,
    generate_server,
    generate_vm,
)


# ---------------------------------------------------------------------------
# Statische Choice-Tupel (nicht DB-abhängig)
# ---------------------------------------------------------------------------

SYSTEM_TYPE_CHOICES = [
    ('', '— Systemtyp wählen —'),
    ('netzwerkgeraet', 'Netzwerkgerät (Switch, Firewall, Storage, AP)'),
    ('server',         'Physischer Server'),
    ('pc',             'Desktop-PC'),
    ('notebook',       'Notebook'),
    ('vm',             'Virtuelle Maschine'),
]

PC_KENNUNG_TYPE_CHOICES = [
    ('abteilung', 'Abteilungskürzel (mit Auto-Nummerierung)'),
    ('inventar',  'Inventarnummer (direkt)'),
]


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
        choices=[],
        label='Standort',
        required=False,
    )
    ng_typ = forms.ChoiceField(
        choices=[],
        label='Gerätetyp',
        required=False,
    )
    ng_funktion = forms.ChoiceField(
        choices=[],
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
        choices=[],
        label='Standort',
        required=False,
    )
    srv_zweck = forms.ChoiceField(
        choices=[],
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
        choices=[],
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
        choices=[],
        label='Bereich',
        required=False,
    )
    vm_funktion = forms.ChoiceField(
        choices=[],
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lazy Import, damit name_logic testbar ohne Django bleibt
        from .models import (
            NetzwerkgeraetFunktion,
            NetzwerkgeraetTyp,
            ServerZweck,
            Standort,
            VmBereich,
            VmFunktion,
        )

        standorte = list(Standort.objects.select_related('site').order_by('kuerzel'))
        typen = list(NetzwerkgeraetTyp.objects.prefetch_related('funktionen').order_by('kuerzel'))
        serverzwecke = list(ServerZweck.objects.order_by('kuerzel'))
        vmbereiche = list(VmBereich.objects.order_by('kuerzel'))
        vmfunktionen = list(VmFunktion.objects.order_by('kuerzel'))

        # Standort-Label: zeigt verknüpfte NetBox-Site wenn vorhanden
        def standort_label(s):
            return f'{s.kuerzel} – {s.site.name}' if s.site_id else s.kuerzel

        standort_choices = [('', '— Standort —')] + [(s.kuerzel, standort_label(s)) for s in standorte]
        self.fields['ng_standort'].choices = standort_choices
        self.fields['srv_standort'].choices = standort_choices
        self.fields['pc_standort'].choices = standort_choices

        self.fields['ng_typ'].choices = [('', '— Typ —')] + [(t.kuerzel, t.kuerzel) for t in typen]

        # Alle Funktionen für ng_funktion (JS filtert nach Typ)
        alle_funktionen: set[str] = set()
        for t in typen:
            for f in t.funktionen.all():
                alle_funktionen.add(f.kuerzel)
        self.fields['ng_funktion'].choices = (
            [('', '— Funktion —')]
            + [(f, f) for f in sorted(alle_funktionen)]
        )

        self.fields['srv_zweck'].choices = (
            [('', '— Zweck —')]
            + [(z.kuerzel, z.kuerzel) for z in serverzwecke]
            + [('__frei__', 'Freitext …')]
        )

        self.fields['vm_bereich'].choices = (
            [('', '— Bereich —')]
            + [(b.kuerzel, b.kuerzel) for b in vmbereiche]
        )

        self.fields['vm_funktion'].choices = (
            [('', '— Funktion —')]
            + [(f.kuerzel, f.kuerzel) for f in vmfunktionen]
            + [('__frei__', 'Freitext …')]
        )

        # JSON-Attribute für JavaScript
        funktionen_by_typ: dict[str, list[str]] = {}
        typ_hat_funktion: dict[str, bool] = {}
        for t in typen:
            funktionen_by_typ[t.kuerzel] = [f.kuerzel for f in t.funktionen.all()]
            typ_hat_funktion[t.kuerzel] = t.hat_funktion

        self.ng_funktionen_json = json.dumps(funktionen_by_typ)
        self.ng_typ_hat_funktion_json = json.dumps(typ_hat_funktion)

    def clean(self):
        cleaned = super().clean()
        system_type = cleaned.get('system_type')

        if not system_type:
            raise forms.ValidationError('Bitte einen Systemtyp auswählen.')

        from dcim.models import Device
        from virtualization.models import VirtualMachine

        existing_names: set[str] = (
            set(Device.objects.values_list('name', flat=True))
            | set(VirtualMachine.objects.values_list('name', flat=True))
        )

        # Standort-Kürzel je Systemtyp ermitteln (für Site-Vorausfüllung)
        standort_kuerzel_map = {
            'netzwerkgeraet': cleaned.get('ng_standort', ''),
            'server':         cleaned.get('srv_standort', ''),
            'pc':             cleaned.get('pc_standort', ''),
        }
        standort_kuerzel = standort_kuerzel_map.get(system_type, '')

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

        # Site-ID des gewählten Standorts ermitteln
        site_id = None
        if standort_kuerzel:
            from .models import Standort as StandortModel
            try:
                site_id = StandortModel.objects.get(kuerzel=standort_kuerzel).site_id
            except StandortModel.DoesNotExist:
                pass

        # Redirect-URL aufbauen
        params = f'name={name}'
        if site_id:
            params += f'&site={site_id}'

        self.generated_name = name
        self.target_url = f'{url_base}?{params}'
        return cleaned

    # --- Typ-spezifische clean-Methoden ---

    def _clean_netzwerkgeraet(self, cleaned: dict, existing_names: set) -> str:
        from .models import NetzwerkgeraetTyp

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

        # Prüfen ob der Typ eine Funktion erfordert
        try:
            typ_obj = NetzwerkgeraetTyp.objects.get(kuerzel=typ)
            hat_funktion = typ_obj.hat_funktion
        except NetzwerkgeraetTyp.DoesNotExist:
            hat_funktion = True

        if not hat_funktion:
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
