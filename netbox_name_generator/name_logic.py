"""
Core logic for name generation according to the IT system naming policy.

Allowed characters: A-Z, 0-9, hyphen (-)
Maximum length: 15 characters
"""

import re

ERLAUBTE_ZEICHEN = re.compile(r'^[A-Z0-9\-]+$')


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def validate_name(name: str, max_laenge: int = 15) -> tuple[bool, str]:
    """
    Checks whether a name complies with the general rules.

    Returns:
        (True, '') if valid
        (False, error message) if invalid
    """
    if not name:
        return False, 'Name must not be empty.'
    if len(name) > max_laenge:
        return False, f'Name "{name}" is {len(name)} characters long (max. {max_laenge}).'
    if not ERLAUBTE_ZEICHEN.match(name):
        return False, (
            f'Name "{name}" contains invalid characters. '
            'Only A-Z, 0-9 and hyphen (-) are allowed.'
        )
    return True, ''


def _naechste_nummer(prefix: str, existing_names: set[str], stellen: int = 2) -> str:
    """
    Finds the smallest available number for the given prefix (case-insensitive).

    Args:
        prefix: Name prefix without number, e.g. 'RZ1-SRV-ADDS'
        existing_names: Set of already assigned names
        stellen: Number of digits (default 2 → 01–99)

    Returns:
        Zero-padded number as string, e.g. '01'

    Raises:
        ValueError: if all numbers are already assigned
    """
    prefix_upper = prefix.upper()
    existing_upper = {n.upper() for n in existing_names}
    max_num = 10 ** stellen

    for n in range(1, max_num):
        nummer = f'{n:0{stellen}d}'
        if f'{prefix_upper}{nummer}' not in existing_upper:
            return nummer

    max_str = f'{max_num - 1:0{stellen}d}'
    raise ValueError(
        f'All numbers 01–{max_str} for prefix "{prefix}" are already assigned.'
    )


# ---------------------------------------------------------------------------
# Name generators
# ---------------------------------------------------------------------------

def generate_netzwerkgeraet(
    standort: str,
    typ: str,
    funktion: str,
    rackid: str,
    existing_names: set[str],
    max_laenge: int = 15,
    nummer_stellen: int = 2,
    strategie: str = 'ohne_rack',
) -> str:
    """
    Schema: [LOCATION]-[TYPE]-[FUNCTION][NUMBER][RACKID]

    Counting strategies:
      'ohne_rack'   (default): number is unique per prefix (ignoring rack suffix)
      'vollstaendig':          full name including rack must be unique per candidate
    """
    standort = standort.upper().strip()
    typ      = typ.upper().strip()
    funktion = funktion.upper().strip()
    rackid   = rackid.upper().strip()

    if not rackid or not re.match(r'^[A-Z0-9]+$', rackid):
        raise ValueError(f'RACKID must only contain A–Z and 0–9 and must not be empty: "{rackid}"')

    prefix = f'{standort}-{typ}-{funktion}'

    # Dynamic RACKID length limit: max_laenge − len(prefix) − nummer_stellen
    max_rackid_len = max_laenge - len(prefix) - nummer_stellen
    if len(rackid) > max_rackid_len:
        raise ValueError(
            f'RACKID for {typ} may be at most {max_rackid_len} characters '
            f'(entered: {len(rackid)} characters "{rackid}"). '
            f'Prefix "{prefix}" + {nummer_stellen}-digit number already occupy {len(prefix) + nummer_stellen} characters.'
        )

    if strategie == 'vollstaendig':
        # Full name (including RACKID) must be unique → same number allowed in different racks
        existing_upper = {n.upper() for n in existing_names}
        max_num = 10 ** nummer_stellen
        nummer = None
        for n in range(1, max_num):
            nr = f'{n:0{nummer_stellen}d}'
            if f'{prefix}{nr}{rackid}'.upper() not in existing_upper:
                nummer = nr
                break
        if nummer is None:
            max_str = f'{max_num - 1:0{nummer_stellen}d}'
            raise ValueError(
                f'All numbers 01–{max_str} for prefix "{prefix}" with RACKID "{rackid}" are already assigned.'
            )
    elif strategie == 'standort_uebergreifend':
        # Strip both standort prefix and rack suffix; number unique per type+function globally
        typ_prefix = f'{typ}-{funktion}'
        rackid_len = len(rackid)
        existing_for_num = set()
        for n in existing_names:
            idx = n.upper().find(typ_prefix.upper())
            if idx >= 0 and len(n) > idx + len(typ_prefix) + rackid_len:
                existing_for_num.add(n[idx:-rackid_len])
        nummer = _naechste_nummer(typ_prefix, existing_for_num, stellen=nummer_stellen)
    else:
        # ohne_rack (default): strip RACKID, number is unique per prefix
        rackid_len = len(rackid)
        existing_for_num = {
            n[:-rackid_len]
            for n in existing_names
            if n.upper().startswith(prefix.upper()) and len(n) > rackid_len + nummer_stellen
        }
        nummer = _naechste_nummer(prefix, existing_for_num, stellen=nummer_stellen)

    candidate = f'{prefix}{nummer}{rackid}'

    ok, err = validate_name(candidate, max_laenge)
    if not ok:
        raise ValueError(err)

    return candidate


