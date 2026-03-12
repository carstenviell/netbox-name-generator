"""
Kernlogik für die Namensgenerierung gemäß IT-Systembezeichnungsrichtlinie.

Erlaubte Zeichen: A-Z, 0-9, Bindestrich (-)
Maximale Länge: 15 Zeichen
"""

import re

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

ERLAUBTE_ZEICHEN = re.compile(r'^[A-Z0-9\-]+$')

STANDORTE = ('RZ1', 'HAU', 'NEB', 'B01')

NETZWERKGERAET_TYPEN = ('SW', 'FW', 'STO', 'AP')

NETZWERKGERAET_FUNKTIONEN = {
    'SW':  ('COR', 'DIS', 'ACC', 'EDG'),
    'FW':  ('EXT', 'INT'),
    'STO': ('SAN', 'NAS'),
    'AP':  (),  # kein Präfix – NUMMER direkt nach TYP
}

SERVER_ZWECKE = ('ADDS', 'SQLP', 'FILE', 'MONI', 'SAP', 'EXCH', 'HYPV')

VM_BEREICHE  = ('APP', 'WEB', 'DB', 'ADM', 'RDS', 'DEV', 'TEST', 'PROD')
VM_FUNKTIONEN = ('BMS', 'RDH', 'NOC', 'SQL', 'CRM', 'ERP', 'AD', 'FIL')


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def validate_name(name: str) -> tuple[bool, str]:
    """
    Prüft, ob ein Name den allgemeinen Regeln entspricht.

    Returns:
        (True, '') wenn gültig
        (False, Fehlermeldung) wenn ungültig
    """
    if not name:
        return False, 'Name darf nicht leer sein.'
    if len(name) > 15:
        return False, f'Name "{name}" ist {len(name)} Zeichen lang (max. 15).'
    if not ERLAUBTE_ZEICHEN.match(name):
        return False, (
            f'Name "{name}" enthält unerlaubte Zeichen. '
            'Nur A-Z, 0-9 und Bindestrich (-) sind zulässig.'
        )
    return True, ''


def _naechste_nummer(prefix: str, existing_names: set[str]) -> str:
    """
    Sucht die kleinste freie zweistellige Nummer (01–99) für den gegebenen
    Präfix (Groß-/Kleinschreibung wird ignoriert).

    Args:
        prefix: Namenspräfix ohne Nummer, z. B. 'RZ1-SRV-ADDS'
        existing_names: Menge bereits vergebener Namen

    Returns:
        Zweistellige Nummer als String, z. B. '01'

    Raises:
        ValueError: wenn alle Nummern 01–99 belegt sind
    """
    prefix_upper = prefix.upper()
    existing_upper = {n.upper() for n in existing_names}

    for n in range(1, 100):
        nummer = f'{n:02d}'
        if f'{prefix_upper}{nummer}' not in existing_upper:
            return nummer

    raise ValueError(
        f'Alle Nummern 01–99 für Präfix "{prefix}" sind bereits vergeben.'
    )


# ---------------------------------------------------------------------------
# Namensgeneratoren
# ---------------------------------------------------------------------------

