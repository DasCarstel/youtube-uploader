# 🌐 SMB/NAS-Laufwerk Setup für YouTube Uploader

> **Anleitung für die Integration von Netzlaufwerken (SMB/CIFS) in den YouTube Gaming Video Uploader**

## 📋 Überblick

Viele Content Creator speichern ihre Gaming-Videos auf NAS-Servern oder Netzlaufwerken. Diese Anleitung zeigt, wie Sie SMB/CIFS-Shares dauerhaft in Linux einbinden, damit der YouTube Uploader direkt darauf zugreifen kann.

## ⚙️ Einmalige Einrichtung

### 1. Notwendige Pakete installieren
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install cifs-utils

# CentOS/RHEL/Fedora
sudo yum install cifs-utils
# ODER
sudo dnf install cifs-utils
```

### 2. Mount-Punkt erstellen
```bash
# Erstelle Ordner für das Netzlaufwerk
mkdir -p ~/n_drive

# Alternativ: System-weiter Mount-Punkt
sudo mkdir -p /mnt/nas
```

### 3. SMB-Credentials sicher speichern
```bash
# Erstelle Credentials-Datei (als root)
sudo nano /etc/smb-credentials
```

**Inhalt der Datei:**
```
username=ihr_benutzername
password=ihr_passwort
domain=ihre_domain
```

```bash
# Sichere Berechtigung setzen (nur root kann lesen)
sudo chmod 600 /etc/smb-credentials
sudo chown root:root /etc/smb-credentials
```

### 4. Benutzer-ID ermitteln
```bash
# Ihre UID und GID herausfinden
id
# Ausgabe: uid=1001(carst) gid=1001(carst) groups=...
```

### 5. Automatisches Mount konfigurieren
```bash
# fstab bearbeiten
sudo nano /etc/fstab
```

**Zeile am Ende der fstab hinzufügen:**
```
//IP_ADRESSE/SHARE_NAME /home/username/n_drive cifs credentials=/etc/smb-credentials,uid=1001,gid=1001,vers=3.0,file_mode=0755,dir_mode=0755,noperm 0 0
```

**Parameter erklären:**
- `//IP_ADRESSE/SHARE_NAME`: Ihr NAS/Server und Share-Name
- `/home/username/n_drive`: Ihr lokaler Mount-Punkt
- `uid=1001,gid=1001`: Ihre Benutzer-ID (aus `id` Befehl)
- `vers=3.0`: SMB-Version (meist 3.0 oder 2.1)
- `file_mode=0755,dir_mode=0755`: Dateiberechtigungen
- `noperm`: Ignore Serverberechtigungen

### 6. Erstes Mount testen
```bash
# Mount testen
sudo mount /home/username/n_drive

# Erfolgsprüfung
df -h | grep n_drive
ls -la /home/username/n_drive/

# Aufnahmen-Ordner prüfen
ls -la /home/username/n_drive/AUFNAHMEN/
```

## 🎮 Integration mit YouTube Uploader

### .env Konfiguration
```bash
# .env Datei bearbeiten
nano .env
```

**Pfad auf NAS-Laufwerk setzen:**
```env
RECORDINGS_PATH=/home/username/n_drive/AUFNAHMEN
DEFAULT_VISIBILITY=unlisted
DEBUG_MODE=false
```

### Testen
```bash
# System testen
source venv/bin/activate
python uploader.py --debug --preview
```

## 🔧 Alltägliche Nutzung

### Nach Neustart
```bash
# SMB-Laufwerk ist durch fstab automatisch gemountet
# Bei Problemen manuell mounten:
sudo mount /home/username/n_drive
```

### Status prüfen
```bash
# Mount-Status anzeigen
df -h | grep cifs
mount | grep cifs

# Netzwerk-Verbindung testen
ping IP_ADRESSE_IHRES_NAS
```

## 🛠️ Troubleshooting

