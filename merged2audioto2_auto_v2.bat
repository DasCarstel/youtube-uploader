@echo off
setlocal enabledelayedexpansion

for %%f in (*.mp4) do (
    echo Analysiere: %%f
    
    REM Zaehle die Anzahl der Audiospuren
    set audio_count=0
    for /f "tokens=*" %%a in ('ffmpeg -i "%%f" 2^>^&1 ^| findstr /c:"Audio:"') do (
        set /a audio_count+=1
    )
    
    echo Gefundene Audiospuren: !audio_count!
    
    if !audio_count! geq 2 (
        echo Merge wird durchgefuehrt...
        ffmpeg -i "%%f" -filter_complex "[0:a:0]loudnorm=I=-16:TP=-1.5:LRA=11,volume=0.25[a1];[0:a:1]loudnorm=I=-16:TP=-1.5:LRA=11[a2];[a1][a2]amerge=inputs=2[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -ac 2 "merged_%%f"
        
        if !errorlevel! equ 0 (
            echo ERFOLG: Merge abgeschlossen
        ) else (
            echo FEHLER beim Mergen
        )
    ) else (
        echo WARNUNG: Nur !audio_count! Audiospur^(en^) gefunden - Datei wird umbenannt
        ren "%%f" "unmergable_%%f"
    )
    echo ----------------------------------------
)
pause
