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

### 5. SMB-Drive mounten (nur für WSL-Umgebungen)
```bash
# Für WSL-Benutzer mit Windows-Netzlaufwerken:
# ~/n_drive/AUFNAHMEN sollte bereits als SMB-Mount verfügbar sein
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

### 2. Netzlaufwerk-Integration (SMB/CIFS)

Für Videos auf Netzlaufwerken (NAS, Server) unterstützt das System SMB/CIFS-Mounts:

```bash
# SMB-Mount einrichten (einmalig)
sudo mkdir -p /home/username/n_drive

# Credentials-Datei erstellen
sudo tee /etc/smb-credentials << EOF
username=your_username
password=your_password
domain=your_domain
EOF

sudo chmod 600 /etc/smb-credentials

# Automatisches Mount in /etc/fstab
echo "//SERVER_IP/SHARE_NAME /home/username/n_drive cifs credentials=/etc/smb-credentials,uid=$(id -u),gid=$(id -g),vers=3.0,file_mode=0755,dir_mode=0755,noperm 0 0" | sudo tee -a /etc/fstab

# Testen
sudo mount /home/username/n_drive
```

**Konfiguration in .env:**
```bash
RECORDINGS_PATH=/home/username/n_drive/AUFNAHMEN
```

**Mount nach Neustart:**
```bash
# Automatisch durch fstab oder manuell:
sudo mount /home/username/n_drive
```

### 3. YouTube Upload

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

### .env Konfiguration
```env
RECORDINGS_PATH=/pfad/zu/aufnahmen  # Anpassen an Ihr System
DEFAULT_VISIBILITY=unlisted        # private, unlisted, public  
DEBUG_MODE=false                    # true für detaillierte Ausgaben
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
   - Mount-Status prüfen: `df -h | grep n_drive`
   - Bei Bedarf remounten: `sudo mount ~/n_drive`

2. **SMB-Mount Probleme**
   ```bash
   # SMB-Verbindung testen
   ping SERVER_IP
   
   # Credentials prüfen
   sudo cat /etc/smb-credentials
   
   # Mount-Logs anzeigen
   dmesg | tail -10
   
   # Manuelles Mount mit Debug
   sudo mount -t cifs //SERVER_IP/SHARE /mount/point -o username=user,vers=3.0 -v
   ```

3. **"credentials.json nicht gefunden"**
   - Laden Sie die OAuth2-Credentials von der Google Cloud Console herunter
   - Benennen Sie die Datei zu `credentials.json` um

4. **"Keine Videos gefunden"**
   - Überprüfen Sie die Video-Präfixe (`merged_` oder `unmergable_`)
   - Aktivieren Sie Debug-Modus: `python uploader.py --debug --preview`

5. **YouTube API Quota überschritten**
   - YouTube Data API hat tägliche Limits von **~10.000 Einheiten pro Tag**
   - **Praktisch:** Ca. **39-40 Videos** pro Tag uploadbar (getestet: 39 komplett + 1 teilweise)
   - **Upload-Kosten:** ~250 Einheiten pro Video (Upload + Playlist + Metadaten)
   - **Lösung:** Warten Sie bis zum nächsten Tag (Reset um Mitternacht PST)
   - **Alternative:** Google Cloud Console - Quota-Erhöhung beantragen (kostenpflichtig)

6. **"Insufficient authentication scopes" oder Playlist-Fehler**
   - Die API-Berechtigung reicht nicht für Playlist-Management
   - Löschen Sie `token.json`: `rm -f token.json`
   - Authentifizieren Sie sich neu: `python uploader.py --preview` (testet jetzt auch die Authentifizierung)
   - Akzeptieren Sie alle Berechtigungen im Browser

## 📊 Implementation Status

### ✅ Vollständig implementiert
- [x] Automatische Video-Erkennung (Datei + Ordner-basiert)
- [x] YouTube Data API v3 Integration mit OAuth2
- [x] Multi-Playlist-Verwaltung (hierarchisch)
- [x] Datei-Umbenennung nach Upload (`uploaded_` Präfix)
- [x] Progress-Tracking mit 5MB Chunks
- [x] Debug- und Preview-Modi
- [x] Umfassende Fehler-Behandlung
- [x] Automatische Metadaten-Generierung
- [x] Encoding-Fixes für deutsche Umlaute
- [x] Folder-basierte Upload-Funktionalität

### 🚧 Mögliche Erweiterungen
- [ ] Thumbnail-Upload Integration
- [ ] Batch-Upload-Konfiguration per JSON
- [ ] Resume-Funktionalität bei unterbrochenen Uploads
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
