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

def validate_name(name: str) -> tuple[bool, str]:
    """
    Checks whether a name complies with the general rules.

    Returns:
        (True, '') if valid
        (False, error message) if invalid
    """
    if not name:
        return False, 'Name must not be empty.'
    if len(name) > 15:
        return False, f'Name "{name}" is {len(name)} characters long (max. 15).'
    if not ERLAUBTE_ZEICHEN.match(name):
        return False, (
            f'Name "{name}" contains invalid characters. '
            'Only A-Z, 0-9 and hyphen (-) are allowed.'
        )
    return True, ''


def _naechste_nummer(prefix: str, existing_names: set[str]) -> str:
    """
    Finds the smallest available two-digit number (01–99) for the given
    prefix (case-insensitive).

    Args:
        prefix: Name prefix without number, e.g. 'RZ1-SRV-ADDS'
        existing_names: Set of already assigned names

    Returns:
        Two-digit number as string, e.g. '01'

    Raises:
        ValueError: if all numbers 01–99 are already assigned
    """
    prefix_upper = prefix.upper()
    existing_upper = {n.upper() for n in existing_names}

    for n in range(1, 100):
        nummer = f'{n:02d}'
        if f'{prefix_upper}{nummer}' not in existing_upper:
            return nummer

    raise ValueError(
        f'All numbers 01–99 for prefix "{prefix}" are already assigned.'
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
) -> str:
    """
    Schema: [LOCATION]-[TYPE]-[FUNCTION][NUMBER][RACKID]
    Length: exactly 15 characters

    The allowed RACKID length is derived from: 15 − len(prefix) − 2 (number)
      SW/FW  → max. 3 characters  (e.g. NGV)
      STO    → max. 2 characters  (e.g. R1)
      AP     → max. 6 characters  (no function, more space)

    Example: RZ1-SW-COR01NGV  (3+1+2+1+3+2+3 = 15)

    Args:
        standort:       e.g. 'RZ1'
        typ:            e.g. 'SW', 'FW', 'STO', 'AP'
        funktion:       e.g. 'COR', 'EXT', 'SAN'  (empty for types without function)
        rackid:         Rack identifier, length depends on type (see above)
        existing_names: already assigned names

    Returns:
        Generated name, e.g. 'RZ1-SW-COR01NGV'
    """
    standort = standort.upper().strip()
    typ      = typ.upper().strip()
    funktion = funktion.upper().strip()
    rackid   = rackid.upper().strip()

    if not rackid or not re.match(r'^[A-Z0-9]+$', rackid):
        raise ValueError(f'RACKID must only contain A–Z and 0–9 and must not be empty: "{rackid}"')

    prefix = f'{standort}-{typ}-{funktion}'

    # Dynamic RACKID length limit: 15 − len(prefix) − 2 (number)
    max_rackid_len = 15 - len(prefix) - 2
    if len(rackid) > max_rackid_len:
        raise ValueError(
            f'RACKID for {typ} may be at most {max_rackid_len} characters '
            f'(entered: {len(rackid)} characters "{rackid}"). '
            f'Prefix "{prefix}" + 2-digit number already occupy {len(prefix) + 2} characters.'
        )

    # Reduce existing names to prefix+number (strip RACKID from end)
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
    Schema: [LOCATION]-SRV-[PURPOSE][NUMBER]
    Length: 14 characters

    Example: RZ1-SRV-ADDS01  (3+1+3+1+4+2 = 14)

    Args:
        standort:       e.g. 'RZ1'
        zweck:          e.g. 'ADDS', 'SQLP' or free text (max. 4 characters)
        existing_names: already assigned names

    Returns:
        Generated name, e.g. 'RZ1-SRV-ADDS01'
    """
    standort = standort.upper().strip()
    zweck    = zweck.upper().strip()

    if not zweck or len(zweck) > 4:
        raise ValueError(f'PURPOSE must be 1–4 characters: "{zweck}"')
    if not re.match(r'^[A-Z0-9]+$', zweck):
        raise ValueError(f'PURPOSE must only contain A-Z and 0-9: "{zweck}"')

    prefix   = f'{standort}-SRV-{zweck}'
    nummer   = _naechste_nummer(prefix, existing_names)
    candidate = f'{prefix}{nummer}'

    ok, err = validate_name(candidate)
    if not ok:
        raise ValueError(err)
    if len(candidate) != 14:
        raise ValueError(
            f'Generated name "{candidate}" has {len(candidate)} characters (expected: 14).'
        )

    return candidate


def generate_pc(
    standort: str,
    kennung_type: str,
    kennung: str,
    existing_names: set[str],
) -> str:
    """
    Schema: [LOCATION]-PC-[IDENTIFIER]
    Length: max. 15 characters

    With kennung_type='abteilung': identifier is a department code (max. 4 characters),
    number is assigned automatically → e.g. HAU-PC-MARK01
    With kennung_type='inventar': identifier used directly → e.g. HAU-PC-INV0042

    Args:
        standort:      e.g. 'HAU'
        kennung_type:  'abteilung' or 'inventar'
        kennung:       department code or inventory number
        existing_names: already assigned names

    Returns:
        Generated name
    """
    standort = standort.upper().strip()
    kennung  = kennung.upper().strip()

    if kennung_type == 'abteilung':
        if not kennung or len(kennung) > 4:
            raise ValueError(f'Department code must be 1–4 characters: "{kennung}"')
        if not re.match(r'^[A-Z0-9]+$', kennung):
            raise ValueError(f'Department code must only contain A-Z and 0-9: "{kennung}"')
        prefix    = f'{standort}-PC-{kennung}'
        nummer    = _naechste_nummer(prefix, existing_names)
        candidate = f'{prefix}{nummer}'

    elif kennung_type == 'inventar':
        if not kennung:
            raise ValueError('Inventory number must not be empty.')
        if not re.match(r'^[A-Z0-9]+$', kennung):
            raise ValueError(f'Inventory number must only contain A-Z and 0-9: "{kennung}"')
        candidate = f'{standort}-PC-{kennung}'

    else:
        raise ValueError(f'Unknown kennung_type: "{kennung_type}". Valid: abteilung, inventar')

    ok, err = validate_name(candidate)
    if not ok:
        raise ValueError(err)

    return candidate


def generate_notebook(benutzerkuerzel: str) -> str:
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
    nummer    = _naechste_nummer(prefix, existing_names)
    candidate = f'{prefix}{nummer}'

    ok, err = validate_name(candidate)
    if not ok:
        raise ValueError(err)
    if len(candidate) != 12:
        raise ValueError(
            f'Generated name "{candidate}" has {len(candidate)} characters (expected: 12).'
        )

    return candidate
