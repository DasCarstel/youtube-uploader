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
1. [Google Cloud Console](https://console.cloud.google.com/) → Neues Projekt
2. **YouTube Data API v3** aktivieren  
3. OAuth2-Credentials erstellen → als `credentials.json` speichern

> 📖 **Detaillierte Anleitung:** [docs/GOOGLE_API_SETUP.md](docs/GOOGLE_API_SETUP.md)

### 4. Los geht's
```bash
python uploader.py --preview  # Testen
python uploader.py           # Upload starten
```

## 🎬 Audio-Merging (Optional)

Gaming-Videos mit separaten Audio-Spuren können vor dem Upload optimiert werden:

```batch
merged2audioto2_auto_v2.bat  # Windows Script im Video-Ordner
```

→ Merged automatisch Game-Audio + Mikrofon und normalisiert die Lautstärke für YouTube

## 📁 Video-Organisation

```
AUFNAHMEN/SPIEL AUFNAHMEN/Grand Theft Auto V/
├── BUG/merged_LUSTIGER_BUG.mp4           # Einzelne Datei
└── merged_LUSTIGE_MOMENTE/               # Ganzer Ordner
    ├── video1.mp4
    └── video2.mp4
```

- **Einzelne Dateien:** `merged_*` oder `unmergable_*` Präfixe
- **Ganze Ordner:** Ordner mit Upload-Präfixen
- **Formate:** .mp4, .avi, .mov, .mkv, .webm, .flv

## 📋 Playlist-Management

Hierarchische Playlist-Zuordnung basierend auf Ordner-Struktur:

```
SPIEL AUFNAHMEN/Star Wars Jedi/BUG/video.mp4
   ↓ Wird automatisch hinzugefügt zu:
1. "BUG" 2. "Star Wars Jedi" 3. "SPIEL AUFNAHMEN"
```

## 🔧 Befehle

```bash
python uploader.py --preview    # System testen
python uploader.py --debug      # Debug-Infos  
python uploader.py             # Upload starten
python uploader.py --help      # Hilfe anzeigen
```

## 🐛 Häufige Probleme

**"credentials.json nicht gefunden"**
- OAuth2-Credentials von Google Cloud Console herunterladen
- Siehe [docs/GOOGLE_API_SETUP.md](docs/GOOGLE_API_SETUP.md)

**"Keine Videos gefunden"**
```bash
python uploader.py --debug --preview  # Debug-Infos anzeigen
```

**SMB/NAS-Laufwerk nicht erreichbar**
```bash
# Mount-Status prüfen
df -h | grep n_drive

# Bei Bedarf remounten  
sudo mount /home/username/n_drive
```

**YouTube API Quota überschritten**
- **Limit:** ~39-40 Videos pro Tag (getestet: 39 komplett + 1 teilweise)
- **Reset:** Täglich um Mitternacht PST
- **Lösung:** Warten oder Quota in Google Cloud Console erhöhen

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
