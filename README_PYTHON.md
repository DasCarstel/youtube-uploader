# YouTube Gaming Video Uploader - Installation und Setup

## 🚀 Schnellstart

### 1. Virtuelle Python-Umgebung erstellen
```bash
python3 -m venv venv
source venv/bin/activate  # Für Linux/macOS
# ODER
venv\Scripts\activate     # Für Windows
```

### 2. Python-Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 3. Umgebungsvariablen konfigurieren
```bash
cp .env.example .env
# Bearbeiten Sie die .env-Datei mit Ihren Pfaden
```

### 4. YouTube Data API Credentials einrichten

**Detaillierte Anleitung:** Siehe [GOOGLE_API_SETUP.md](GOOGLE_API_SETUP.md)

**Kurz-Version:**
1. Gehen Sie zur [Google Cloud Console](https://console.cloud.google.com/)
2. Erstellen Sie ein neues Projekt oder wählen Sie ein existierendes
3. Aktivieren Sie die **YouTube Data API v3**
4. Erstellen Sie OAuth2-Credentials (Desktop application)
5. Laden Sie die JSON-Datei herunter und benennen Sie sie zu `credentials.json` um

### 5. SMB-Drive mounten (für WSL)
```bash
# Bereits durchgeführt in Ihrem Setup:
# ~/n_drive/AUFNAHMEN ist Ihr gemountetes N: Laufwerk
```

## 🎮 Verwendung

### Virtuelle Umgebung aktivieren
```bash
source venv/bin/activate
# ODER verwenden Sie das praktische Script:
./activate_venv.sh
```

### Preview-Modus (empfohlen für ersten Test)
```bash
python uploader.py --preview
```

### Standard-Upload
```bash
python uploader.py
```

### Debug-Modus
```bash
python uploader.py --debug
```

### Alternativer Pfad
```bash
python uploader.py --path /anderer/pfad/zu/aufnahmen
```

### Hilfe anzeigen
```bash
python uploader.py --help
```

## 📁 Ordner-Struktur

Das Skript erwartet folgende Struktur in Ihrem AUFNAHMEN-Verzeichnis:

```
AUFNAHMEN/
├── SPIEL AUFNAHMEN/
│   ├── Grand Theft Auto V/
│   │   ├── BUG/
│   │   │   ├── merged_LUSTIGER_BUG.mp4
│   │   │   └── unmergable_CRASH_VIDEO.mp4
│   │   └── LUSTIG/
│   │       └── merged_PERFEKTES_EINPARKEN.mp4
│   └── Valorant/
│       ├── merged_ACE_ROUND.mp4
│       └── unmergable_TEAM_WIPE.mp4
├── WITZIGE MOMENTE/
│   └── merged_FUNNY_MOMENT.mp4
└── GESCHNITTE MOMENTE/
    └── unmergable_HIGHLIGHT_REEL.mp4
```

## 🎯 Video-Erkennung

Das Skript sucht nach Videos mit folgenden Kriterien:
- **Präfixe:** `merged_` oder `unmergable_`
- **Formate:** .mp4, .avi, .mov, .mkv, .webm, .flv
- **Ausschluss:** Bereits hochgeladene Videos (Präfix `uploaded_`)

## 🔧 Konfiguration

### .env Datei
```env
RECORDINGS_PATH=/home/carst/n_drive/AUFNAHMEN
DEFAULT_VISIBILITY=unlisted
DEBUG_MODE=false
```

### Sichtbarkeits-Optionen
- `private` - Nur Sie können das Video sehen
- `unlisted` - Nur Personen mit dem Link können das Video sehen
- `public` - Jeder kann das Video finden und ansehen

## 📋 Playlist-Management

- Videos werden automatisch zu Playlists hinzugefügt basierend auf der Ordner-Struktur
- **Hierarchie:** Unterordner > Spiel > Hauptordner
- Playlists werden automatisch erstellt falls sie nicht existieren

## 🔄 Datei-Lifecycle

Nach erfolgreichem Upload:
```
VOR Upload:
├── merged_LUSTIGES_GAMEPLAY.mp4
├── unmergable_BUG_VIDEO.mp4  

NACH Upload:
├── uploaded_LUSTIGES_GAMEPLAY.mp4  ✅
├── uploaded_BUG_VIDEO.mp4          ✅
```

## 🐛 Troubleshooting

### Häufige Probleme

1. **"Aufnahmen-Pfad nicht gefunden"**
   - Überprüfen Sie, ob der SMB-Drive gemountet ist
   - Testen Sie: `ls ~/n_drive/AUFNAHMEN`

2. **"credentials.json nicht gefunden"**
   - Laden Sie die OAuth2-Credentials von der Google Cloud Console herunter
   - Benennen Sie die Datei zu `credentials.json` um

3. **"Keine Videos gefunden"**
   - Überprüfen Sie die Video-Präfixe (`merged_` oder `unmergable_`)
   - Aktivieren Sie Debug-Modus: `python uploader.py --debug --preview`

4. **YouTube API Quota überschritten**
   - YouTube Data API hat tägliche Limits
   - Warten Sie bis zum nächsten Tag oder erhöhen Sie das Quota

5. **"Insufficient authentication scopes" oder Playlist-Fehler**
   - Die API-Berechtigung reicht nicht für Playlist-Management
   - Löschen Sie `token.json`: `rm -f token.json`
   - Authentifizieren Sie sich neu: `python uploader.py --preview` (testet jetzt auch die Authentifizierung)
   - Akzeptieren Sie alle Berechtigungen im Browser

## 📊 Features

### ✅ Implementiert
- [x] Automatische Video-Erkennung
- [x] YouTube Data API v3 Integration
- [x] Intelligente Playlist-Verwaltung
- [x] Datei-Umbenennung nach Upload
- [x] Progress-Tracking
- [x] Debug-Modus
- [x] Preview-Modus
- [x] Fehler-Behandlung
- [x] Metadaten-Generierung

### 🚧 Geplant
- [ ] Thumbnail-Upload
- [ ] Batch-Upload-Konfiguration
- [ ] Resume-Funktionalität
- [ ] Multi-Account-Support

## 🔐 Sicherheit

- OAuth2-Tokens werden lokal in `token.json` gespeichert
- Credentials werden nicht im Code gespeichert
- .env-Dateien sind in .gitignore ausgeschlossen

## 📞 Support

Bei Problemen:
1. Aktivieren Sie Debug-Modus: `--debug`
2. Überprüfen Sie die Konsolen-Ausgabe
3. Testen Sie zunächst mit `--preview`
4. Überprüfen Sie YouTube Studio für Upload-Status
