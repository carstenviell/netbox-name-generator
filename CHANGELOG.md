# Changelog

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.

Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [1.4.4] - 2026-08-10

### Behoben
- Formular zeigte nach Auswahl des System Type keine weiteren Felder mehr an: Der beim XSS-Fix (v1.4.1) über den `json_script`-Tags eingefügte Erklärkommentar nutzte die mehrzeilige `{# ... #}`-Syntax, die Django nur einzeilig unterstützt. Dadurch wurde der Kommentar wortwörtlich in die Seite gerendert; die darin enthaltene `</`-Sequenz ließ den Browser das direkt folgende `<script id="ng-funktionen-data">`-Tag als ungültigen Kommentar verschlucken, wodurch `document.getElementById(...)` `null` lieferte und das gesamte Formular-JavaScript (inkl. Dropdown-Umschaltung) mit einer `TypeError` abbrach, bevor es initialisiert war. Kommentar auf `{% comment %}...{% endcomment %}` umgestellt

## [1.4.3] - 2026-08-02

### Sicherheit
- Race Condition bei der Namensvergabe entschärft: Das Plugin legt nie selbst ein Objekt an, sondern leitet mit vorausgefülltem `?name=...` zur NetBox-Erstellungsseite weiter, die der Nutzer separat (ggf. Minuten später) ausfüllt — zwei gleichzeitige Generierungen konnten bisher denselben Namensvorschlag erhalten. Neues Modell `ReservedName` (Unique-Constraint, 10-Minuten-TTL) reserviert generierte Namen atomar: der Normalfall wird proaktiv verhindert (Reservierungen fließen in die Kollisionsprüfung ein), eine echte gleichzeitige Kollision wird über den DB-Constraint abgefangen und dem Nutzer mit Aufforderung zum erneuten Versuch gemeldet. Gilt für alle auto-nummerierten Typen (Netzwerkgerät/Server/PC/VM); Notebook-Namen sind deterministisch und daher nicht betroffen. Live gegen den Container verifiziert (Normalfall, erzwungene Kollision, TTL-Ablauf)

## [1.4.2] - 2026-08-01

### Sicherheit
- **Git-Historie bereinigt**: Der in CRITICAL-01 (`SECURITY-ANALYSE-2026-08-01.md`) dokumentierte private SSH-Schlüssel (`ssh_carstenviell`/`ssh_carstenviell.pub`, ursprünglich in einem Commit von 2026-03-14 versehentlich eingecheckt) wurde per `git filter-repo` aus **jedem** Commit der Historie entfernt und die bereinigte Historie per Force-Push auf `main` sowie alle betroffenen Release-Tags (`v1.3.0`–`v1.4.1`) angewendet. Commit-Hashes ab dem betroffenen Commit haben sich dadurch geändert (`v1.1.0`–`v1.2.1` unverändert, da vor der Einführung des Schlüssels).
- **Wichtig für bestehende Klone/Forks**: Ein `git pull` auf einem alten Klon führt zu divergierender Historie. Empfehlung: Repository neu klonen (`git clone`), lokale Änderungen vorher sichern. GitHubs eigene Caches/Forks/PR-Referenzen auf die alten Commits sind von dieser Bereinigung nicht erfasst — falls relevant, GitHub Support kontaktieren.
- Der exponierte Schlüssel gilt unabhängig von dieser Bereinigung weiterhin als kompromittiert und sollte, falls noch nicht geschehen, umgehend rotiert/widerrufen werden.

## [1.4.1] - 2026-08-01

### Sicherheit
- Stored XSS behoben: Die JSON-Konfiguration für den Name-Generator wurde per `json.dumps()` + `|safe` in einen `<script>`-Block gerendert, wodurch ein `beschreibung`-Feld (z. B. bei `NetzwerkgeraetFunktion`) mit einer `</script>`-Sequenz aus dem Skript-Block ausbrechen konnte (Session-Kompromittierung jedes Nutzers, der die Startseite öffnet, ausgelöst von einem Nutzer mit deutlich geringerem Privileg). Template nutzt jetzt Djangos `|json_script`-Filter, der HTML-sicher escaped
- Defense in Depth: `beschreibung`-Felder aller sechs Konfigurationsmodelle (`Standort`, `NetzwerkgeraetTyp`, `NetzwerkgeraetFunktion`, `ServerZweck`, `VmBereich`, `VmFunktion`) lassen die Zeichen `<`/`>` nicht mehr zu
- `NameGeneratorView` prüfte bisher nur Login, keine Berechtigung, und lieferte dadurch jedem eingeloggten Nutzer die vollständige Rack-/Standort-Topologie sowie (indirekt) den Geräte-/VM-Namensbestand. Erfordert jetzt `dcim.add_device` und `virtualization.add_virtualmachine`; die Rack-Liste wird zusätzlich auf `.restrict(user, 'view')` gefiltert

### Bekannt / zurückgestellt
- Race Condition bei der Namensvergabe (TOCTOU zwischen Namensvorschlag und tatsächlicher Objekterstellung durch den Nutzer) bewusst nicht behoben — erfordert eine Architekturentscheidung (z. B. sofortige Platzhalter-Objekterstellung), siehe `SECURITY-ANALYSE-2026-08-01.md`

## [1.4.0] - 2026-07-17

### Neu
- Konfigurierbare Namensregeln über `NamierungsKonfiguration`: maximale Länge, Anzahl Zählerstellen, Zählstrategie pro Systemtyp

## [1.3.1] - 2026-03-17

### Behoben
- `struct.error` beim Öffnen von `/core/plugins/` durch leere `.mo`-Übersetzungsdatei

## [1.3.0] - 2026-03-14

### Geändert
- UX-Verbesserungen am Namensgenerator-Formular

## [1.2.1] - 2026-03-14

### Behoben
- `SerializerNotFound`-Fehler beim Löschen von Objekten (fehlende API-Serializer für NetBoxModel-Changelog)

## [1.2.0] - 2026-03-14

### Neu
- "Generate Name & Add"-Button auf den Device- und VM-Listenansichten

## [1.1.1] - 2026-03-14

### Behoben
- Migrations-Abhängigkeit korrigiert für breitere NetBox-4.5.x-Kompatibilität

## [1.1.0] - 2026-03-13

### Neu
- Vollständige Mehrsprachigkeit (Deutsch/Englisch) inkl. zweisprachigem README
- Lizenz- und URL-Metadaten in `pyproject.toml`

## [1.0.0] - 2026-03-12

### Neu
- Initiale Version: automatisierte, regelkonforme Namensvergabe für Netzwerkgeräte, Server, PCs, Notebooks und VMs
- DB-verwaltete Parameter (Standorte, Gerätetypen/-funktionen, Server-Zwecke, VM-Bereiche/-Funktionen) mit eigener CRUD-UI
