[English](README.md) | **Deutsch**

# NetBox Name Generator

[NetBox](https://github.com/netbox-community/netbox)-Plugin zur automatisierten Namensvergabe für IT-Systeme.

## Funktionsweise

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

## Voraussetzungen

- NetBox ≥ 4.5
- Python ≥ 3.10

## Installation

Das Plugin liegt nicht auf PyPI. Installiert wird aus dem GitHub-Release-Archiv – das funktioniert ohne `git`,
auch im netbox-docker-Image. `v1.4.5` ggf. durch das gewünschte [Release](https://github.com/carstenviell/netbox-name-generator/releases) ersetzen.

**NetBox aus dem Quellcode (systemd):**

```bash
sudo /opt/netbox/venv/bin/pip install https://github.com/carstenviell/netbox-name-generator/archive/refs/tags/v1.4.5.tar.gz

# bleibt bei NetBox-Upgrades erhalten (upgrade.sh installiert local_requirements.txt neu)
echo "https://github.com/carstenviell/netbox-name-generator/archive/refs/tags/v1.4.5.tar.gz" | sudo tee -a /opt/netbox/local_requirements.txt
```

**netbox-docker:** in `plugin_requirements.txt`

```text
https://github.com/carstenviell/netbox-name-generator/archive/refs/tags/v1.4.5.tar.gz
```

und in `Dockerfile-Plugins` (aus dem `netbox`, `netbox-worker` und `netbox-housekeeping` per `docker-compose.override.yml` gebaut werden):

```dockerfile
FROM netboxcommunity/netbox:v4.7
COPY ./plugin_requirements.txt /opt/netbox/
RUN /usr/local/bin/uv pip install -r /opt/netbox/plugin_requirements.txt
```

Plugin aktivieren in der `configuration.py` (Docker: `configuration/plugins.py`):

```python
PLUGINS = [
    # ...
    'netbox_name_generator',
]
```

Migrationen anwenden und **beide** Dienste neu starten:

```bash
cd /opt/netbox/netbox
sudo /opt/netbox/venv/bin/python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

Docker: `docker compose build --no-cache && docker compose up -d` – die Migrationen laufen beim Start automatisch.

### Upgrade

Neues Release-Archiv installieren (auch in `local_requirements.txt` bzw. `plugin_requirements.txt`
anpassen), danach `migrate` und Neustart (Docker: neu bauen).

## Verwendung

**Plugins → Name Generator** aufrufen, Systemtyp wählen, Felder befüllen → Name wird generiert und die NetBox-Erstellungsseite öffnet sich mit vorausgefülltem Namensfeld.

## Konfiguration der Parameter

Nach der Installation sind Standardwerte bereits hinterlegt. Anpassungen erfolgen unter **Plugins → Name Generator**:

- **Standorte** – Kürzel (z. B. `RZ1`) + optionale Verknüpfung mit einer NetBox-Site
- **NG-Typen** – Netzwerkgerätetypen (z. B. `SW`, `FW`, `AP`)
- **NG-Funktionen** – Zugeordnet zu einem Typ (z. B. `COR` → `SW`)
- **Server-Zwecke** – z. B. `ADDS`, `SQLP`
- **VM-Bereiche** – z. B. `APP`, `WEB`
- **VM-Funktionen** – z. B. `BMS`, `SQL`

Alle Änderungen werden im NetBox-Changelog protokolliert.

## Sprache

Die Oberfläche ist englisch, eine deutsche Übersetzung wird mitgeliefert. Angezeigt wird die Sprache,
die der Benutzer in NetBox gewählt hat (*Profil → Einstellungen → Sprache*); für Sprachen ohne Übersetzung erscheint Englisch.

## Lizenz

[Apache License 2.0](LICENSE)
