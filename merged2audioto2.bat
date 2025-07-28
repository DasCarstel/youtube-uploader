@echo off
setlocal enabledelayedexpansion

for %%f in (*.mp4) do (
    REM Ueberspringe Dateien die bereits ein Praefix haben
    echo %%f | findstr /B "merged_ unmergable_" >nul
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
            echo Merge wird durchgefuehrt...
            ffmpeg -i "%%f" -filter_complex "[0:a:0]loudnorm=I=-16:TP=-1.5:LRA=11,volume=0.25[a1];[0:a:1]dynaudnorm=f=150:g=31:p=0.95:m=15,loudnorm=I=-16:TP=-1.5:LRA=11[a2];[a1][a2]amerge=inputs=2[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -ac 2 "merged_%%f"
            
            if !errorlevel! equ 0 (
                echo ERFOLG: Merge abgeschlossen fuer %%f
                
                REM Kopiere Erstelldatum und Aenderungsdatum von Original auf gemergte Datei
                echo Kopiere Zeitstempel von Original auf gemergte Datei...
                for %%i in ("%%f") do (
                    set "original_date=%%~ti"
                    powershell -Command "& {$original = Get-Item '%%f'; $merged = Get-Item 'merged_%%f'; $merged.CreationTime = $original.CreationTime; $merged.LastWriteTime = $original.LastWriteTime; $merged.LastAccessTime = $original.LastAccessTime}"
                )
                echo Zeitstempel erfolgreich kopiert
                
                REM Optional: Original-Datei loeschen
                REM del "%%f"
            ) else (
                echo FEHLER beim Mergen von %%f
            )
        ) else (
            echo WARNUNG: Nur !audio_count! Audiospur^(en^) gefunden - Datei wird umbenannt
            ren "%%f" "unmergable_%%f"
        )
    )
    echo ----------------------------------------
)

echo.
echo Verarbeitung abgeschlossen!
echo - Dateien mit "merged_" = erfolgreich verarbeitet
echo - Dateien mit "unmergable_" = nur eine Audiospur gefunden
pause