def generate_netzwerkgeraet(
    standort: str,
    typ: str,
    funktion: str,
    rackid: str,
    existing_names: set[str],
) -> str:
    """
    Schema: [STANDORT]-[TYP]-[FUNKTION][NUMMER][RACKID]
    Länge:  genau 15 Zeichen

    Die erlaubte RACKID-Länge ergibt sich aus: 15 − len(Präfix) − 2 (Nummer)
      SW/FW  → max. 3 Zeichen  (z. B. NGV)
      STO    → max. 2 Zeichen  (z. B. R1)
      AP     → max. 6 Zeichen  (keine Funktion, mehr Platz)

    Beispiel: RZ1-SW-COR01NGV  (3+1+2+1+3+2+3 = 15)

    Args:
        standort:       z. B. 'RZ1'
        typ:            z. B. 'SW', 'FW', 'STO', 'AP'
        funktion:       z. B. 'COR', 'EXT', 'SAN'  (leer für AP)
        rackid:         Rack-Bezeichner, Länge abhängig vom Typ (s. o.)
        existing_names: bereits belegte Namen

    Returns:
        Generierter Name, z. B. 'RZ1-SW-COR01NGV'
    """
    standort = standort.upper().strip()
    typ      = typ.upper().strip()
    funktion = funktion.upper().strip()
    rackid   = rackid.upper().strip()

    if standort not in STANDORTE:
        raise ValueError(f'Unbekannter Standort: "{standort}". Gültig: {STANDORTE}')
    if typ not in NETZWERKGERAET_TYPEN:
        raise ValueError(f'Unbekannter Typ: "{typ}". Gültig: {NETZWERKGERAET_TYPEN}')
    if not rackid or not re.match(r'^[A-Z0-9]+$', rackid):
        raise ValueError(f'RACKID darf nur A–Z und 0–9 enthalten und nicht leer sein: "{rackid}"')

    # AP hat keine Funktion
    if typ == 'AP':
        funktion = ''

    prefix = f'{standort}-{typ}-{funktion}'

    # Dynamische RACKID-Längenbegrenzung: 15 − len(Präfix) − 2 (Nummer)
    max_rackid_len = 15 - len(prefix) - 2
    if len(rackid) > max_rackid_len:
        raise ValueError(
            f'RACKID für {typ} darf maximal {max_rackid_len} Zeichen haben '
            f'(eingegeben: {len(rackid)} Zeichen "{rackid}"). '
            f'Präfix "{prefix}" + 2-stellige Nummer belegen bereits {len(prefix) + 2} Zeichen.'
        )

    # Bestehende Namen auf Präfix+Nummer reduzieren (RACKID am Ende abschneiden)
    rackid_len = len(rackid)
    existing_for_num = {
        n[:-rackid_len]
        for n in existing_names
        if n.upper().startswith(prefix.upper()) and len(n) > rackid_len + 2
    }

    nummer    = _naechste_nummer(prefix, existing_for_num)
    candidate = f'{prefix}{nummer}{rackid}'

    ok, err = validate_name(candidate)
    if not ok:
        raise ValueError(err)

    return candidate


def generate_server(
    standort: str,
    zweck: str,
    existing_names: set[str],
) -> str:
    """
    Schema: [STANDORT]-SRV-[ZWECK][NUMMER]
    Länge:  14 Zeichen

    Beispiel: RZ1-SRV-ADDS01  (3+1+3+1+4+2 = 14)

    Args:
        standort:       z. B. 'RZ1'
        zweck:          z. B. 'ADDS', 'SQLP' oder freier Text (max. 4 Zeichen)
        existing_names: bereits belegte Namen

    Returns:
        Generierter Name, z. B. 'RZ1-SRV-ADDS01'
    """
    standort = standort.upper().strip()
    zweck    = zweck.upper().strip()

    if standort not in STANDORTE:
        raise ValueError(f'Unbekannter Standort: "{standort}". Gültig: {STANDORTE}')
    if not zweck or len(zweck) > 4:
        raise ValueError(f'ZWECK muss 1–4 Zeichen haben: "{zweck}"')
    if not re.match(r'^[A-Z0-9]+$', zweck):
        raise ValueError(f'ZWECK darf nur A-Z und 0-9 enthalten: "{zweck}"')

    prefix   = f'{standort}-SRV-{zweck}'
    nummer   = _naechste_nummer(prefix, existing_names)
    candidate = f'{prefix}{nummer}'

    ok, err = validate_name(candidate)
    if not ok:
        raise ValueError(err)
    if len(candidate) != 14:
        raise ValueError(
            f'Generierter Name "{candidate}" hat {len(candidate)} Zeichen (erwartet: 14).'
        )

    return candidate


