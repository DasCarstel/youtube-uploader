#!/bin/bash
# Skript zum Löschen aller Dateien <1MB in Blattordnern (Leaf-Folders)
# Usage: ./delete_small_files_in_leaf_folders.sh <ROOT_PATH>

set -e

ROOT_PATH="${1:-.}"

echo "🔍 Suche nach Blattordnern in: $ROOT_PATH"

# Finde alle Blattordner (Ordner ohne Unterordner)
find "$ROOT_PATH" -type d | while read -r dir; do
    # Prüfe ob der Ordner ein Blattordner ist (keine Unterordner)
    if [ "$(find "$dir" -mindepth 1 -type d | wc -l)" -eq 0 ]; then
        echo "📁 Blattordner gefunden: $dir"
        # Zeige alle Dateien <1MB in diesem Blattordner
        find "$dir" -type f -size -1024k -print | while read -r file; do
            echo "   🗑️ Lösche: $file"
        done
        # Lösche rekursiv alle Dateien <1MB in diesem Blattordner
        find "$dir" -type f -size -1024k -delete
    fi
done

echo "✅ Alle Dateien <1MB in Blattordnern wurden gelöscht."