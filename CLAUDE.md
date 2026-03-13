# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Zweck dieses Repositories

Dieses Repository enthält die Richtlinie zur Bezeichnung von IT-Systemen (`Richtlinie zur Bezeichnung von IT-Systemen.pdf`). Die Konventionen bilden die Grundlage für das NetBox-Plugin **"Name Generator"**, das die automatisierte, regelkonforme Namensvergabe für alle IT-Systeme übernimmt.

## Namenskonventionen im Überblick

### Allgemeine Regeln (gelten für alle Systemtypen)
- Maximale Länge: **15 Zeichen**
- Erlaubte Zeichen: Großbuchstaben (A-Z), Ziffern (0-9), Bindestriche (-)
- Systemweit eindeutig, ausschließlich Großbuchstaben
- Komponenten werden durch Bindestriche getrennt

### Schemata nach Systemtyp

| Typ | Schema | Länge | Beispiel |
|-----|--------|-------|---------|
| Netzwerkgeräte (Switch, FW, Storage) | `[STANDORT]-[TYP]-[FUNKTION][NUMMER][RACKID]` | genau 15 | `RZ1-SW-COR01NGV` |
| Physische Server | `[STANDORT]-[SRV]-[ZWECK][NUMMER]` | 14 | `RZ1-SRV-ADDS01` |
| Desktop-PCs | `[STANDORT]-[PC]-[KENNUNG]` | max. 15 | `HAU-PC-MARK01` |
| Notebooks | `[NB]-[BENUTZERKUERZEL]` | max. 15 | `NB-SCHMIDTH` |
| Virtuelle Maschinen | `[VM]-[BEREICH]-[FUNKTION][NUMMER]` | 12 | `VM-APP-BMS01` |

### Wichtige Abkürzungen

**STANDORT:** `RZ1` (Rechenzentrum 1), `HAU` (Hauptgebäude), `NEB` (Nebengebäude), `B01` (Gebäude 01)

**Netzwerkgeräte – TYP:** `SW` (Switch), `FW` (Firewall), `STO` (Storage), `AP` (WLAN-Accesspoint)

**Netzwerkgeräte – FUNKTION:**
- SW: `COR` (Core), `DIS` (Distribution), `ACC` (Access), `EDG` (Edge)
- FW: `EXT` (External/Perimeter), `INT` (Internal)
- STO: `SAN` (Storage Area Network), `NAS` (Network Attached Storage)

**Server – ZWECK:** `ADDS`, `SQLP`, `FILE`, `MONI`, `SAP`, `EXCH`, `HYPV`

**VM – BEREICH:** `APP`, `WEB`, `DB`, `ADM`, `RDS`, `DEV`, `TEST`, `PROD`

**VM – FUNKTION:** `BMS`, `RDH`, `NOC`, `SQL`, `CRM`, `ERP`, `AD`, `FIL`

## Namensvergabe-Prozess

Neue Namen werden **ausschließlich** über das NetBox-Plugin "Name Generator" vergeben:
1. NetBox aufrufen → **Plugins** → **Name Generator**
2. Systemtyp auswählen und Felder befüllen
3. Das Plugin generiert den Namen, prüft Länge und Eindeutigkeit
4. Weiterleitung zur NetBox-Erstellungsseite mit vorausgefülltem Namensfeld

## NetBox als CMDB

NetBox ist die "Single Source of Truth" für alle IT-Assets. Informationen, die nicht im Namen abgebildet werden können (Raumnummer, Benutzer, IP-Adressen, Hardware-Spezifikationen, Wartungsverträge, Software), werden dort gepflegt.

---

## Plugin-Entwicklung

### Docker-Workflow (Entwicklungsumgebung)

Das Plugin läuft in `~/dev/netbox/netbox-docker/`. Es wird via `pip install -e` in das Docker-Image eingebaut (Dockerfile dort konfiguriert).

```bash
# Image neu bauen (nach Code-Änderungen)
cd ~/dev/netbox/netbox-docker
docker compose build netbox

# Container neu starten
docker compose up -d

# Plugin-Seite: http://localhost:8000/plugins/name-generator/
```

```bash
# NetBox-Shell (für DB-Abfragen, Tests)
docker compose exec netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py shell -c "
from netbox_name_generator.models import Standort
print(list(Standort.objects.all()))
"

# Migrationen anwenden (nach neuen Migrations-Dateien)
docker compose exec netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py migrate
```

