#!/bin/bash
# YouTube Gaming Video Uploader - venv Aktivierungsscript
# Führen Sie dieses Script aus, um die virtuelle Umgebung zu aktivieren

echo "🐍 Aktiviere virtuelle Python-Umgebung..."

# Überprüfe ob venv existiert
if [ ! -d "venv" ]; then
    echo "❌ Virtuelle Umgebung nicht gefunden!"
    echo "💡 Erstellen Sie zuerst eine venv mit: python3 -m venv venv"
    echo "💡 Installieren Sie dann die Abhängigkeiten: source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Aktiviere venv
source venv/bin/activate

echo "✅ Virtuelle Umgebung aktiviert!"
echo "🎮 Sie können jetzt den YouTube Uploader verwenden:"
echo "   python uploader.py --preview    # Vorschau"
echo "   python uploader.py              # Upload starten"
echo ""
echo "⚠️  Um die venv zu deaktivieren, geben Sie 'deactivate' ein"

# Starte eine neue Shell mit aktivierter venv
exec "$SHELL"
