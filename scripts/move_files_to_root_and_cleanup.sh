#!/bin/bash
# Skript zum Verschieben aller Dateien in den Root-Pfad und Löschen leerer Ordner
# Usage: ./move_files_to_root_and_cleanup.sh <ROOT_PATH>

set -e

ROOT_PATH="${1:-.}"

if [ ! -d "$ROOT_PATH" ]; then
    echo "❌ Fehler: Pfad '$ROOT_PATH' existiert nicht!"
    exit 1
fi

echo "🔍 Verarbeite Verzeichnis: $ROOT_PATH"
echo "📂 Verschiebe alle Dateien in den Root-Pfad und entferne leere Ordner..."

# Zähler für Statistiken
moved_files=0
deleted_dirs=0

# Finde alle Dateien (nicht in Root-Verzeichnis) und verschiebe sie
find "$ROOT_PATH" -mindepth 2 -type f | while read -r file; do
    filename=$(basename "$file")
    target_path="$ROOT_PATH/$filename"
    
    echo "📄 Gefunden: $file"
    
    # Prüfe ob Zieldatei bereits existiert
    if [ -f "$target_path" ]; then
        echo "   ⚠️  Warnung: '$filename' existiert bereits im Root-Pfad"
        
        # Erstelle eindeutigen Namen mit Zeitstempel
        name_without_ext="${filename%.*}"
        extension="${filename##*.}"
        timestamp=$(date +"%Y%m%d_%H%M%S")
        
        if [ "$name_without_ext" = "$filename" ]; then
            # Keine Dateiendung
            new_filename="${filename}_${timestamp}"
        else
            # Mit Dateiendung
            new_filename="${name_without_ext}_${timestamp}.${extension}"
        fi
        
        target_path="$ROOT_PATH/$new_filename"
        echo "   🔄 Neuer Name: $new_filename"
    fi
    
    # Verschiebe Datei
    mv "$file" "$target_path"
    echo "   ✅ Verschoben nach: $(basename "$target_path")"
    moved_files=$((moved_files + 1))
done

echo ""
echo "🗂️  Entferne leere Ordner..."

# Entferne leere Ordner (mehrfach, da sich Hierarchien auflösen)
while true; do
    empty_dirs=$(find "$ROOT_PATH" -mindepth 1 -type d -empty)
    
    if [ -z "$empty_dirs" ]; then
        break
    fi
    
    echo "$empty_dirs" | while read -r empty_dir; do
        echo "🗑️  Lösche leeren Ordner: $(basename "$empty_dir")"
        rmdir "$empty_dir"
        deleted_dirs=$((deleted_dirs + 1))
    done
done

echo ""
echo "✅ Verarbeitung abgeschlossen!"
echo "📊 Statistik:"
echo "   📄 Verschobene Dateien: $moved_files"
echo "   🗂️  Gelöschte leere Ordner: $deleted_dirs"
