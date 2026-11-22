**English** | [Deutsch](CHANGELOG.de.md)

# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed
- Documentation in two languages in separate files: `README.md` (English) / `README.de.md` (German), `CHANGELOG.md` / `CHANGELOG.de.md`; added `LICENSE` (Apache-2.0, as declared in `pyproject.toml`).

## [1.4.5] - 2026-11-22

### Fixed
- Installation guide: installation from the GitHub release archive instead of `git+https://…` (the netbox-docker image has no `git`); variants for source installation (incl. `local_requirements.txt`) and netbox-docker, restart of web and worker, upgrade.
- The German translation is now shipped compiled (`django.mo`) – before only the `.po`; without `gettext` on the target system the UI stayed English. Added a test against outdated/guessed translations.
- Added 19 missing translations (e.g. settings/counting strategies) and corrected two wrongly guessed ones ("Rack", "Network Device Counting Strategy").
- Replaced hard-coded German placeholders ("z. B. …") in the form and JavaScript with translatable English texts – the source language is English throughout.

## [1.4.4] - 2026-08-10

### Fixed
- After selecting the system type, the form no longer showed any further fields: the explanatory comment added above the `json_script` tags with the XSS fix (v1.4.1) used the multi-line `{# ... #}` syntax, which Django only supports on a single line. The comment was therefore rendered literally into the page; the `</` sequence in it made the browser swallow the directly following `<script id="ng-funktionen-data">` tag as an invalid comment, so `document.getElementById(...)` returned `null` and the whole form JavaScript (incl. drop-down switching) aborted with a `TypeError` before it was initialised. Changed the comment to `{% comment %}...{% endcomment %}`

## [1.4.3] - 2026-08-02

### Security
- Mitigated a race condition in name assignment: the plugin never creates an object itself but redirects with a prefilled `?name=...` to the NetBox creation page, which the user fills in separately (possibly minutes later) — two simultaneous generations could so far get the same name suggestion. A new model `ReservedName` (unique constraint, 10-minute TTL) reserves generated names atomically: the normal case is prevented proactively (reservations are included in the collision check), a real simultaneous collision is caught by the DB constraint and reported to the user with a request to try again. Applies to all auto-numbered types (network device/server/PC/VM); notebook names are deterministic and therefore not affected. Verified live against the container (normal case, forced collision, TTL expiry)

## [1.4.2] - 2026-08-01

### Security
- **Git history cleaned**: the private SSH key documented in CRITICAL-01 (`SECURITY-ANALYSE-2026-08-01.md`) (`ssh_carstenviell`/`ssh_carstenviell.pub`, accidentally committed on 2026-03-14) was removed from **every** commit of the history with `git filter-repo`, and the cleaned history was force-pushed to `main` and all affected release tags (`v1.3.0`–`v1.4.1`). Commit hashes from the affected commit on have changed as a result (`v1.1.0`–`v1.2.1` unchanged, as they predate the key).
- **Important for existing clones/forks**: a `git pull` on an old clone leads to a diverging history. Recommendation: clone the repository again (`git clone`), back up local changes first. GitHub's own caches/forks/PR references to the old commits are not covered by this cleanup — if relevant, contact GitHub Support.
- Regardless of this cleanup, the exposed key is still considered compromised and should be rotated/revoked immediately if not done yet.

## [1.4.1] - 2026-08-01

### Security
- Fixed stored XSS: the JSON configuration for the name generator was rendered via `json.dumps()` + `|safe` into a `<script>` block, so a `beschreibung` field (e.g. of `NetzwerkgeraetFunktion`) containing a `</script>` sequence could break out of the script block (session compromise of every user opening the start page, triggered by a user with much lower privileges). The template now uses Django's `|json_script` filter, which escapes HTML-safely
- Defense in depth: the `beschreibung` fields of all six configuration models (`Standort`, `NetzwerkgeraetTyp`, `NetzwerkgeraetFunktion`, `ServerZweck`, `VmBereich`, `VmFunktion`) no longer allow the characters `<`/`>`
- `NameGeneratorView` so far only checked login, no permission, and therefore delivered the complete rack/site topology and (indirectly) the device/VM name inventory to every logged-in user. It now requires `dcim.add_device` and `virtualization.add_virtualmachine`; the rack list is additionally filtered with `.restrict(user, 'view')`

### Known / deferred
- Race condition in name assignment (TOCTOU between the name suggestion and the actual object creation by the user) deliberately not fixed — requires an architecture decision (e.g. creating a placeholder object immediately), see `SECURITY-ANALYSE-2026-08-01.md`

## [1.4.0] - 2026-07-17

### Added
- Configurable naming rules via `NamierungsKonfiguration`: maximum length, number of counter digits, counting strategy per system type

## [1.3.1] - 2026-03-17

### Fixed
- `struct.error` when opening `/core/plugins/` caused by an empty `.mo` translation file

## [1.3.0] - 2026-03-14

### Changed
- UX improvements to the name generator form

## [1.2.1] - 2026-03-14

### Fixed
- `SerializerNotFound` error when deleting objects (missing API serializers for the NetBoxModel changelog)

## [1.2.0] - 2026-03-14

### Added
- "Generate Name & Add" button on the device and VM list views

## [1.1.1] - 2026-03-14

### Fixed
- Corrected a migration dependency for broader NetBox 4.5.x compatibility

## [1.1.0] - 2026-03-13

### Added
- Full multilingual support (German/English) incl. a bilingual README
- License and URL metadata in `pyproject.toml`

## [1.0.0] - 2026-03-12

### Added
- Initial version: automated, policy-compliant name assignment for network devices, servers, PCs, notebooks and VMs
- DB-managed parameters (sites, device types/functions, server purposes, VM areas/functions) with their own CRUD UI
