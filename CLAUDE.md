# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Zweck dieses Repositories

NetBox-Plugin **"Name Generator"** zur automatisierten, regelkonformen Namensvergabe für alle IT-Systeme.

## Namenskonventionen

### Allgemeine Regeln
- Maximale Länge: **konfigurierbar** (Default 15, Range 10–63) via `NamierungsKonfiguration`
- Erlaubte Zeichen: Großbuchstaben (A-Z), Ziffern (0-9), Bindestriche (-)
- Systemweit eindeutig (Device + VirtualMachine werden gemeinsam geprüft)

### Schemata nach Systemtyp

| Typ | Schema | Beispiel |
|-----|--------|---------|
| Netzwerkgeräte (Switch, FW, Storage) | `[STANDORT]-[TYP]-[FUNKTION][NUMMER][RACKID]` | `RZ1-SW-COR01NGV` |
| Physische Server | `[STANDORT]-SRV-[ZWECK][NUMMER]` | `RZ1-SRV-ADDS01` |
| Desktop-PCs | `[STANDORT]-PC-[KENNUNG]` | `HAU-PC-MARK01` |
| Notebooks | `NB-[BENUTZERKUERZEL]` | `NB-SCHMIDTH` |
| Virtuelle Maschinen | `VM-[BEREICH]-[FUNKTION][NUMMER]` | `VM-APP-BMS01` |

### Konfigurierbare Parameter (Plugin → Settings → `NamierungsKonfiguration`)

Singleton-Modell (Migrationen 0003–0006):
- `max_laenge` – maximale Namenslänge (Default 15)
- `nummer_stellen` – Stellen des Zählers (Default 2 → 01–99)
- `strategie_netzwerkgeraet` – `ohne_rack` (Default) / `vollstaendig` / `standort_uebergreifend`
- `strategie_server` / `strategie_pc` – `praefix` (Default) / `standort_uebergreifend`

Alle `generate_*`-Funktionen in `name_logic.py` akzeptieren diese als optionale Parameter.

---

## Plugin-Entwicklung

### Docker-Workflow

Das Plugin läuft in `~/dev/netbox/netbox-docker/`. Es wird via `pip install` in das Docker-Image eingebaut (`Dockerfile-plugin`). Die lokale Instanz ist unter **https://localhost:8000** erreichbar (nginx mit selbstsigniertem Zertifikat).

```bash
# Nach Code-Änderungen: Image neu bauen und starten
cd ~/dev/netbox/netbox-docker
docker compose build netbox && docker compose up -d

# NetBox-Shell
docker compose exec netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py shell -c "
from netbox_name_generator.models import Standort
print(list(Standort.objects.all()))
"

# Migrationen anwenden
docker compose exec netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py migrate
```

### Neue Migrationen generieren

NetBox 4.5 blockiert `makemigrations` ohne `DEVELOPER = True`. Workaround via temporärem Container:

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
  bash -c "/opt/netbox/venv/bin/python manage.py makemigrations netbox_name_generator && \
           cp /opt/netbox/venv/lib/python3.12/site-packages/netbox_name_generator/migrations/0001_initial.py /migrations-output/"
