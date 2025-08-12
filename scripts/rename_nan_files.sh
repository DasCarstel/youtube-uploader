#!/bin/bash
# Skript zum Umbenennen von NaN-Dateien nach ihrem Ordnernamen
# Usage: ./rename_nan_files.sh <ROOT_PATH>

set -e

ROOT_PATH="${1:-.}"

echo "🔍 Suche nach NaN-Dateien in: $ROOT_PATH"

#!/bin/bash
# Skript zum Umbenennen von fehlerhaften Dateien nach ihrem Ordnernamen
# Usage: ./rename_nan_files.sh <ROOT_PATH>

set -e

ROOT_PATH="${1:-.}"

echo "🔍 Suche nach fehlerhaften Dateien in: $ROOT_PATH"

# Finde alle Dateien mit fehlerhaften Patterns (NaN, undefined, error, etc.)
find "$ROOT_PATH" -type f \( -name "*NaN*" -o -name "*undefined*" -o -name "*error*" -o -name "*null*" \) | while read -r file; do
    # Extrahiere den Ordnernamen (letzter Teil des Pfads vor der Datei)
    dir_path=$(dirname "$file")
    folder_name=$(basename "$dir_path")
    
    # Extrahiere die Dateiendung
    extension="${file##*.}"
    
    # Erstelle neuen Dateinamen: Ordnername + .extension
    new_filename="${folder_name}.${extension}"
    new_filepath="${dir_path}/${new_filename}"
    
    echo "📁 Gefunden: $(basename "$file")"
    echo "   📂 Ordner: $folder_name"
    echo "   🔄 Umbenennen zu: $new_filename"
    
    # Prüfe ob Zieldatei bereits existiert
    if [ -f "$new_filepath" ]; then
        echo "   ⚠️  Warnung: Datei '$new_filename' existiert bereits, füge Suffix hinzu..."
        counter=1
        while [ -f "${dir_path}/${folder_name}_${counter}.${extension}" ]; do
            counter=$((counter + 1))
        done
        new_filename="${folder_name}_${counter}.${extension}"
        new_filepath="${dir_path}/${new_filename}"
        echo "   🔄 Neuer Name: $new_filename"
    fi
    
    # Benenne Datei um
    mv "$file" "$new_filepath"
    echo "   ✅ Erfolgreich umbenannt!"
    echo ""
done

echo "✅ Alle fehlerhaften Dateien wurden verarbeitet."

echo "✅ Alle NaN-Dateien wurden verarbeitet."
