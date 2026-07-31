# Changelog

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.

Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

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
