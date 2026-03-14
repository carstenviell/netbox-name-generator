import json

from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
    ('', _('— Select System Type —')),
    ('netzwerkgeraet', _('Network Device (Switch, Firewall, Storage, AP)')),
    ('server',         _('Physical Server')),
    ('pc',             _('Desktop PC')),
    ('notebook',       'Notebook'),
    ('vm',             _('Virtual Machine')),
]

PC_KENNUNG_TYPE_CHOICES = [
    ('abteilung', _('Department Code (with Auto-Numbering)')),
    ('inventar',  _('Inventory Number (direct)')),
]


# ---------------------------------------------------------------------------
# Formular
# ---------------------------------------------------------------------------

class NameGeneratorForm(forms.Form):
    # Haupt-Selektor
    system_type = forms.ChoiceField(
        choices=SYSTEM_TYPE_CHOICES,
        label=_('System Type'),
    )

    # --- Netzwerkgerät ---
    ng_standort = forms.ChoiceField(
        choices=[],
        label=_('Site'),
        required=False,
    )
    ng_typ = forms.ChoiceField(
        choices=[],
        label=_('Device Type'),
        required=False,
    )
    ng_funktion = forms.ChoiceField(
        choices=[],
        label=_('Function'),
        required=False,
        widget=forms.Select(attrs={'class': 'no-ts'}),
    )
    ng_rackid = forms.CharField(
        label=_('Rack ID'),
        max_length=6,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'z. B. NGV'}),
    )

    # --- Server ---
    srv_standort = forms.ChoiceField(
        choices=[],
        label=_('Site'),
        required=False,
    )
    srv_zweck = forms.ChoiceField(
        choices=[],
        label=_('Purpose'),
        required=False,
    )
    srv_zweck_frei = forms.CharField(
        label=_('Purpose (free-text, max. 4 characters)'),
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'z. B. BKUP'}),
    )

    # --- Desktop-PC ---
    pc_standort = forms.ChoiceField(
        choices=[],
        label=_('Site'),
        required=False,
    )
    pc_kennung_type = forms.ChoiceField(
        choices=PC_KENNUNG_TYPE_CHOICES,
        label=_('Identifier Type'),
        required=False,
    )
    pc_kennung = forms.CharField(
        label=_('Code / Inventory Number'),
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'z. B. MARK oder INV0042'}),
    )

    # --- Notebook ---
    nb_kuerzel = forms.CharField(
        label=_('User Code'),
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'z. B. SCHMIDTH'}),
    )

    # --- Virtuelle Maschine ---
    vm_bereich = forms.ChoiceField(
        choices=[],
        label=_('Area'),
        required=False,
    )
    vm_funktion = forms.ChoiceField(
        choices=[],
        label=_('Function'),
        required=False,
    )
    vm_funktion_frei = forms.CharField(
        label=_('Function (free-text, max. 3 characters)'),
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

        def label(kuerzel, beschreibung):
            return f'{kuerzel} – {beschreibung}' if beschreibung else kuerzel

        # Standort-Label: verknüpfte NetBox-Site, sonst Beschreibung
        def standort_label(s):
            if s.site_id:
                return f'{s.kuerzel} – {s.site.name}'
            return label(s.kuerzel, s.beschreibung)

        standort_choices = [('', _('— Site —'))] + [(s.kuerzel, standort_label(s)) for s in standorte]
        self.fields['ng_standort'].choices = standort_choices
        self.fields['srv_standort'].choices = standort_choices
        self.fields['pc_standort'].choices = standort_choices

        self.fields['ng_typ'].choices = (
            [('', _('— Type —'))]
            + [(t.kuerzel, label(t.kuerzel, t.beschreibung)) for t in typen]
        )

        # Alle Funktionen für ng_funktion (JS filtert nach Typ)
        alle_funktionen: dict[str, str] = {}
        for t in typen:
            for f in t.funktionen.all():
                if f.kuerzel not in alle_funktionen:
                    alle_funktionen[f.kuerzel] = label(f.kuerzel, f.beschreibung)
        self.fields['ng_funktion'].choices = (
            [('', _('— Function —'))]
            + [(k, v) for k, v in sorted(alle_funktionen.items())]
        )

        self.fields['srv_zweck'].choices = (
            [('', _('— Purpose —'))]
            + [(z.kuerzel, label(z.kuerzel, z.beschreibung)) for z in serverzwecke]
            + [('__frei__', _('Free-text …'))]
        )

        self.fields['vm_bereich'].choices = (
            [('', _('— Area —'))]
            + [(b.kuerzel, label(b.kuerzel, b.beschreibung)) for b in vmbereiche]
        )

        self.fields['vm_funktion'].choices = (
            [('', _('— Function —'))]
            + [(f.kuerzel, label(f.kuerzel, f.beschreibung)) for f in vmfunktionen]
            + [('__frei__', _('Free-text …'))]
        )

        # JSON-Attribute für JavaScript
        # ng_funktionen_json: {typ: [{v: kuerzel, l: label}, ...]}
        funktionen_by_typ: dict[str, list] = {}
        typ_hat_funktion: dict[str, bool] = {}
        for t in typen:
            funktionen_by_typ[t.kuerzel] = [
                {'v': f.kuerzel, 'l': label(f.kuerzel, f.beschreibung)}
                for f in t.funktionen.all()
            ]
            typ_hat_funktion[t.kuerzel] = t.hat_funktion

        self.ng_funktionen_json = json.dumps(funktionen_by_typ)
        self.ng_typ_hat_funktion_json = json.dumps(typ_hat_funktion)

        # Standort → site_id und Racks pro site_id für JS
        from dcim.models import Rack
        standort_site_map = {s.kuerzel: s.site_id for s in standorte if s.site_id}
        site_ids = list(standort_site_map.values())
        racks_by_site: dict[int, list] = {}
        for rack in Rack.objects.filter(site_id__in=site_ids).select_related('location').order_by('name'):
            label_text = f'{rack.name} ({rack.location.name})' if rack.location_id else rack.name
            racks_by_site.setdefault(rack.site_id, []).append({'v': rack.name, 'l': label_text})

        self.ng_standort_site_json = json.dumps(standort_site_map)
        self.ng_racks_json = json.dumps(racks_by_site)

    def clean(self):
        cleaned = super().clean()
        system_type = cleaned.get('system_type')

        if not system_type:
            raise forms.ValidationError(_('Please select a system type.'))

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
                raise forms.ValidationError(_('Unknown system type:') + f' {system_type}')

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

        # Rack und Location aus gewähltem Rack-Namen ermitteln (nur Netzwerkgeräte)
        rack_id = None
        location_id = None
        if system_type == 'netzwerkgeraet' and site_id:
            from dcim.models import Rack
            rackid_value = cleaned.get('ng_rackid', '').strip()
            if rackid_value:
                rack = Rack.objects.filter(site_id=site_id, name=rackid_value).first()
                if rack:
                    rack_id = rack.id
                    location_id = rack.location_id

        # Redirect-URL aufbauen
        params = f'name={name}'
        if site_id:
            params += f'&site={site_id}'
        if rack_id:
            params += f'&rack={rack_id}'
        if location_id:
            params += f'&location={location_id}'

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
            raise forms.ValidationError(_('Please select a site for the network device.'))
        if not typ:
            raise forms.ValidationError(_('Please select a device type.'))
        if not rackid:
            raise forms.ValidationError(_('Please enter a Rack ID.'))

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
                raise forms.ValidationError(_('Please select a function for the network device.'))

        return generate_netzwerkgeraet(standort, typ, funktion, rackid, existing_names)

    def _clean_server(self, cleaned: dict, existing_names: set) -> str:
        standort   = cleaned.get('srv_standort', '')
        zweck      = cleaned.get('srv_zweck', '')
        zweck_frei = cleaned.get('srv_zweck_frei', '').upper().strip()

        if not standort:
            raise forms.ValidationError(_('Please select a site for the server.'))

        if zweck == '__frei__':
            if not zweck_frei:
                raise forms.ValidationError(_('Please enter a free-text purpose.'))
            zweck = zweck_frei
        elif not zweck:
            raise forms.ValidationError(_('Please select a purpose for the server.'))

        return generate_server(standort, zweck, existing_names)

    def _clean_pc(self, cleaned: dict, existing_names: set) -> str:
        standort     = cleaned.get('pc_standort', '')
        kennung_type = cleaned.get('pc_kennung_type', 'abteilung')
        kennung      = cleaned.get('pc_kennung', '').upper().strip()

        if not standort:
            raise forms.ValidationError(_('Please select a site for the PC.'))
        if not kennung:
            raise forms.ValidationError(_('Please enter a code or inventory number.'))

        return generate_pc(standort, kennung_type, kennung, existing_names)

    def _clean_notebook(self, cleaned: dict) -> str:
        kuerzel = cleaned.get('nb_kuerzel', '').upper().strip()

        if not kuerzel:
            raise forms.ValidationError(_('Please enter a user code.'))

        return generate_notebook(kuerzel)

    def _clean_vm(self, cleaned: dict, existing_names: set) -> str:
        bereich       = cleaned.get('vm_bereich', '')
        funktion      = cleaned.get('vm_funktion', '')
        funktion_frei = cleaned.get('vm_funktion_frei', '').upper().strip()

        if not bereich:
            raise forms.ValidationError(_('Please select an area for the VM.'))

        if funktion == '__frei__':
            if not funktion_frei:
                raise forms.ValidationError(_('Please enter a free-text function.'))
            funktion = funktion_frei
        elif not funktion:
            raise forms.ValidationError(_('Please select a function for the VM.'))

        return generate_vm(bereich, funktion, existing_names)
