@echo off
setlocal enabledelayedexpansion

for %%f in (*.mp4) do (
    REM Ueberspringe Dateien die bereits ein Praefix haben
    echo %%f | findstr /B "merged_ unmergable_ onlydesktop_ onlymic_" >nul
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
            echo Erstelle 3 Versionen aus %%f...
            
            REM 1. MERGED VERSION (wie bisher)
            echo [1/3] Erstelle merged Version...
            ffmpeg -i "%%f" -filter_complex "[0:a:0]loudnorm=I=-16:TP=-1.5:LRA=11,volume=0.15[a1];[0:a:1]dynaudnorm=f=150:g=31:p=0.95:m=15,loudnorm=I=-16:TP=-1.5:LRA=11[a2];[a1][a2]amerge=inputs=2[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -ac 2 "merged_%%f"
            
            if !errorlevel! equ 0 (
                echo ERFOLG: Merged Version erstellt
                
                REM Kopiere Zeitstempel fuer merged Version
                echo Kopiere Zeitstempel fuer merged Version...
                powershell -Command "& {$original = Get-Item '%%f'; $merged = Get-Item 'merged_%%f'; $merged.CreationTime = $original.CreationTime; $merged.LastWriteTime = $original.LastWriteTime; $merged.LastAccessTime = $original.LastAccessTime}"
            ) else (
                echo FEHLER beim Erstellen der merged Version von %%f
            )
            
            REM 2. ONLY DESKTOP VERSION (nur erste Audiospur - Game/Desktop Audio - mit minimalem Video)
            echo [2/3] Erstelle onlydesktop Version...
            ffmpeg -i "%%f" -f lavfi -i color=black:size=640x360:rate=1 -map 1:v -map 0:a:0 -c:v libx264 -preset ultrafast -crf 51 -pix_fmt yuv420p -r 1 -c:a aac -shortest "onlydesktop_%%f"
            
            if !errorlevel! equ 0 (
                echo ERFOLG: OnlyDesktop Version erstellt
                
                REM Kopiere Zeitstempel fuer onlydesktop Version
                echo Kopiere Zeitstempel fuer onlydesktop Version...
                powershell -Command "& {$original = Get-Item '%%f'; $desktop = Get-Item 'onlydesktop_%%f'; $desktop.CreationTime = $original.CreationTime; $desktop.LastWriteTime = $original.LastWriteTime; $desktop.LastAccessTime = $original.LastAccessTime}"
            ) else (
                echo FEHLER beim Erstellen der onlydesktop Version von %%f
            )
            
            REM 3. ONLY MIC VERSION (nur zweite Audiospur - Mikrofon Audio - mit minimalem Video)
            echo [3/3] Erstelle onlymic Version...
            ffmpeg -i "%%f" -f lavfi -i color=black:size=640x360:rate=1 -map 1:v -map 0:a:1 -c:v libx264 -preset ultrafast -crf 51 -pix_fmt yuv420p -r 1 -c:a aac -shortest "onlymic_%%f"
            
            if !errorlevel! equ 0 (
                echo ERFOLG: OnlyMic Version erstellt
                
                REM Kopiere Zeitstempel fuer onlymic Version
                echo Kopiere Zeitstempel fuer onlymic Version...
                powershell -Command "& {$original = Get-Item '%%f'; $mic = Get-Item 'onlymic_%%f'; $mic.CreationTime = $original.CreationTime; $mic.LastWriteTime = $original.LastWriteTime; $mic.LastAccessTime = $original.LastAccessTime}"
            ) else (
                echo FEHLER beim Erstellen der onlymic Version von %%f
            )
            
            echo ALLE 3 VERSIONEN FERTIG fuer %%f
            
            REM Optional: Original-Datei loeschen
            REM del "%%f"
        ) else (
            echo WARNUNG: Nur !audio_count! Audiospur^(en^) gefunden - Datei wird umbenannt
            ren "%%f" "unmergable_%%f"
        )
    )
    echo ========================================
)

echo.
echo Verarbeitung abgeschlossen!
echo - Dateien mit "merged_" = beide Audiospuren kombiniert
echo - Dateien mit "onlydesktop_" = nur Game/Desktop Audio
echo - Dateien mit "onlymic_" = nur Mikrofon Audio  
echo - Dateien mit "unmergable_" = nur eine Audiospur gefunden
pause