### Häufige Probleme

**"mount error(115): Operation now in progress"**
```bash
# Netzwerk prüfen
ping IP_ADRESSE

# SMB-Service auf NAS prüfen
telnet IP_ADRESSE 445

# Mit anderen SMB-Versionen probieren
sudo mount -t cifs //IP/SHARE /mount/point -o vers=2.1,username=user
```

**"mount error(13): Permission denied"**
```bash
# Credentials prüfen
sudo cat /etc/smb-credentials

# Benutzer auf NAS existiert?
# Berechtigung für Share auf NAS korrekt?

# Mit Debug-Infos mounten
sudo mount -t cifs //IP/SHARE /mount/point -o username=user,vers=3.0,debug
```

**"No such file or directory"**
```bash
# Mount-Punkt existiert?
ls -la /home/username/n_drive

# fstab-Syntax korrekt?
sudo mount -a  # Alle fstab-Einträge mounten
```

**"Transport endpoint is not connected"**
```bash
# Verbindung unterbrochen - remounten
sudo umount /home/username/n_drive
sudo mount /home/username/n_drive

# Oder forciert unmounten bei hängender Verbindung
sudo umount -f /home/username/n_drive
sudo umount -l /home/username/n_drive  # lazy unmount
```

### Debug-Kommandos
```bash
# SMB-Debug-Mount
sudo mount -t cifs //IP/SHARE /mount/point -o username=user,vers=3.0,debug -v

# Kernel-Messages anzeigen
dmesg | tail -20

# Netzwerk-Trace
sudo tcpdump -i eth0 port 445

# SMB-Verbindung testen mit smbclient
smbclient -L //IP_ADRESSE -U username
```

## 📊 Beispiel-Konfiguration

**Vollständiges Beispiel für Synology NAS:**
```bash
# /etc/smb-credentials
username=media_user
password=super_secure_password
domain=WORKGROUP

# /etc/fstab Zeile
//192.168.1.100/video /home/carst/n_drive cifs credentials=/etc/smb-credentials,uid=1001,gid=1001,vers=3.0,file_mode=0755,dir_mode=0755,noperm 0 0

# .env Konfiguration
RECORDINGS_PATH=/home/carst/n_drive/AUFNAHMEN
```

**Test-Sequenz:**
```bash
# 1. Mount testen
sudo mount /home/carst/n_drive
df -h | grep n_drive

# 2. Zugriff testen  
ls -la /home/carst/n_drive/AUFNAHMEN/

# 3. Uploader testen
source venv/bin/activate
python uploader.py --debug --preview
```

## 🔐 Sicherheitshinweise

1. **Credentials-Datei schützen:**
   ```bash
   sudo chmod 600 /etc/smb-credentials  # Nur root kann lesen
   ```

2. **Netzwerk-Sicherheit:**
   - Verwenden Sie sichere Passwörter
   - SMBv3.0 ist sicherer als ältere Versionen
   - Erwägen Sie VPN für externe Zugriffe

3. **Backup der Konfiguration:**
   ```bash
   # Konfiguration sichern
   sudo cp /etc/fstab /etc/fstab.backup
   sudo cp /etc/smb-credentials /etc/smb-credentials.backup
   ```

## 🚀 Performance-Tipps

```bash
# Für bessere Performance in fstab:
//IP/SHARE /mount/point cifs credentials=/etc/smb-credentials,uid=1001,gid=1001,vers=3.0,cache=strict,rsize=1048576,wsize=1048576,file_mode=0755,dir_mode=0755,noperm 0 0
```

**Parameter für Performance:**
- `cache=strict`: Aktiviert Caching
- `rsize=1048576`: 1MB Lese-Blöcke
- `wsize=1048576`: 1MB Schreib-Blöcke

---

**Mit dieser Konfiguration kann der YouTube Uploader nahtlos auf Netzlaufwerke zugreifen! 🎮✨**