def generate_server(
    standort: str,
    zweck: str,
    existing_names: set[str],
    max_laenge: int = 15,
    nummer_stellen: int = 2,
    strategie: str = 'praefix',
) -> str:
    """
    Schema: [LOCATION]-SRV-[PURPOSE][NUMBER]

    Counting strategies:
      'praefix'               (default): number unique per location+purpose
      'standort_uebergreifend':           number globally unique per purpose
    """
    standort = standort.upper().strip()
    zweck    = zweck.upper().strip()

    if not zweck or len(zweck) > 4:
        raise ValueError(f'PURPOSE must be 1–4 characters: "{zweck}"')
    if not re.match(r'^[A-Z0-9]+$', zweck):
        raise ValueError(f'PURPOSE must only contain A-Z and 0-9: "{zweck}"')

    if strategie == 'standort_uebergreifend':
        typ_prefix = f'SRV-{zweck}'
        existing_for_num = {
            n[n.upper().find(typ_prefix.upper()):]
            for n in existing_names
            if typ_prefix.upper() in n.upper()
        }
        nummer = _naechste_nummer(typ_prefix, existing_for_num, stellen=nummer_stellen)
    else:
        nummer = _naechste_nummer(f'{standort}-SRV-{zweck}', existing_names, stellen=nummer_stellen)

    candidate = f'{standort}-SRV-{zweck}{nummer}'

    ok, err = validate_name(candidate, max_laenge)
    if not ok:
        raise ValueError(err)

    return candidate


def generate_pc(
    standort: str,
    kennung_type: str,
    kennung: str,
    existing_names: set[str],
    max_laenge: int = 15,
    nummer_stellen: int = 2,
    strategie: str = 'praefix',
) -> str:
    """
    Schema: [LOCATION]-PC-[IDENTIFIER]

    Counting strategies (only relevant for kennung_type='abteilung'):
      'praefix'               (default): number unique per location+department
      'standort_uebergreifend':           number globally unique per department
    """
    standort = standort.upper().strip()
    kennung  = kennung.upper().strip()

    if kennung_type == 'abteilung':
        if not kennung or len(kennung) > 4:
            raise ValueError(f'Department code must be 1–4 characters: "{kennung}"')
        if not re.match(r'^[A-Z0-9]+$', kennung):
            raise ValueError(f'Department code must only contain A-Z and 0-9: "{kennung}"')
        if strategie == 'standort_uebergreifend':
            typ_prefix = f'PC-{kennung}'
            existing_for_num = {
                n[n.upper().find(typ_prefix.upper()):]
                for n in existing_names
                if typ_prefix.upper() in n.upper()
            }
            nummer = _naechste_nummer(typ_prefix, existing_for_num, stellen=nummer_stellen)
        else:
            nummer = _naechste_nummer(f'{standort}-PC-{kennung}', existing_names, stellen=nummer_stellen)
        candidate = f'{standort}-PC-{kennung}{nummer}'

    elif kennung_type == 'inventar':
        if not kennung:
            raise ValueError('Inventory number must not be empty.')
        if not re.match(r'^[A-Z0-9]+$', kennung):
            raise ValueError(f'Inventory number must only contain A-Z and 0-9: "{kennung}"')
        candidate = f'{standort}-PC-{kennung}'

    else:
        raise ValueError(f'Unknown kennung_type: "{kennung_type}". Valid: abteilung, inventar')

    ok, err = validate_name(candidate, max_laenge)
    if not ok:
        raise ValueError(err)

    return candidate


def generate_notebook(benutzerkuerzel: str, max_laenge: int = 15) -> str:
    """
    Schema: NB-[USERCODE]
    Length: max. 15 characters

    Example: NB-SCHMIDTH  (2+1+8 = 11)

    Args:
        benutzerkuerzel: e.g. 'SCHMIDTH' (max. 12 characters)

    Returns:
        Generated name, e.g. 'NB-SCHMIDTH'
    """
    kuerzel = benutzerkuerzel.upper().strip()

    if not kuerzel:
        raise ValueError('User code must not be empty.')
    if not re.match(r'^[A-Z0-9]+$', kuerzel):
        raise ValueError(f'User code must only contain A-Z and 0-9: "{kuerzel}"')

    candidate = f'NB-{kuerzel}'

    ok, err = validate_name(candidate, max_laenge)
    if not ok:
        raise ValueError(err)

    return candidate


def generate_vm(
    bereich: str,
    funktion: str,
    existing_names: set[str],
    max_laenge: int = 15,
    nummer_stellen: int = 2,
) -> str:
    """
    Schema: VM-[AREA]-[FUNCTION][NUMBER]
    Length: 12 characters

    Example: VM-APP-BMS01  (2+1+3+1+3+2 = 12)

    Args:
        bereich:        e.g. 'APP', 'WEB', 'DB'
        funktion:       e.g. 'BMS', 'SQL' or free text (max. 3 characters)
        existing_names: already assigned names

    Returns:
        Generated name, e.g. 'VM-APP-BMS01'
    """
    bereich  = bereich.upper().strip()
    funktion = funktion.upper().strip()

    if not funktion or len(funktion) > 3:
        raise ValueError(f'VM function must be 1–3 characters: "{funktion}"')
    if not re.match(r'^[A-Z0-9]+$', funktion):
        raise ValueError(f'VM function must only contain A-Z and 0-9: "{funktion}"')

    prefix    = f'VM-{bereich}-{funktion}'
    nummer    = _naechste_nummer(prefix, existing_names, stellen=nummer_stellen)
    candidate = f'{prefix}{nummer}'

    ok, err = validate_name(candidate, max_laenge)
    if not ok:
        raise ValueError(err)

    return candidate