### Neue Migrationen generieren

NetBox 4.5 blockiert `makemigrations` ohne `DEVELOPER = True`:

```bash
cp -r ~/dev/netbox/netbox-docker/configuration /tmp/netbox-config-dev
echo "DEVELOPER = True" >> /tmp/netbox-config-dev/configuration.py
docker run --rm \
  --network netbox-docker_default \
  --env-file ~/dev/netbox/netbox-docker/env/netbox.env \
  -v /tmp/netbox-config-dev:/etc/netbox/config:ro \
  -v ~/dev/netbox/NamingProcess/netbox_name_generator/migrations:/migrations-output \
  --workdir /opt/netbox/netbox --entrypoint "" \
  docker.io/netboxcommunity/netbox:v4.5-4.0.1 \
  bash -c "python manage.py makemigrations netbox_name_generator && cp .../0001_initial.py /migrations-output/"
rm -rf /tmp/netbox-config-dev
# Danach: generierte Migration prüfen (Rück-Referenz auf 0002 entfernen falls vorhanden)
```

## Architektur des Plugins

### Datenpfad: DB → Form → Name → Redirect

1. **`models.py`** – 6 `NetBoxModel`-Klassen verwalten die Konfigurationsparameter (Standorte, NG-Typen, NG-Funktionen, Server-Zwecke, VM-Bereiche, VM-Funktionen). `Standort` hat ein optionales FK zu `dcim.Site` – wenn gesetzt, wird `?site=<pk>` an die Redirect-URL angehängt.

2. **`forms.py`** – `NameGeneratorForm` lädt alle Choices in `__init__` aus der DB. Baut `ng_funktionen_json` und `ng_typ_hat_funktion_json` als JSON-Strings für clientseitiges JS-Filtering. `clean()` ruft die entsprechende `generate_*`-Funktion auf und speichert die Ziel-URL in `self.target_url`.

3. **`name_logic.py`** – Reine Python-Funktionen, kein Django-Import. Fünf `generate_*`-Funktionen, je eine pro Systemtyp. `_naechste_nummer()` sucht die kleinste freie zweistellige Nummer im Bestand. Uniqueness-Check kombiniert Device + VirtualMachine aus NetBox.

4. **`views.py`** – `NameGeneratorView` (Haupt-GET/POST). Zusätzlich je 4 generische NetBox-Views pro Modell: `ObjectListView`, `ObjectEditView`, `ObjectDeleteView`, `ObjectChangeLogView` (letztere ist pflicht, da `ActionsColumn` in `NetBoxTable` automatisch `{model}_changelog`-URLs sucht).

5. **`templates/name_generator.html`** – Alle 5 Sektionen sind initial `display:none`, JS blendet die passende per `showSection()` ein. **Wichtig:** JSON-Attribute des Forms müssen mit `|safe` gerendert werden (`{{ form.ng_funktionen_json|safe }}`), sonst escaped Django die Anführungszeichen und das JS schlägt fehl.

### NetBox-spezifische Besonderheiten

- `get_absolute_url()` zeigt auf den Edit-View (kein separater Detail-View implementiert)
- `NetzwerkgeraetTyp.hat_funktion` (BooleanField) steuert ob das Funktions-Dropdown angezeigt wird (AP = False)
- RACKID-Länge ist dynamisch: `max_rackid = 15 − len(prefix) − 2`, abhängig vom Typ
- `ButtonColorChoices` in NetBox 4.5 kommt aus `netbox.plugins.navigation`, nicht `utilities.choices`
- NetBox wendet Tom-Select auf **alle** `<select>`-Elemente an (außer `.no-ts`, `.api-select`, `.color-select`)

### URL-Schema

`/plugins/name-generator/` → Index
`/plugins/name-generator/standorte/` → Liste (analog für ng-typen, ng-funktionen, server-zwecke, vm-bereiche, vm-funktionen)
`/plugins/name-generator/standorte/add/` → Anlegen
`/plugins/name-generator/standorte/<pk>/edit/` → Bearbeiten
`/plugins/name-generator/standorte/<pk>/delete/` → Löschen
`/plugins/name-generator/standorte/<pk>/changelog/` → Changelog
