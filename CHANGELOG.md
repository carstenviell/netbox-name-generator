# Changelog

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.

Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

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
