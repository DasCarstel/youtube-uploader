# 🚀 YouTube Gaming Video Uploader - Schnellstart Guide

> **Schnelle Einrichtung für den automatisierten Upload von Gaming-Videos zu YouTube**

## 📋 Voraussetzungen

- Python 3.8+
- Git
- Google Account mit YouTube-Kanal
- FFmpeg (optional, für Audio-Merging)

## ⚡ 5-Minuten Setup

### 1. Repository klonen und Dependencies installieren
```bash
git clone https://github.com/yourusername/youtube-uploader.git
cd youtube-uploader

# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ODER für Windows:
# venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Konfiguration erstellen
```bash
# .env Datei erstellen
cp .env.example .env

# Bearbeiten Sie die .env-Datei mit Ihren Pfaden:
# RECORDINGS_PATH=/pfad/zu/ihren/aufnahmen
# DEFAULT_VISIBILITY=unlisted
# DEBUG_MODE=false
```

### 2.1 SMB/NAS-Laufwerk mounten (Optional)
Falls Ihre Videos auf einem Netzlaufwerk (SMB/CIFS) gespeichert sind:

```bash
# 1. Mount-Punkt erstellen
mkdir -p ~/n_drive

# 2. SMB-Credentials-Datei erstellen (einmalig)
sudo nano /etc/smb-credentials
```

**Inhalt der `/etc/smb-credentials` Datei:**
```
username=ihr_benutzername
password=ihr_passwort
domain=ihre_domain  # Optional
```

```bash
# 3. Berechtigung setzen
sudo chmod 600 /etc/smb-credentials

# 4. fstab-Eintrag hinzufügen (für automatisches Mount)
sudo nano /etc/fstab
```

**Fügen Sie diese Zeile zu `/etc/fstab` hinzu:**
```
//IP_ADRESSE/SHARE_NAME /home/username/n_drive cifs credentials=/etc/smb-credentials,uid=1001,gid=1001,vers=3.0,file_mode=0755,dir_mode=0755,noperm 0 0
```

```bash
# 5. Testen und mounten
sudo mount /home/username/n_drive

# 6. Prüfen ob erfolgreich
df -h | grep n_drive
```

**Dann in .env setzen:**
```bash
RECORDINGS_PATH=/home/username/n_drive/AUFNAHMEN
```

### 3. YouTube API Credentials einrichten
```bash
# Detaillierte Anleitung lesen:
cat GOOGLE_API_SETUP.md
```

**Kurzversion:**
1. [Google Cloud Console](https://console.cloud.google.com/) öffnen
2. Neues Projekt erstellen
3. **YouTube Data API v3** aktivieren
4. OAuth2-Credentials erstellen (Desktop application)
5. JSON-Datei als `credentials.json` speichern

### 4. System testen
```bash
# Virtuelle Umgebung aktivieren
source venv/bin/activate

# Erste Vorschau (testet auch Authentifizierung)
python uploader.py --preview

# Upload starten
python uploader.py
```

Falls Ihre Videos mehrere Audiospuren haben (Game-Audio + Mikrofon), verwenden Sie das mitgelieferte Batch-Script:

```batch
# In Windows (im Video-Ordner):
merged2audioto2_auto_v2.bat
```

**Das Script macht:**
- 🔍 Analysiert alle .mp4 Dateien automatisch  
- 🎵 Videos mit 2+ Audiospuren: Merging → `merged_` Präfix
- 📝 Videos mit 1 Audiospur: Umbenennung → `unmergable_` Präfix
- 🎚️ Loudness-Normalisierung (-16 LUFS) für YouTube-Qualität

## 📁 Video-Organisation

### Beispiel-Struktur:
```
AUFNAHMEN/SPIEL AUFNAHMEN/Grand Theft Auto V/
├── BUG/merged_LUSTIGER_BUG.mp4
├── BUG/unmergable_CRASH_VIDEO.mp4  
└── merged_LUSTIGE_MOMENTE/          # ← Ganzer Ordner-Upload
    ├── video1.mp4 → video2.mp4
