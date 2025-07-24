# 🎮 YouTube Gaming Video Uploader

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![YouTube Data API v3](https://img.shields.io/badge/YouTube%20Data%20API-v3-red.svg)](https://developers.google.com/youtube/v3)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Ein automatisierter Uploader für Gaming-Videos zu YouTube mit intelligenter Playlist-Verwaltung, Audio-Merging und Datei-Organisation basierend auf der YouTube Data API v3.

## ✨ Features

- 🎯 **Automatische Video-Erkennung** (`merged_` und `unmergable_` Präfixe)
- 📁 **Folder-basierte Uploads** - Ganze Ordner mit Upload-Präfixen werden erkannt
- 🎵 **Audio-Merging** für Gaming-Videos mit separaten Audio-Spuren
- 📋 **Multi-Playlist-Support** - Videos werden zu allen hierarchischen Playlists hinzugefügt
- 🔧 **Encoding-Fixes** für deutsche Umlaute (WINDM�LE → WINDMÜHLE)
- 📊 **Progress-Tracking** mit 5MB Chunks und Ein-Zeilen-Updates
- �️ **Automatische Metadaten-Extraktion** (Titel, Aufnahmedatum, Spiel, Status)
- 🔒 **OAuth2-Authentifizierung** mit sicherer Token-Verwaltung

## 🚀 Schnellstart

### 1. Installation
```bash
# Repository klonen
git clone https://github.com/yourusername/youtube-uploader.git
cd youtube-uploader

# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Konfiguration
```bash
# .env Datei erstellen und bearbeiten
cp .env.example .env

# In .env anpassen:
# RECORDINGS_PATH=/pfad/zu/ihren/aufnahmen
# DEFAULT_VISIBILITY=unlisted
```

### 3. YouTube API einrichten
1. [Google Cloud Console](https://console.cloud.google.com/) öffnen
2. Neues Projekt erstellen
3. **YouTube Data API v3** aktivieren
4. OAuth2-Credentials erstellen (Desktop application)
5. JSON-Datei als `credentials.json` speichern

> 📖 **Detaillierte Anleitung:** [docs/GOOGLE_API_SETUP.md](docs/GOOGLE_API_SETUP.md)

### 4. Ersten Upload
```bash
source venv/bin/activate

# Vorschau (testet auch Authentifizierung)
python uploader.py --preview

# Upload starten
python uploader.py
```

## 🎬 Audio-Vorbereitung (Optional)

Für Gaming-Videos mit separaten Audio-Spuren (Game + Mikrofon):

```batch
# In Windows, im Video-Ordner ausführen:
merged2audioto2_auto_v2.bat
```

Das Script analysiert automatisch alle .mp4 Dateien und merged Videos mit 2+ Audiospuren optimal für YouTube.

## 📁 Video-Organisation

### Unterstützte Struktur:
```
AUFNAHMEN/
├── SPIEL AUFNAHMEN/
│   ├── Grand Theft Auto V/
│   │   ├── BUG/
│   │   │   ├── merged_LUSTIGER_BUG.mp4
│   │   │   └── unmergable_CRASH_VIDEO.mp4
│   │   └── merged_LUSTIGE_MOMENTE/     # ← Ganzer Ordner
│   │       ├── video1.mp4
│   │       └── video2.mp4
├── WITZIGE MOMENTE/
└── GESCHNITTE MOMENTE/
```

### Video-Erkennung:
- **Einzelne Dateien:** `merged_*` oder `unmergable_*` Präfixe
- **Ganze Ordner:** Ordner mit `merged_*` oder `unmergable_*` Namen
- **Formate:** .mp4, .avi, .mov, .mkv, .webm, .flv

## 📋 Playlist-Management

Videos werden automatisch zu **hierarchischen Playlists** hinzugefügt:

```
SPIEL AUFNAHMEN/Star Wars Jedi/BUG/video.mp4
   ↓ Wird hinzugefügt zu:
1. "BUG" (primäre Playlist)
2. "Star Wars Jedi" 
3. "SPIEL AUFNAHMEN"
```

- ✅ Playlists werden automatisch erstellt
- 🎯 Intelligente Hierarchie-Erkennung

## 🔧 Wichtige Befehle

```bash
# System testen (empfohlen zuerst)
python uploader.py --preview

# Debug-Informationen
python uploader.py --debug --preview

# Upload starten
python uploader.py

# Hilfe anzeigen
python uploader.py --help

# Alternativer Pfad
python uploader.py --path /anderer/pfad
```

## 🐛 Häufige Probleme

**"credentials.json nicht gefunden"**
- OAuth2-Credentials von Google Cloud Console herunterladen
- Siehe [docs/GOOGLE_API_SETUP.md](docs/GOOGLE_API_SETUP.md)

**"Keine Videos gefunden"**
```bash
python uploader.py --debug --preview  # Debug-Infos anzeigen
```

**YouTube API Quota überschritten**
- Standard: ~6 Videos/Tag
- Lösung: Quota in Google Cloud Console erhöhen

## 📚 Dokumentation

- 📖 **[Detaillierte Installation](docs/README_PYTHON.md)** - Vollständige Setup-Anleitung
- 🔧 **[API Setup Guide](docs/GOOGLE_API_SETUP.md)** - YouTube API einrichten
- 🚀 **[Schnellstart Guide](docs/SCHNELLSTART.md)** - 5-Minuten Setup
- 📋 **[Spezifikation](docs/uploader.instructions.md)** - Vollständige Anforderungen
- 📚 **[Dokumentations-Übersicht](docs/)** - Alle Dokumente im Überblick

## ⚙️ Systemanforderungen

- **Python:** 3.8+
- **FFmpeg:** Für Audio-Merging (optional)
- **Google Account:** Mit YouTube-Kanal
- **Internet:** Stabile Verbindung für Uploads

## 🔐 Sicherheit

- ✅ OAuth2-Authentifizierung mit lokaler Token-Speicherung
- ✅ Keine Credentials im Code gespeichert
- ✅ `.env` und `token.json` in `.gitignore`

## 🤝 Beitragen

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/name`)
3. Änderungen committen (`git commit -m 'Add feature'`)
4. Push zum Branch (`git push origin feature/name`)
5. Pull Request öffnen

## 📄 Lizenz

MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

---

**Automatisierter YouTube Upload für Gaming-Videos - Entwickelt für Content Creator** 🎮

> � **Tipp:** Starten Sie mit `python uploader.py --preview` um das System zu testen!