rm -rf /tmp/netbox-config-dev
# Danach: Abhängigkeiten in 0001_initial.py prüfen – auf ('dcim', '0001_initial') und ('extras', '0001_initial') setzen
```

---

## Architektur des Plugins

### Datenpfad: DB → Form → Name → Redirect

1. **`models.py`** – 6 `NetBoxModel`-Klassen: `Standort`, `NetzwerkgeraetTyp`, `NetzwerkgeraetFunktion`, `ServerZweck`, `VmBereich`, `VmFunktion`. `Standort` hat optionales FK zu `dcim.Site` → wird als `?site=<pk>` an die Redirect-URL angehängt.

2. **`forms.py`** – `NameGeneratorForm` lädt alle Choices in `__init__` aus der DB. Baut folgende JSON-Strings für JS:
   - `ng_funktionen_json`: `{typ: [{v: kuerzel, l: "kuerzel – beschreibung"}, ...]}` – für Funktions-Dropdown-Filterung
   - `ng_typ_hat_funktion_json`: `{typ: bool}` – steuert ob Funktionsfeld angezeigt wird
   - `ng_standort_site_json`: `{standort_kuerzel: site_id}` – Mapping für Rack-Lookup
   - `ng_racks_json`: `{site_id: [{v: rack_name, l: "rack_name (location)"}]}` – Racks pro Site
   - `clean()` ruft die passende `generate_*`-Funktion auf, speichert `target_url` inkl. `?site=&rack=&location=`

3. **`name_logic.py`** – Reine Python-Funktionen, **kein Django-Import**. Fünf `generate_*`-Funktionen. `_naechste_nummer()` sucht kleinste freie zweistellige Nummer. Uniqueness-Check kombiniert Device + VirtualMachine.

4. **`views.py`** – `NameGeneratorView` (Haupt-GET/POST) + je 4 generische NetBox-Views pro Modell: `ObjectListView`, `ObjectEditView`, `ObjectDeleteView`, `ObjectChangeLogView`.

5. **`api/`** – Minimale REST-API-Schicht (serializers, views, urls) für alle 6 Modelle. **Pflicht:** `NetBoxModel` benötigt registrierte API-Serializer für die Changelog-Serialisierung beim Löschen, sonst `SerializerNotFound`.

6. **`template_content.py`** – `PluginTemplateExtension` mit `list_buttons()` fügt "Generate Name & Add"-Button auf `/dcim/devices/` und `/virtualization/virtual-machines/` ein. Wird automatisch über den NetBox-Default-Pfad geladen (kein explizites Setzen in `PluginConfig` nötig).

7. **`templates/name_generator.html`** – Alle 5 Sektionen initial `display:none`, JS blendet per `showSection()` ein. Live-Vorschau des Namens. Rack-Feld wechselt dynamisch zwischen Dropdown (wenn Racks vorhanden) und Textfeld.

### Kritische Implementierungsdetails

- **JSON-Attribute mit `|safe` rendern:** `{{ form.ng_funktionen_json|safe }}` – ohne `|safe` escaped Django `"` zu `&quot;` im `<script>`-Block → JS-Fehler
- **Tom-Select:** NetBox wendet Tom-Select auf alle `<select>` an. Das `ng_funktion`-Feld hat `class="no-ts"` um clientseitiges DOM-Filtering zu ermöglichen
- **Migration-Abhängigkeiten:** Immer `('dcim', '0001_initial')` und `('extras', '0001_initial')` verwenden – versionsspezifische Migrations-Namen (z.B. `0226_modulebay`) brechen auf anderen Patch-Versionen
- **`*.mo`-Dateien** nicht ins Repo committen (in `.gitignore`). Leere `.mo`-Dateien verursachen `struct.error` beim Start. Das `Dockerfile-plugin` kompiliert sie via `msgfmt` beim Build
- **`get_absolute_url()`** zeigt auf Edit-View (kein separater Detail-View)
- **RACKID-Länge** ist dynamisch: `max_rackid = 15 − len(prefix) − 2`
- **`ActionsColumn`** in `NetBoxTable` sucht automatisch `{model}_changelog`-URLs → `ObjectChangeLogView` + URL-Pattern für alle 6 Modelle erforderlich

### URL-Schema

```
/plugins/name-generator/                          → Generator
/plugins/name-generator/standorte/               → Liste
/plugins/name-generator/standorte/add/           → Anlegen
/plugins/name-generator/standorte/<pk>/edit/     → Bearbeiten
/plugins/name-generator/standorte/<pk>/delete/   → Löschen
/plugins/name-generator/standorte/<pk>/changelog/ → Changelog
```
Analog für: `ng-typen`, `ng-funktionen`, `server-zwecke`, `vm-bereiche`, `vm-funktionen`

### i18n

- Englische Strings als `msgid`, deutsche Übersetzungen in `locale/de/LC_MESSAGES/django.po`
- Template: `{% load i18n %}` + `{% trans "..." %}` / `{% blocktrans %}...{% endblocktrans %}`
- `django.po` pflegen, `django.mo` wird beim Docker-Build via `msgfmt` kompiliert
- "Site" statt "Location" verwenden – Django's eigene deutsche Übersetzung überschreibt sonst "Location" → "Lokation"
