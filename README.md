**English** | [Deutsch](README.de.md)

# NetBox Name Generator

[NetBox](https://github.com/netbox-community/netbox) plugin for automated IT system name generation.

## How It Works

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

## Requirements

- NetBox ≥ 4.5
- Python ≥ 3.10

## Installation

The plugin is not published on PyPI. Install it from the GitHub release archive – this works without `git`,
also in the netbox-docker image. Replace `v1.4.5` with the [release](https://github.com/carstenviell/netbox-name-generator/releases) you want.

**NetBox installed from source (systemd):**

```bash
sudo /opt/netbox/venv/bin/pip install https://github.com/carstenviell/netbox-name-generator/archive/refs/tags/v1.4.5.tar.gz

# keep the plugin when NetBox is upgraded (upgrade.sh reinstalls local_requirements.txt)
echo "https://github.com/carstenviell/netbox-name-generator/archive/refs/tags/v1.4.5.tar.gz" | sudo tee -a /opt/netbox/local_requirements.txt
```

**netbox-docker:** add to `plugin_requirements.txt`

```text
https://github.com/carstenviell/netbox-name-generator/archive/refs/tags/v1.4.5.tar.gz
```

and to `Dockerfile-Plugins` (build `netbox`, `netbox-worker` and `netbox-housekeeping` from it via `docker-compose.override.yml`):

```dockerfile
FROM netboxcommunity/netbox:v4.7
COPY ./plugin_requirements.txt /opt/netbox/
RUN /usr/local/bin/uv pip install -r /opt/netbox/plugin_requirements.txt
```

Enable the plugin in `configuration.py` (Docker: `configuration/plugins.py`):

```python
PLUGINS = [
    # ...
    'netbox_name_generator',
]
```

Apply the migrations and restart **both** services:

```bash
cd /opt/netbox/netbox
sudo /opt/netbox/venv/bin/python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

Docker: `docker compose build --no-cache && docker compose up -d` – migrations run automatically at start.

### Upgrade

Install the new release archive (also update `local_requirements.txt` / `plugin_requirements.txt`),
then `migrate` and restart (Docker: rebuild).

## Usage

Navigate to **Plugins → Name Generator**, select a system type, fill in the fields → the name is generated and the NetBox creation page opens with the name pre-filled.

## Configuring Parameters

Default values are pre-loaded after installation. Adjustments can be made under **Plugins → Name Generator**:

- **Sites** – Abbreviation (e.g. `RZ1`) + optional link to a NetBox Site
- **ND Types** – Network device types (e.g. `SW`, `FW`, `AP`)
- **ND Functions** – Assigned to a type (e.g. `COR` → `SW`)
- **Server Purposes** – e.g. `ADDS`, `SQLP`
- **VM Areas** – e.g. `APP`, `WEB`
- **VM Functions** – e.g. `BMS`, `SQL`

All changes are logged in the NetBox changelog.

## Language

The user interface is English and ships with a German translation. It follows the language the user
selected in NetBox (*Profile → Preferences → Language*); languages without a translation fall back to English.

## License

[Apache License 2.0](LICENSE)