```

### Erkennungsregeln:
- **Einzelne Dateien:** `merged_*` oder `unmergable_*` Präfixe
- **Ganze Ordner:** Ordner mit Upload-Präfixen werden komplett verarbeitet
- **Bereits verarbeitet:** `uploaded_*` werden übersprungen

## ✨ Haupt-Features

- 🎯 Automatische Video-Erkennung mit Präfix-System
- 📁 Folder-basierte Uploads - Ganze Ordner werden verarbeitet  
- 📋 Multi-Playlist-Support - Hierarchische Playlist-Zuordnung
- 🎵 Audio-Merging für Gaming-Videos mit FFmpeg
- 🔧 Encoding-Fixes für deutsche Umlaute
- 📊 Progress-Tracking mit sauberen Ein-Zeilen-Updates

## 🔧 Wichtige Befehle

```bash
python uploader.py --preview          # System testen
python uploader.py --debug --preview  # Debug-Informationen  
python uploader.py                    # Upload starten
python uploader.py --path /pfad       # Alternativer Aufnahmen-Pfad
```

## 📊 Konfiguration (.env)

```env
# Pfad zu Ihren Aufnahmen
RECORDINGS_PATH=/pfad/zu/aufnahmen

# Sichtbarkeit: private, unlisted, public
DEFAULT_VISIBILITY=unlisted

# Debug-Ausgaben aktivieren
DEBUG_MODE=false
```

## 🎬 Playlist-Management

```
SPIEL AUFNAHMEN/Star Wars Jedi/BUG/video.mp4
   ↓ Automatisch hinzugefügt zu:
1. "BUG" 2. "Star Wars Jedi" 3. "SPIEL AUFNAHMEN"
```

- ✅ Playlists werden automatisch erstellt
- 🎯 Hierarchie basierend auf Ordner-Struktur

## ⚠️ Wichtige Hinweise

1. **API Limits:** YouTube Data API hat tägliche Quotas (~6 Videos/Tag bei Standard-Quota)
2. **Sicherheit:** `credentials.json` wird aus Sicherheitsgründen nicht in Git gespeichert
3. **SMB-Verbindungen:** Nach einem Neustart muss das Netzlaufwerk möglicherweise neu gemountet werden

## 🛠️ Troubleshooting

### SMB-Mount Probleme
```bash
# SMB-Laufwerk nach Neustart remounten
sudo mount /home/username/n_drive

# Prüfen ob Mount erfolgreich
df -h | grep n_drive

# SMB-Verbindung testen
ls -la /home/username/n_drive/

# Mount-Status prüfen
mount | grep cifs
```

### Häufige Fehler
**"No such file or directory"**
- SMB-Laufwerk nicht gemountet → `sudo mount /home/username/n_drive`

**"Permission denied"**
- SMB-Credentials prüfen → `/etc/smb-credentials`
- UID/GID in fstab prüfen → `id` Befehl ausführen

**"Operation now in progress"**
- Netzwerkverbindung prüfen
- IP-Adresse des NAS/Servers prüfen
3. **Erste Authentifizierung:** Browser öffnet sich automatisch für OAuth2-Flow
4. **Datei-Sicherheit:** Videos werden nur umbenannt, nicht gelöscht (`uploaded_` Präfix)
5. **Internet:** Stabile Verbindung für große Video-Uploads erforderlich

## 🐛 Häufige Probleme

### "credentials.json nicht gefunden"
```bash
# 1. Google Cloud Console besuchen
# 2. OAuth2-Credentials für Desktop-App erstellen
# 3. JSON-Datei als 'credentials.json' speichern
```

### "Keine Videos gefunden"
```bash
# Video-Präfixe überprüfen (merged_ oder unmergable_)
python uploader.py --debug --preview
```

### YouTube API Quota überschritten
```bash
# Standardlimit: ~6 Videos/Tag
# Lösung: Warten oder Quota in Google Cloud Console erhöhen
```

## 📚 Weitere Dokumentation

- 📖 **[README.md](README.md)** - Vollständige Dokumentation
- 🔧 **[GOOGLE_API_SETUP.md](GOOGLE_API_SETUP.md)** - Detaillierte API-Einrichtung
- 📋 **[README_PYTHON.md](README_PYTHON.md)** - Technische Details
- 📝 **[Anforderungen](.github/instructions/uploader.instructions.md)** - Vollständige Spezifikation

## 🎉 Los geht's!

Nach dem Setup können Sie sofort starten:

```bash
source venv/bin/activate
python uploader.py --preview  # Erst testen
python uploader.py           # Dann uploaden
```

**Happy Gaming und erfolgreiche Uploads!** 🎮✨
