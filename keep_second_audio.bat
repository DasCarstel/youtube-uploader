@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Zweiten Audiokanal behalten - Script
echo ========================================
echo.
echo Dieses Script:
echo - Behaelt nur den zweiten Audiokanal (meist Game-Audio)
echo - Entfernt den ersten Audiokanal (meist Mikrofon)
echo - Praefix: "gameonly_" fuer verarbeitete Dateien
echo.

for %%f in (*.mp4) do (
    REM Ueberspringe Dateien die bereits ein Praefix haben
    echo %%f | findstr /B "gameonly_ merged_ unmergable_ uploaded_" >nul
    if !errorlevel! equ 0 (
        echo UEBERSPRINGE: %%f wurde bereits verarbeitet
    ) else (
        echo Analysiere: %%f
        
        REM Zaehle die Anzahl der Audiospuren
        set audio_count=0
        for /f "tokens=*" %%a in ('ffmpeg -i "%%f" 2^>^&1 ^| findstr /c:"Audio:"') do (
            set /a audio_count+=1
        )
        
        echo Gefundene Audiospuren: !audio_count!
        
        if !audio_count! geq 2 (
            echo Extrahiere zweiten Audiokanal...
            ffmpeg -i "%%f" -map 0:v -map 0:a:1 -c:v copy -c:a aac "gameonly_%%f"
            
            if !errorlevel! equ 0 (
                echo ERFOLG: Zweiter Audiokanal extrahiert fuer %%f
                
                REM Kopiere Erstelldatum und Aenderungsdatum von Original auf neue Datei
                echo Kopiere Zeitstempel von Original auf neue Datei...
                for %%i in ("%%f") do (
                    set "original_date=%%~ti"
                    powershell -Command "& {$original = Get-Item '%%f'; $processed = Get-Item 'gameonly_%%f'; $processed.CreationTime = $original.CreationTime; $processed.LastWriteTime = $original.LastWriteTime; $processed.LastAccessTime = $original.LastAccessTime}"
                )
                echo Zeitstempel erfolgreich kopiert
                
                REM Optional: Original-Datei loeschen
                REM del "%%f"
            ) else (
                echo FEHLER beim Extrahieren des zweiten Audiokanals von %%f
            )
        ) else (
            echo WARNUNG: Nur !audio_count! Audiospur^(en^) gefunden - kann zweiten Kanal nicht extrahieren
            echo Datei wird uebersprungen: %%f
        )
    )
    echo ----------------------------------------
)

echo.
echo Verarbeitung abgeschlossen!
echo.
echo Ergebnis:
echo - Dateien mit "gameonly_" = Nur zweiter Audiokanal ^(Game-Audio^)
echo - Original-Dateien bleiben unveraendert
echo.
echo HINWEIS: 
echo - Der erste Audiokanal ^(meist Mikrofon^) wurde entfernt
echo - Der zweite Audiokanal ^(meist Game-Audio^) wurde beibehalten
echo - Video-Stream wurde unveraendert kopiert ^(schnell^)
echo.
pause