def generate_pc(
    standort: str,
    kennung_type: str,
    kennung: str,
    existing_names: set[str],
) -> str:
    """
    Schema: [STANDORT]-PC-[KENNUNG]
    Länge:  max. 15 Zeichen

    Bei kennung_type='abteilung': Kennung ist ein Kürzel (max. 4 Zeichen),
    Nummer wird automatisch hochgezählt → z. B. HAU-PC-MARK01
    Bei kennung_type='inventar': Kennung direkt übernommen → z. B. HAU-PC-INV0042

    Args:
        standort:      z. B. 'HAU'
        kennung_type:  'abteilung' oder 'inventar'
        kennung:       Abteilungskürzel oder Inventarnummer
        existing_names: bereits belegte Namen

    Returns:
        Generierter Name
    """
    standort = standort.upper().strip()
    kennung  = kennung.upper().strip()

    if standort not in STANDORTE:
        raise ValueError(f'Unbekannter Standort: "{standort}". Gültig: {STANDORTE}')

    if kennung_type == 'abteilung':
        if not kennung or len(kennung) > 4:
            raise ValueError(f'Abteilungskürzel muss 1–4 Zeichen haben: "{kennung}"')
        if not re.match(r'^[A-Z0-9]+$', kennung):
            raise ValueError(f'Abteilungskürzel darf nur A-Z und 0-9 enthalten: "{kennung}"')
        prefix    = f'{standort}-PC-{kennung}'
        nummer    = _naechste_nummer(prefix, existing_names)
        candidate = f'{prefix}{nummer}'

    elif kennung_type == 'inventar':
        if not kennung:
            raise ValueError('Inventarnummer darf nicht leer sein.')
        if not re.match(r'^[A-Z0-9]+$', kennung):
            raise ValueError(f'Inventarnummer darf nur A-Z und 0-9 enthalten: "{kennung}"')
        candidate = f'{standort}-PC-{kennung}'

    else:
        raise ValueError(f'Unbekannter kennung_type: "{kennung_type}". Gültig: abteilung, inventar')

    ok, err = validate_name(candidate)
    if not ok:
        raise ValueError(err)

    return candidate


def generate_notebook(benutzerkuerzel: str) -> str:
    """
    Schema: NB-[BENUTZERKUERZEL]
    Länge:  max. 15 Zeichen

    Beispiel: NB-SCHMIDTH  (2+1+8 = 11)

    Args:
        benutzerkuerzel: z. B. 'SCHMIDTH' (max. 12 Zeichen)

    Returns:
        Generierter Name, z. B. 'NB-SCHMIDTH'
    """
    kuerzel = benutzerkuerzel.upper().strip()

    if not kuerzel:
        raise ValueError('Benutzerkürzel darf nicht leer sein.')
    if not re.match(r'^[A-Z0-9]+$', kuerzel):
        raise ValueError(f'Benutzerkürzel darf nur A-Z und 0-9 enthalten: "{kuerzel}"')

    candidate = f'NB-{kuerzel}'

    ok, err = validate_name(candidate)
    if not ok:
        raise ValueError(err)

    return candidate


def generate_vm(
    bereich: str,
    funktion: str,
    existing_names: set[str],
) -> str:
    """
    Schema: VM-[BEREICH]-[FUNKTION][NUMMER]
    Länge:  12 Zeichen

    Beispiel: VM-APP-BMS01  (2+1+3+1+3+2 = 12)

    Args:
        bereich:        z. B. 'APP', 'WEB', 'DB'
        funktion:       z. B. 'BMS', 'SQL' oder freier Text (max. 3 Zeichen)
        existing_names: bereits belegte Namen

    Returns:
        Generierter Name, z. B. 'VM-APP-BMS01'
    """
    bereich  = bereich.upper().strip()
    funktion = funktion.upper().strip()

    if bereich not in VM_BEREICHE:
        raise ValueError(f'Unbekannter Bereich: "{bereich}". Gültig: {VM_BEREICHE}')
    if not funktion or len(funktion) > 3:
        raise ValueError(f'VM-Funktion muss 1–3 Zeichen haben: "{funktion}"')
    if not re.match(r'^[A-Z0-9]+$', funktion):
        raise ValueError(f'VM-Funktion darf nur A-Z und 0-9 enthalten: "{funktion}"')

    prefix    = f'VM-{bereich}-{funktion}'
    nummer    = _naechste_nummer(prefix, existing_names)
    candidate = f'{prefix}{nummer}'

    ok, err = validate_name(candidate)
    if not ok:
        raise ValueError(err)
    if len(candidate) != 12:
        raise ValueError(
            f'Generierter Name "{candidate}" hat {len(candidate)} Zeichen (erwartet: 12).'
        )

    return candidate
