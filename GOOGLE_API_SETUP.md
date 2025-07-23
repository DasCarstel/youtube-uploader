# YouTube Data API Setup Guide

## 🔑 Google Cloud Console Setup

### Schritt 1: Google Cloud Projekt erstellen

1. Gehen Sie zur [Google Cloud Console](https://console.cloud.google.com/)
2. Melden Sie sich mit Ihrem Google-Konto an
3. Klicken Sie auf "Projekt auswählen" (oben links)
4. Klicken Sie auf "NEUES PROJEKT"
5. Geben Sie einen Projektnamen ein (z.B. "YouTube Gaming Uploader")
6. Klicken Sie auf "ERSTELLEN"

### Schritt 2: YouTube Data API v3 aktivieren

1. Stellen Sie sicher, dass Ihr neues Projekt ausgewählt ist
2. Gehen Sie zu "APIs & Services" > "Library" (im Seitenmenü)
3. Suchen Sie nach "YouTube Data API v3"
4. Klicken Sie auf "YouTube Data API v3"
5. Klicken Sie auf "AKTIVIEREN"

### Schritt 3: OAuth2 Credentials erstellen

1. Gehen Sie zu "APIs & Services" > "Credentials"
2. Klicken Sie auf "CREATE CREDENTIALS" > "OAuth client ID"

**Beim ersten Mal:**
- Sie werden aufgefordert, einen "OAuth consent screen" zu konfigurieren
- Wählen Sie "External" (es sei denn, Sie haben eine Google Workspace Organisation)
- Füllen Sie die erforderlichen Felder aus:
  - App name: "YouTube Gaming Uploader"
  - User support email: Ihre E-Mail
  - Developer contact information: Ihre E-Mail
- Klicken Sie auf "SPEICHERN UND FORTFAHREN"
- Bei "Scopes": Klicken Sie einfach auf "SPEICHERN UND FORTFAHREN"
- Bei "Test users": Fügen Sie Ihre eigene E-Mail-Adresse hinzu
- Überprüfen Sie die Zusammenfassung und klicken Sie auf "ZURÜCK ZUM DASHBOARD"

**OAuth Client ID erstellen:**
1. Gehen Sie zurück zu "Credentials"
2. Klicken Sie auf "CREATE CREDENTIALS" > "OAuth client ID"
3. Wählen Sie "Desktop application"
4. Geben Sie einen Namen ein (z.B. "YouTube Uploader Desktop")
5. Klicken Sie auf "CREATE"

### Schritt 4: Credentials herunterladen

1. Nach der Erstellung erscheint ein Dialog mit Ihren Credentials
2. Klicken Sie auf "DOWNLOAD JSON"
3. Speichern Sie die Datei als `credentials.json` in Ihrem Projektverzeichnis
   ```
   /home/carst/youtube-uploader/credentials.json
   ```

## 🔒 Wichtige Sicherheitshinweise

- **NIEMALS** die `credentials.json` Datei in ein öffentliches Repository hochladen
- Die Datei ist bereits in `.gitignore` ausgeschlossen
- Die `token.json` (wird automatisch erstellt) enthält Ihre Zugriffstoken und sollte ebenfalls geheim bleiben

## 🎯 Erste Authentifizierung

Beim ersten Start des Uploaders:

```bash
source venv/bin/activate
python uploader.py --preview  # Testet jetzt auch die Authentifizierung
```

1. Ein Browser-Fenster öffnet sich automatisch
2. Melden Sie sich mit Ihrem Google-Konto an
3. Bestätigen Sie die Berechtigungen für die App:
   - **YouTube Data API v3 Upload**: Zum Hochladen von Videos
   - **YouTube Data API v3 Playlists**: Zum Verwalten von Playlists
4. Der Browser zeigt "Die Authentifizierung ist abgeschlossen"
5. Eine `token.json` Datei wird automatisch erstellt

**Hinweis:** Die Multi-Playlist-Funktionalität erfordert erweiterte Playlist-Berechtigungen.

## ⚠️ Troubleshooting

### Problem: "credentials.json nicht gefunden"
- Stellen Sie sicher, dass die Datei im richtigen Verzeichnis liegt
- Überprüfen Sie den Dateinamen (muss exakt `credentials.json` sein)

### Problem: "redirect_uri_mismatch"
- Stellen Sie sicher, dass Sie "Desktop application" gewählt haben
- Nicht "Web application"

### Problem: "Insufficient Permission" oder "Insufficient authentication scopes"
- Die App hat nicht die nötigen Berechtigungen für alle Features
- **Lösung:** Löschen Sie `token.json` und authentifizieren Sie sich neu
- Akzeptieren Sie **alle** Berechtigungen im Browser-Dialog
- Der neue Scope umfasst sowohl Video-Upload als auch Playlist-Management

### Problem: "access_denied"
- Überprüfen Sie, ob Ihr Google-Konto als "Test user" hinzugefügt wurde
- Versuchen Sie es mit dem Google-Konto, das das Projekt erstellt hat

### Problem: "The app is blocked" oder "Zugriff blockiert"
- Ihre App ist noch im "Testing" Modus
- **Lösung 1:** Gehen Sie zu "OAuth consent screen" > "Test users" > "ADD USERS" und fügen Sie Ihre E-Mail hinzu
- **Lösung 2:** Klicken Sie auf "PUBLISH APP" um die App öffentlich zu machen (empfohlen für persönliche Nutzung)
- **Lösung 3:** Warten Sie 1-2 Stunden nach dem Hinzufügen als Test-User

## 🏷️ YouTube API Quotas

- Die YouTube Data API hat tägliche Limits
- Standard-Quota: 10.000 Einheiten pro Tag
- Ein Video-Upload verbraucht ca. 1600 Einheiten
- Sie können also etwa 6 Videos pro Tag hochladen
- Für mehr Uploads müssen Sie eine Quota-Erhöhung beantragen

## 📊 Quota-Verbrauch der App

- Video-Upload: ~1600 Einheiten
- Playlist erstellen: 50 Einheiten
- Video zu Playlist hinzufügen: 50 Einheiten
- Playlist auflisten: 1 Einheit

## 🔄 Token erneuern

- Der `token.json` wird automatisch erneuert wenn möglich
- Falls Probleme auftreten, löschen Sie `token.json` und authentifizieren Sie sich neu
- Die Authentifizierung ist für längere Zeit gültig (normalerweise Monate)

## 📞 Support

Bei Problemen mit der API-Einrichtung:
1. Überprüfen Sie die Google Cloud Console Logs
2. Stellen Sie sicher, dass alle Schritte befolgt wurden
3. Verwenden Sie `--debug` für detaillierte Fehlermeldungen
