# NetBox Name Generator

NetBox-Plugin zur automatisierten Namensvergabe für IT-Systeme.

## Funktionsweise

Das Plugin generiert eindeutige, normkonforme Namen für alle IT-Systemtypen und leitet anschließend direkt zur NetBox-Erstellungsseite weiter – mit vorausgefülltem Namensfeld (und ggf. Site).

**Unterstützte Systemtypen:**

| Typ | Schema | Beispiel |
|-----|--------|---------|
| Netzwerkgeräte (Switch, Firewall, Storage, AP) | `[STANDORT]-[TYP]-[FUNKTION][NR][RACKID]` | `RZ1-SW-COR01NGV` |
| Physische Server | `[STANDORT]-SRV-[ZWECK][NR]` | `RZ1-SRV-ADDS01` |
| Desktop-PCs | `[STANDORT]-PC-[KENNUNG]` | `HAU-PC-MARK01` |
| Notebooks | `NB-[BENUTZERKUERZEL]` | `NB-SCHMIDTH` |
| Virtuelle Maschinen | `VM-[BEREICH]-[FUNKTION][NR]` | `VM-APP-BMS01` |

Alle Parameter (Standorte, Gerätetypen, Funktionen etc.) sind über die NetBox-Oberfläche konfigurierbar (**Plugins → Name Generator → Parameterlisten**). Standorte können optional mit einer NetBox-Site verknüpft werden, damit der Site-Parameter beim Anlegen automatisch vorausgefüllt wird.

## Voraussetzungen

- NetBox ≥ 4.5
- Python ≥ 3.10

## Installation

### 1. Plugin installieren

```bash
# Im NetBox-Verzeichnis (venv aktiviert):
pip install netbox-name-generator
```

Oder direkt aus dem Repository:

```bash
pip install git+https://github.com/carstenviell/netbox-name-generator.git
```

### 2. Plugin in NetBox aktivieren

In `configuration.py`:

```python
PLUGINS = [
    'netbox_name_generator',
]
```

### 3. Migrationen anwenden

```bash
python manage.py migrate
```

```bash
systemctl restart netbox netbox-rq
```

### 4. Verwendung

**Plugins → Name Generator** aufrufen, Systemtyp wählen, Felder befüllen → Name wird generiert und die NetBox-Erstellungsseite öffnet sich mit vorausgefülltem Namensfeld.

## Konfiguration der Parameter

Nach der Installation sind die Standard-Abkürzungen aus der Richtlinie bereits hinterlegt. Anpassungen erfolgen unter **Plugins → Name Generator** über die jeweiligen Parameterlisten:

- **Standorte** – Kürzel (z. B. `RZ1`) + optionale Verknüpfung mit einer NetBox-Site
- **NG-Typen** – Netzwerkgerätetypen (z. B. `SW`, `FW`, `AP`)
- **NG-Funktionen** – Zugeordnet zu einem Typ (z. B. `COR` → `SW`)
- **Server-Zwecke** – z. B. `ADDS`, `SQLP`
- **VM-Bereiche** – z. B. `APP`, `WEB`
- **VM-Funktionen** – z. B. `BMS`, `SQL`

Alle Änderungen werden im NetBox-Changelog protokolliert.
