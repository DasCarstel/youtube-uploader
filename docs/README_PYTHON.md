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

## 🎮 Workflow und Video-Vorbereitung

### 1. Audio-Merging Vorbereitung (Optional)

Viele Gaming-Videos haben separate Audiospuren (z.B. Game-Audio + Mikrofon). Das enthaltene `merged2audioto2_auto_v2.bat` Script hilft dabei:

```batch
# Analysiert alle .mp4 Dateien im Ordner
# Videos mit 2+ Audiospuren: Wird gemerged → "merged_" Präfix
# Videos mit 1 Audiospur: Wird umbenannt → "unmergable_" Präfix
```

**Funktionen des Batch-Scripts:**
- 🔍 **Automatische Analyse** aller .mp4 Dateien
- 🎵 **Audio-Erkennung** (Zählung der Audiospuren)
- 🔀 **Intelligentes Merging** mit Loudness-Normalisierung
- 📝 **Automatische Umbenennung** basierend auf Audio-Struktur
- ⚡ **Batch-Verarbeitung** für ganze Ordner

**Audio-Processing Details:**
- Loudness-Normalisierung auf -16 LUFS (YouTube-Standard)
- Mikrofon-Audio wird auf 25% reduziert (bessere Balance)
- Stereo-Output mit AAC-Codec für beste Kompatibilität
- Video-Stream wird unverändert kopiert (schnelle Verarbeitung)

**FFmpeg-Kommando (vereinfacht):**
```bash
ffmpeg -i "video.mp4" \
  -filter_complex "[0:a:0]loudnorm=I=-16,volume=0.25[mic];[0:a:1]loudnorm=I=-16[game];[mic][game]amerge[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac "merged_video.mp4"
```

**Typische Gaming-Szenarien:**
- 🎮 **Game + Mikrofon:** Dual-Audio wird optimal gemerged
- 🔇 **Nur Game-Audio:** Video wird als "unmergable" markiert (kein Processing nötig)
- ✅ **Bereits gemergt:** Video wird als "unmergable" markiert

### 2. YouTube Upload

Nach der Audio-Vorbereitung kann der Python Uploader alle vorbereiteten Videos verarbeiten:

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

### Einzelne Video-Dateien:
- **Präfixe:** `merged_` oder `unmergable_`
- **Formate:** .mp4, .avi, .mov, .mkv, .webm, .flv
- **Ausschluss:** Bereits hochgeladene Videos (Präfix `uploaded_`)

### Folder-basierte Uploads (NEU):
- **Ordner-Präfixe:** `merged_` oder `unmergable_` im Ordnernamen
- **Verhalten:** Alle Videos im Ordner werden automatisch erkannt und hochgeladen
- **Typ-Bestimmung:** Video-Typ wird vom Ordner-Präfix abgeleitet
- **Hierarchie:** Unterordner werden in die Playlist-Struktur einbezogen

### Beispiel für Folder-basierte Uploads:
```
AUFNAHMEN/SPIEL AUFNAHMEN/Grand Theft Auto V/merged_LUSTIGE_MOMENTE/
├── video1.mp4          # Wird als 'merged' erkannt
├── video2.mp4          # Wird als 'merged' erkannt
└── subfolder/
    └── video3.mp4      # Wird als 'merged' erkannt

# Playlist-Struktur: "SPIEL AUFNAHMEN > Grand Theft Auto V > LUSTIGE_MOMENTE"
```

## 🎮 Wichtige Features im Detail

### Multi-Playlist-Support
Videos werden automatisch zu **allen hierarchischen Playlists** hinzugefügt:
```
Beispiel: AUFNAHMEN/SPIEL AUFNAHMEN/Star Wars Jedi Fallen Order/BUG/video.mp4

Wird hinzugefügt zu:
1. "BUG" (primäre Playlist)
2. "Star Wars Jedi Fallen Order" 
3. "SPIEL AUFNAHMEN"
```

### Umfassende Encoding-Fixes
Das System behebt automatisch häufige Encoding-Probleme:
- `WINDM�LE` → `WINDMÜHLE`
- `H�NGT` → `HÄNGT` 
- `VIEH H�NGT` → `VIEH HÄNGT`
- Unicode-Escape-Sequenzen (`\udcc4` → `Ä`)
- Sowohl in der Konsolen-Ausgabe als auch in YouTube-Metadaten

### Verbesserte Upload-Anzeige
- Saubere Ein-Zeilen-Progress-Bar mit 5MB Chunks
- Prozentanzeige und geschätzte Restzeit
- Retry-Information bei temporären Fehlern
- Farbkodierte Status-Meldungen

### Status-Beschreibungen
Jedes Video erhält automatisch eine detaillierte Beschreibung mit:
- Titel und Spielinformation
- Audio-Status (Sound gemerged vs. unmergable)
- Aufnahmedatum und -zeit
- Kategorie-Information aus der Ordner-Struktur

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
