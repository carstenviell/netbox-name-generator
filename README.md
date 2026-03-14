# NetBox Name Generator

[🇩🇪 Deutsch](#deutsch) | [🇬🇧 English](#english)

---

## Deutsch

NetBox-Plugin zur automatisierten Namensvergabe für IT-Systeme.

### Funktionsweise

Das Plugin generiert eindeutige, normkonforme Namen für alle IT-Systemtypen und leitet anschließend direkt zur NetBox-Erstellungsseite weiter – mit vorausgefülltem Namensfeld (und ggf. Standort).

**Unterstützte Systemtypen:**

| Typ | Schema | Beispiel |
|-----|--------|---------|
| Netzwerkgeräte (Switch, Firewall, Storage, AP) | `[STANDORT]-[TYP]-[FUNKTION][NR][RACKID]` | `RZ1-SW-COR01NGV` |
| Physische Server | `[STANDORT]-SRV-[ZWECK][NR]` | `RZ1-SRV-ADDS01` |
| Desktop-PCs | `[STANDORT]-PC-[KENNUNG]` | `HAU-PC-MARK01` |
| Notebooks | `NB-[BENUTZERKUERZEL]` | `NB-SCHMIDTH` |
| Virtuelle Maschinen | `VM-[BEREICH]-[FUNKTION][NR]` | `VM-APP-BMS01` |

Alle Parameter (Standorte, Gerätetypen, Funktionen etc.) sind über die NetBox-Oberfläche konfigurierbar (**Plugins → Name Generator**). Standorte können optional mit einer NetBox-Site verknüpft werden, damit der Site-Parameter beim Anlegen automatisch vorausgefüllt wird.

Die Oberfläche passt sich der in NetBox gewählten Sprache an (Deutsch / Englisch).

### Voraussetzungen

- NetBox ≥ 4.5
- Python ≥ 3.10

### Installation

**1. Plugin installieren**

```bash
pip install git+https://github.com/carstenviell/netbox-name-generator.git
```

**2. Plugin in NetBox aktivieren** (`configuration.py`):

```python
PLUGINS = [
    'netbox_name_generator',
]
```

**3. Migrationen anwenden**

```bash
python manage.py migrate
systemctl restart netbox netbox-rq
```

**4. Verwendung**

**Plugins → Name Generator** aufrufen, Systemtyp wählen, Felder befüllen → Name wird generiert und die NetBox-Erstellungsseite öffnet sich mit vorausgefülltem Namensfeld.

### Konfiguration der Parameter

Nach der Installation sind Standardwerte bereits hinterlegt. Anpassungen erfolgen unter **Plugins → Name Generator**:

- **Standorte** – Kürzel (z. B. `RZ1`) + optionale Verknüpfung mit einer NetBox-Site
- **NG-Typen** – Netzwerkgerätetypen (z. B. `SW`, `FW`, `AP`)
- **NG-Funktionen** – Zugeordnet zu einem Typ (z. B. `COR` → `SW`)
- **Server-Zwecke** – z. B. `ADDS`, `SQLP`
- **VM-Bereiche** – z. B. `APP`, `WEB`
- **VM-Funktionen** – z. B. `BMS`, `SQL`

Alle Änderungen werden im NetBox-Changelog protokolliert.

---

## English

NetBox plugin for automated IT system name generation.

### How It Works

The plugin generates unique, policy-compliant names for all IT system types and redirects directly to the NetBox creation page – with the name field (and optionally the site) pre-filled.

**Supported system types:**

| Type | Schema | Example |
|------|--------|---------|
| Network Devices (Switch, Firewall, Storage, AP) | `[SITE]-[TYPE]-[FUNCTION][NO][RACKID]` | `RZ1-SW-COR01NGV` |
| Physical Servers | `[SITE]-SRV-[PURPOSE][NO]` | `RZ1-SRV-ADDS01` |
| Desktop PCs | `[SITE]-PC-[IDENTIFIER]` | `HAU-PC-MARK01` |
| Notebooks | `NB-[USERCODE]` | `NB-SCHMIDTH` |
| Virtual Machines | `VM-[AREA]-[FUNCTION][NO]` | `VM-APP-BMS01` |

All parameters (sites, device types, functions, etc.) are configurable via the NetBox UI (**Plugins → Name Generator**). Sites can optionally be linked to a NetBox Site so the site field is pre-filled when creating a device.

The UI adapts to the language selected in NetBox (German / English).

### Requirements

- NetBox ≥ 4.5
- Python ≥ 3.10

### Installation

**1. Install the plugin**

```bash
pip install git+https://github.com/carstenviell/netbox-name-generator.git
```

**2. Activate the plugin** (`configuration.py`):

```python
PLUGINS = [
    'netbox_name_generator',
]
```

**3. Apply migrations**

```bash
python manage.py migrate
systemctl restart netbox netbox-rq
```

**4. Usage**

Navigate to **Plugins → Name Generator**, select a system type, fill in the fields → the name is generated and the NetBox creation page opens with the name pre-filled.

### Configuring Parameters

Default values are pre-loaded after installation. Adjustments can be made under **Plugins → Name Generator**:

- **Sites** – Abbreviation (e.g. `RZ1`) + optional link to a NetBox Site
- **ND Types** – Network device types (e.g. `SW`, `FW`, `AP`)
- **ND Functions** – Assigned to a type (e.g. `COR` → `SW`)
- **Server Purposes** – e.g. `ADDS`, `SQLP`
- **VM Areas** – e.g. `APP`, `WEB`
- **VM Functions** – e.g. `BMS`, `SQL`

All changes are logged in the NetBox changelog.
