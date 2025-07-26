#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Gaming Video Uploader
================================

Ein automatisierter Uploader für Gaming-Videos zu YouTube mit intelligenter 
Playlist-Verwaltung und Datei-Organisation basierend auf der YouTube Data API v3.

Author: Carsten
Version: 2.0
Date: Juli 2025
"""

import os
import sys
import re
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import argparse
import json

# Google API imports
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload

# Utility imports
from dotenv import load_dotenv
from colorama import init, Fore, Back, Style
from tqdm import tqdm
import click

# Initialize colorama for colored terminal output
init(autoreset=True)

class YouTubeUploader:
    """Hauptklasse für den YouTube Gaming Video Uploader"""
    
    # Unterstützte Video-Formate
    SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    
    # Video-Präfixe
    VIDEO_PREFIXES = ['merged_', 'unmergable_']
    UPLOADED_PREFIX = 'uploaded_'
    
    # Haupt-Ordner
    MAIN_FOLDERS = ['SPIEL AUFNAHMEN', 'WITZIGE MOMENTE', 'GESCHNITTE MOMENTE']
    
    # YouTube API Scopes
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube'
    ]
    
    def __init__(self, recordings_path: Optional[str] = None, debug_mode: bool = False):
        """Initialisierung des YouTube Uploaders"""
        self.debug_mode = debug_mode
        self.recordings_path = recordings_path or os.getenv('RECORDINGS_PATH')
        self.default_visibility = os.getenv('DEFAULT_VISIBILITY', 'unlisted').lower()
        
        # YouTube API Service
        self.youtube_service = None
        
        # Playlist-Cache zur Quota-Optimierung
        self.playlist_cache = {}
        self.playlist_cache_loaded = False
        
        # Statistiken
        self.stats = {
            'found_videos': 0,
            'uploaded_videos': 0,
            'failed_uploads': 0,
            'merged_videos': 0,
            'unmergable_videos': 0
        }
        
        self._print_header()
        
    def _print_header(self):
        """Druckt den Header mit Projektinformationen"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🎮 YouTube Gaming Video Uploader v2.0 (Python + YouTube Data API)")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}📂 Aufnahmen-Pfad: {self.recordings_path}")
        print(f"{Fore.YELLOW}👁️  Standard-Sichtbarkeit: {self.default_visibility.upper()}")
        print(f"{Fore.YELLOW}🐛 Debug-Modus: {'AN' if self.debug_mode else 'AUS'}")
        print(f"{Fore.CYAN}🔧 Quota-Optimierung: Aktiviert (Playlist-Caching)")
        print(f"{Fore.CYAN}{'='*70}\n")
        
    def _print_quota_info(self, video_count: int):
        """Zeigt Quota-Verbrauchsinformationen"""
        print(f"\n{Fore.BLUE}📊 YOUTUBE DATA API QUOTA-INFORMATION")
        print(f"{Fore.BLUE}{'='*50}")
        
        # Schätze Quota-Verbrauch
        video_upload_quota = video_count * 1600  # ~1600 Punkte pro Video
        playlist_list_quota = 1  # Einmalig durch Cache
        playlist_create_quota = 50 * 3  # Durchschnittlich 3 neue Playlists
        playlist_add_quota = video_count * 50 * 3  # Pro Video zu 3 Playlists
        
        total_estimated_quota = video_upload_quota + playlist_list_quota + playlist_create_quota + playlist_add_quota
        
        print(f"{Fore.YELLOW}📤 Video Uploads: {video_count} × 1600 = {video_upload_quota:,} Punkte")
        print(f"{Fore.YELLOW}📋 Playlist-Liste: 1 × 1 = {playlist_list_quota} Punkte (gecacht)")
        print(f"{Fore.YELLOW}➕ Playlist-Erstellung: ~{playlist_create_quota} Punkte")
        print(f"{Fore.YELLOW}📝 Playlist-Zuordnungen: {video_count} × 150 = {playlist_add_quota:,} Punkte")
        print(f"{Fore.CYAN}📊 Geschätzter Gesamt-Verbrauch: {total_estimated_quota:,} Punkte")
        
        if total_estimated_quota > 10000:
            print(f"{Fore.RED}⚠️  WARNUNG: Geschätzter Verbrauch überschreitet Standard-Quota (10.000 Punkte)")
            print(f"{Fore.YELLOW}💡 Empfehlung: Quota-Erhöhung beantragen oder weniger Videos uploaden")
        else:
            print(f"{Fore.GREEN}✅ Quota-Verbrauch im normalen Bereich")
            
        print(f"{Fore.BLUE}{'='*50}\n")
        
    def authenticate_youtube(self) -> bool:
        """Authentifizierung mit der YouTube Data API"""
        try:
            creds = None
            token_path = 'token.json'
            credentials_path = 'credentials.json'
            
            # Lade bestehende Token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
            # Wenn keine gültigen Credentials vorhanden sind, führe OAuth-Flow aus
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(credentials_path):
                        print(f"{Fore.RED}❌ Fehler: credentials.json nicht gefunden!")
                        print(f"{Fore.YELLOW}💡 Bitte erstellen Sie eine OAuth2-Client-ID in der Google Cloud Console:")
                        print(f"{Fore.YELLOW}   1. Gehen Sie zu https://console.cloud.google.com/")
                        print(f"{Fore.YELLOW}   2. Erstellen Sie ein neues Projekt oder wählen Sie ein existierendes")
                        print(f"{Fore.YELLOW}   3. Aktivieren Sie die YouTube Data API v3")
                        print(f"{Fore.YELLOW}   4. Erstellen Sie OAuth2-Credentials")
                        print(f"{Fore.YELLOW}   5. Laden Sie die JSON-Datei herunter und benennen Sie sie 'credentials.json'")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Speichere die Credentials für zukünftige Nutzung
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            # Erstelle YouTube API Service
            self.youtube_service = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
            
            print(f"{Fore.GREEN}✅ YouTube-Authentifizierung erfolgreich!")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Fehler bei der YouTube-Authentifizierung: {str(e)}")
            return False
    
    def _load_playlist_cache(self):
        """Lädt alle existierenden Playlists einmalig in den Cache (Quota-Optimierung)"""
        if self.playlist_cache_loaded or not self.youtube_service:
            return
            
        try:
            if self.debug_mode:
                print(f"{Fore.CYAN}📋 Lade Playlist-Cache (einmalig für Quota-Optimierung)...")
                
            request = self.youtube_service.playlists().list(
                part='snippet',
                mine=True,
                maxResults=50
            )
            
            response = request.execute()
            
            # Speichere alle Playlists im Cache
            for playlist in response.get('items', []):
                playlist_name = playlist['snippet']['title']
                playlist_id = playlist['id']
                self.playlist_cache[playlist_name] = playlist_id
                
            self.playlist_cache_loaded = True
            
            if self.debug_mode:
                print(f"{Fore.GREEN}✅ {len(self.playlist_cache)} Playlist(s) im Cache geladen")
                
        except Exception as e:
            if self.debug_mode:
                print(f"{Fore.YELLOW}⚠️  Warnung: Playlist-Cache konnte nicht geladen werden: {str(e)}")
            self.playlist_cache_loaded = True  # Verhindere weitere Versuche
    
    def find_videos(self) -> List[Dict]:
        """Sucht nach Videos mit den spezifizierten Präfixen"""
        videos = []
        
        if not self.recordings_path or not os.path.exists(self.recordings_path):
            print(f"{Fore.RED}❌ Aufnahmen-Pfad nicht gefunden: {self.recordings_path}")
            return videos
            
        print(f"{Fore.BLUE}🔍 Durchsuche Verzeichnis: {self.recordings_path}")
        
        for main_folder_name in self.MAIN_FOLDERS:
            if not self.recordings_path:
                continue
                
            main_folder_path = Path(self.recordings_path) / main_folder_name
            
            if not main_folder_path.exists():
                if self.debug_mode:
                    print(f"{Fore.YELLOW}⚠️  Ordner nicht gefunden: {main_folder_path}")
                continue
                
            print(f"{Fore.BLUE}📂 Durchsuche: {main_folder_name}")
            folder_videos = self._scan_folder_recursive(main_folder_path, main_folder_name)
            videos.extend(folder_videos)
            
            if folder_videos:
                print(f"{Fore.GREEN}   ✅ {len(folder_videos)} Video(s) gefunden in '{main_folder_name}'")
        
        self.stats['found_videos'] = len(videos)
        self._categorize_videos(videos)
        
        return videos
    
    def _scan_folder_recursive(self, folder_path: Path, main_folder: str, current_path: Optional[List[str]] = None) -> List[Dict]:
        """Rekursive Suche nach Videos in Ordnern"""
        if current_path is None:
            current_path = [main_folder]
            
        videos = []
        
        try:
            for item in folder_path.iterdir():
                if item.is_file() and self._is_video_file(item):
                    video_info = self._analyze_video_file(item, current_path.copy())
                    if video_info:
                        videos.append(video_info)
                        
                elif item.is_dir():
                    # Prüfe ob der Ordner selbst ein Upload-Ordner ist (mit merged_ oder unmergable_ Präfix)
                    if self._is_upload_folder(item):
                        # Durchsuche diesen Ordner und alle Videos darin sollen hochgeladen werden
                        folder_videos = self._scan_upload_folder(item, main_folder, current_path.copy())
                        videos.extend(folder_videos)
                    else:
                        # Normale rekursive Suche in Unterordner
                        sub_path = current_path + [item.name]
                        sub_videos = self._scan_folder_recursive(item, main_folder, sub_path)
                        videos.extend(sub_videos)
                        
        except PermissionError:
            if self.debug_mode:
                print(f"{Fore.YELLOW}⚠️  Keine Berechtigung für: {folder_path}")
                
        return videos
    
    def _is_upload_folder(self, folder_path: Path) -> bool:
        """Prüft, ob ein Ordner ein Upload-Ordner ist (mit merged_ oder unmergable_ Präfix)"""
        folder_name = folder_path.name
        
        # Prüfe auf Upload-Präfixe in Ordnernamen
        has_upload_prefix = any(folder_name.startswith(prefix) for prefix in self.VIDEO_PREFIXES)
        
        # Überspringe bereits verarbeitete Ordner
        already_processed = folder_name.startswith(self.UPLOADED_PREFIX)
        
        return has_upload_prefix and not already_processed
    
    def _scan_upload_folder(self, folder_path: Path, main_folder: str, current_path: List[str]) -> List[Dict]:
        """Durchsucht einen Upload-Ordner und behandelt alle Videos darin als Upload-bereit"""
        videos = []
        folder_name = folder_path.name
        
        # Bestimme Video-Typ basierend auf Ordner-Präfix
        video_type = 'merged' if folder_name.startswith('merged_') else 'unmergable'
        
        # Entferne Präfix vom Ordnernamen für die Pfad-Struktur
        clean_folder_name = folder_name
        for prefix in self.VIDEO_PREFIXES:
            if folder_name.startswith(prefix):
                clean_folder_name = folder_name[len(prefix):]
                break
        
        # Aktualisiere Pfad-Struktur mit bereinigtem Ordnernamen
        folder_path_structure = current_path + [clean_folder_name]
        
        if self.debug_mode:
            print(f"{Fore.CYAN}🎯 Upload-Ordner gefunden: {folder_name} (Typ: {video_type})")
        
        try:
            # Durchsuche den Upload-Ordner rekursiv nach allen Video-Dateien
            for item in folder_path.rglob('*'):
                if item.is_file() and self._is_supported_video_format(item):
                    # Berechne relative Pfad-Struktur innerhalb des Upload-Ordners
                    relative_path = item.relative_to(folder_path)
                    sub_folders = list(relative_path.parent.parts) if relative_path.parent.parts != ('.',) else []
                    
                    # Erstelle vollständige Pfad-Struktur
                    full_path_structure = folder_path_structure + sub_folders
                    
                    video_info = self._analyze_upload_folder_video(item, full_path_structure, video_type)
                    if video_info:
                        videos.append(video_info)
                        
        except PermissionError:
            if self.debug_mode:
                print(f"{Fore.YELLOW}⚠️  Keine Berechtigung für Upload-Ordner: {folder_path}")
        
        if videos and self.debug_mode:
            print(f"{Fore.GREEN}   📁 {len(videos)} Video(s) in Upload-Ordner '{folder_name}' gefunden")
            
        return videos
    
    def _is_supported_video_format(self, file_path: Path) -> bool:
        """Prüft, ob eine Datei ein unterstütztes Video-Format hat und noch nicht hochgeladen wurde"""
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False
            
        filename = file_path.name
        
        # Überspringe bereits hochgeladene Videos
        already_uploaded = filename.startswith(self.UPLOADED_PREFIX)
        
        return not already_uploaded
    
    def _analyze_upload_folder_video(self, file_path: Path, folder_structure: List[str], video_type: str) -> Optional[Dict]:
        """Analysiert ein Video aus einem Upload-Ordner"""
        try:
            filename = file_path.name
            
            # Verwende Dateinamen als Titel (ohne Dateiendung)
            title = file_path.stem
            
            # Bereinige Titel (ersetze Unterstriche durch Leerzeichen und behebe Encoding-Probleme)
            title = title.replace('_', ' ').strip()
            
            # Verwende die gleichen Encoding-Fixes wie bei normalen Videos
            # Behebe häufige Encoding-Probleme
            try:
                if any(ord(c) > 127 and ord(c) < 256 for c in title):
                    title_bytes = title.encode('latin1', errors='ignore')
                    title = title_bytes.decode('utf-8', errors='replace')
            except:
                pass
            
            # Zusätzliche spezifische Fixes für häufige Probleme
            encoding_fixes = {
                'WINDMÜLE': 'WINDMÜHLE',
                'MÜHLE': 'MÜHLE',
                'MÜLE': 'MÜHLE',
                '�': 'Ü',
                '?': 'Ü',
                'M�LE': 'MÜHLE',
                'M�HLE': 'MÜHLE', 
                'M?LE': 'MÜHLE',
                'M?HLE': 'MÜHLE',
                'WINDM�LE': 'WINDMÜHLE',
                'WINDM?LE': 'WINDMÜHLE',
                'H�NGT': 'HÄNGT',
                'H?NGT': 'HÄNGT',
                '\\udcc4': 'Ä',
                '\\udcdc': 'Ü',
                '\\udcf6': 'ö',
                '\\udce4': 'ä',
                '\\udcfc': 'ü',
                '\\udcdf': 'ß',
                'H\\udcc4NGT': 'HÄNGT',
                'VIEH H\\udcc4NGT': 'VIEH HÄNGT',
                'M\\udcdcLE': 'MÜHLE',
                'WINDM\\udcdcLE': 'WINDMÜHLE'
            }
            
            for broken, fixed in encoding_fixes.items():
                title = title.replace(broken, fixed)
            
            # Bestimme Aufnahmedatum
            try:
                record_date = datetime.fromtimestamp(file_path.stat().st_mtime)
            except:
                record_date = datetime.now()
            
            # Bestimme Playlist-Hierarchie
            playlist_info = self._determine_playlists(folder_structure)
            
            video_info = {
                'file_path': str(file_path),
                'filename': filename,
                'title': title,
                'video_type': video_type,  # Vom Ordner bestimmt
                'folder_structure': folder_structure,
                'playlist_info': playlist_info,
                'record_date': record_date,
                'file_size': file_path.stat().st_size,
                'file_size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
                'from_upload_folder': True  # Markierung für Upload-Ordner-Videos
            }
            
            if self.debug_mode:
                print(f"{Fore.CYAN}🔍 Upload-Ordner-Video analysiert: {filename}")
                print(f"   📁 Ordner-Struktur: {' > '.join(folder_structure)}")
                print(f"   🎬 Titel: {title}")
                print(f"   🎯 Typ: {video_type}")
                print(f"   📊 Größe: {video_info['file_size_mb']} MB")
                
            return video_info
            
        except Exception as e:
            if self.debug_mode:
                print(f"{Fore.RED}❌ Fehler beim Analysieren von Upload-Ordner-Video {file_path}: {str(e)}")
            return None
    
    def _is_video_file(self, file_path: Path) -> bool:
        """Prüft, ob eine Datei ein unterstütztes Video ist"""
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False
            
        filename = file_path.name
        
        # Prüfe auf gewünschte Präfixe
        has_prefix = any(filename.startswith(prefix) for prefix in self.VIDEO_PREFIXES)
        
        # Überspringe bereits hochgeladene Videos
        already_uploaded = filename.startswith(self.UPLOADED_PREFIX)
        
        return has_prefix and not already_uploaded
    
    def _analyze_video_file(self, file_path: Path, folder_structure: List[str]) -> Optional[Dict]:
        """Analysiert eine Video-Datei und extrahiert Metadaten"""
        try:
            filename = file_path.name
            
            # Bestimme Video-Typ
            video_type = 'merged' if filename.startswith('merged_') else 'unmergable'
            
            # Extrahiere Titel (entferne Präfix und Dateiendung)
            for prefix in self.VIDEO_PREFIXES:
                if filename.startswith(prefix):
                    title = filename[len(prefix):].rsplit('.', 1)[0]
                    break
            else:
                title = file_path.stem
                
            # Bereinige Titel (ersetze Unterstriche durch Leerzeichen und behebe Encoding-Probleme)
            title = title.replace('_', ' ').strip()
            
            # Behebe häufige Encoding-Probleme
            # Zuerst versuche korrekte UTF-8 Dekodierung
            try:
                # Wenn der Titel bereits problematische Zeichen hat, versuche Dekodierung
                if any(ord(c) > 127 and ord(c) < 256 for c in title):
                    # Versuche als latin1 zu interpretieren und als utf-8 zu dekodieren
                    title_bytes = title.encode('latin1', errors='ignore')
                    title = title_bytes.decode('utf-8', errors='replace')
            except:
                pass
            
            # Zusätzliche spezifische Fixes für häufige Probleme
            encoding_fixes = {
                'WINDMÜLE': 'WINDMÜHLE',  # Korrigiere WINDMÜLE zu WINDMÜHLE
                'MÜHLE': 'MÜHLE',         # Stelle sicher dass MÜHLE korrekt ist
                'MÜLE': 'MÜHLE',          # Korrigiere MÜLE zu MÜHLE
                '�': 'Ü',                # Ersetze Replacement Character
                '?': 'Ü',                # Fallback für Fragezeichen an Ü-Positionen
                'M�LE': 'MÜHLE',
                'M�HLE': 'MÜHLE', 
                'M?LE': 'MÜHLE',
                'M?HLE': 'MÜHLE',
                'WINDM�LE': 'WINDMÜHLE',
                'WINDM?LE': 'WINDMÜHLE',
                'H�NGT': 'HÄNGT',         # Korrigiere H�NGT zu HÄNGT
                'H?NGT': 'HÄNGT',         # Fallback für H?NGT zu HÄNGT
                # Zusätzliche Unicode-Escape-Fixes
                '\\udcc4': 'Ä',          # Unicode escape für Ä
                '\\udcdc': 'Ü',          # Unicode escape für Ü
                '\\udcf6': 'ö',          # Unicode escape für ö
                '\\udce4': 'ä',          # Unicode escape für ä
                '\\udcfc': 'ü',          # Unicode escape für ü
                '\\udcdf': 'ß',          # Unicode escape für ß
                # Weitere problematische Darstellungen
                'H\\udcc4NGT': 'HÄNGT',  # Spezifisch für diesen Fall
                'VIEH H\\udcc4NGT': 'VIEH HÄNGT',
                'M\\udcdcLE': 'MÜHLE',
                'WINDM\\udcdcLE': 'WINDMÜHLE'
            }
            
            for broken, fixed in encoding_fixes.items():
                title = title.replace(broken, fixed)
            
            # Bestimme Aufnahmedatum
            try:
                # Versuche zuerst modification time der Original-Datei
                original_file = file_path.parent / f"original_{title}.{file_path.suffix[1:]}"
                if original_file.exists():
                    record_date = datetime.fromtimestamp(original_file.stat().st_mtime)
                else:
                    record_date = datetime.fromtimestamp(file_path.stat().st_mtime)
            except:
                record_date = datetime.now()
            
            # Bestimme Playlist-Hierarchie
            playlist_info = self._determine_playlists(folder_structure)
            
            video_info = {
                'file_path': str(file_path),
                'filename': filename,
                'title': title,
                'video_type': video_type,
                'folder_structure': folder_structure,
                'playlist_info': playlist_info,
                'record_date': record_date,
                'file_size': file_path.stat().st_size,
                'file_size_mb': round(file_path.stat().st_size / (1024 * 1024), 2)
            }
            
            if self.debug_mode:
                print(f"{Fore.CYAN}🔍 Analysiert: {filename}")
                print(f"   📁 Ordner-Struktur: {' > '.join(folder_structure)}")
                print(f"   🎬 Titel: {title}")
                print(f"   📊 Größe: {video_info['file_size_mb']} MB")
                
            return video_info
            
        except Exception as e:
            if self.debug_mode:
                print(f"{Fore.RED}❌ Fehler beim Analysieren von {file_path}: {str(e)}")
            return None
    
    def _determine_playlists(self, folder_structure: List[str]) -> Dict:
        """Bestimmt die Playlist-Zuordnung basierend auf der Ordner-Struktur"""
        playlist_info = {
            'main_folder': folder_structure[0] if folder_structure else None,
            'game_folder': folder_structure[1] if len(folder_structure) > 1 else None,
            'sub_folders': folder_structure[2:] if len(folder_structure) > 2 else [],
            'all_folders': folder_structure,
            'potential_playlists': [],
            'primary_playlist': None,
            'additional_playlists': []
        }
        
        # Erstelle potentielle Playlists (vom spezifischsten zum allgemeinsten)
        # ALLE Ordner sollen als Playlists verwendet werden (einschließlich Hauptordner)
        if len(folder_structure) > 2:
            # Beispiel: ['SPIEL AUFNAHMEN', 'Star Wars Jedi Fallen Order', 'BUG']
            # Primäre Playlist: BUG (spezifischster)
            playlist_info['primary_playlist'] = folder_structure[-1]
            # Potentielle Playlists: BUG, Star Wars Jedi Fallen Order, SPIEL AUFNAHMEN (rückwärts)
            playlist_info['potential_playlists'] = list(reversed(folder_structure))
            # Zusätzliche Playlists: Star Wars Jedi Fallen Order, SPIEL AUFNAHMEN
            playlist_info['additional_playlists'] = list(reversed(folder_structure[:-1]))
            
        elif len(folder_structure) > 1:
            # Beispiel: ['SPIEL AUFNAHMEN', 'Grand Theft Auto V']
            # Primäre Playlist: Grand Theft Auto V
            playlist_info['primary_playlist'] = folder_structure[1]
            # Potentielle Playlists: Grand Theft Auto V, SPIEL AUFNAHMEN
            playlist_info['potential_playlists'] = list(reversed(folder_structure))
            # Zusätzliche Playlists: SPIEL AUFNAHMEN
            playlist_info['additional_playlists'] = [folder_structure[0]]
            
        else:
            # Nur Hauptordner verfügbar
            playlist_info['primary_playlist'] = folder_structure[0]
            playlist_info['potential_playlists'] = folder_structure
            playlist_info['additional_playlists'] = []
        
        return playlist_info
    
    def _clean_title_for_display(self, title: str) -> str:
        """Bereinigt Titel für saubere Konsolen-Ausgabe"""
        import re
        
        # Entferne Unicode-Escape-Sequenzen wie \udcc4
        clean_title = re.sub(r'\\udc[0-9a-fA-F]{2}', '', title)
        
        # Entferne andere problematische Unicode-Zeichen
        clean_title = re.sub(r'[^\x20-\x7E\u00C0-\u017F]', '', clean_title)
        
        # Cleanup und Normalisierung
        clean_title = clean_title.strip()
        
        return clean_title if clean_title else title
    
    def _categorize_videos(self, videos: List[Dict]):
        """Kategorisiert gefundene Videos für Statistiken"""
        for video in videos:
            if video['video_type'] == 'merged':
                self.stats['merged_videos'] += 1
            else:
                self.stats['unmergable_videos'] += 1
    
    def preview_videos(self, videos: List[Dict]):
        """Zeigt eine Vorschau der gefundenen Videos"""
        if not videos:
            print(f"{Fore.YELLOW}📭 Keine Videos zum Upload gefunden.")
            return
            
        print(f"\n{Fore.GREEN}🎬 {len(videos)} Video(s) bereit für Upload:")
        print(f"{Fore.GREEN}   📹 Merged Videos: {self.stats['merged_videos']}")
        print(f"{Fore.GREEN}   📼 Unmergable Videos: {self.stats['unmergable_videos']}")
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📋 DETAILLIERTE VIDEO-ÜBERSICHT")
        print(f"{Fore.CYAN}{'='*70}")
        
        for i, video in enumerate(videos, 1):
            clean_title = self._clean_title_for_display(video['title'])
            print(f"\n{Fore.WHITE}{i}. {Fore.YELLOW}{clean_title}")
            print(f"   📁 Pfad: {video['folder_structure']}")
            print(f"   📊 Größe: {video['file_size_mb']} MB")
            print(f"   📅 Aufnahme: {video['record_date'].strftime('%d.%m.%Y - %H:%M Uhr')}")
            
            # Playlist-Analyse
            playlist_info = video['playlist_info']
            print(f"\n{Fore.BLUE}🔍 Playlist-Analyse für '{clean_title}':")
            print(f"   - Hauptordner: {playlist_info['main_folder']}")
            if playlist_info['game_folder']:
                print(f"   - Spielordner: {playlist_info['game_folder']}")
            if playlist_info['sub_folders']:
                print(f"   - Alle Unterordner: {playlist_info['sub_folders']}")
            else:
                print(f"   - Alle Unterordner: [keine]")
            print(f"   - Potentielle Playlists: {playlist_info['potential_playlists']}")
            print(f"   - {Fore.GREEN}PRIMÄRE Playlist (für Upload): {playlist_info['primary_playlist']}")
            if playlist_info['additional_playlists']:
                print(f"   - {Fore.CYAN}ZUSÄTZLICHE Playlists: {playlist_info['additional_playlists']}")
            
            print(f"{Fore.CYAN}{'-'*50}")
        
        # Zeige Quota-Information
        self._print_quota_info(len(videos))
    
    def upload_videos(self, videos: List[Dict]) -> bool:
        """Lädt alle Videos zu YouTube hoch"""
        if not videos:
            print(f"{Fore.YELLOW}📭 Keine Videos zum Upload gefunden.")
            return True
            
        if not self.youtube_service:
            print(f"{Fore.RED}❌ YouTube-Service nicht authentifiziert!")
            return False
            
        print(f"\n{Fore.GREEN}🚀 Starte Upload von {len(videos)} Video(s)...")
        
        # Lade Playlist-Cache einmalig für bessere Quota-Effizienz
        self._load_playlist_cache()
        
        # Bestätige Upload
        if not self._confirm_upload(videos):
            print(f"{Fore.YELLOW}⏹️  Upload abgebrochen durch Benutzer.")
            return False
        
        success_count = 0
        
        for i, video in enumerate(videos, 1):
            clean_title = self._clean_title_for_display(video['title'])
            print(f"\n{Fore.CYAN}{'='*70}")
            print(f"{Fore.CYAN}📤 Upload {i}/{len(videos)}: {clean_title}")
            print(f"{Fore.CYAN}{'='*70}")
            
            try:
                # Upload das Video
                video_id = self._upload_single_video(video)
                
                if video_id:
                    # Füge zu Playlist hinzu
                    self._add_to_playlist(video_id, video)
                    
                    # Benenne Datei um
                    self._rename_uploaded_file(video)
                    
                    success_count += 1
                    self.stats['uploaded_videos'] += 1
                    
                    print(f"{Fore.GREEN}✅ '{clean_title}' erfolgreich als {self.default_visibility.upper()} hochgeladen!")
                    
                else:
                    self.stats['failed_uploads'] += 1
                    print(f"{Fore.RED}❌ Upload fehlgeschlagen für: {clean_title}")
                
                # Pause zwischen Uploads
                if i < len(videos):
                    print(f"{Fore.YELLOW}⏳ Warte 10 Sekunden vor nächstem Upload...")
                    time.sleep(10)
                    
            except Exception as e:
                self.stats['failed_uploads'] += 1
                print(f"{Fore.RED}❌ Fehler beim Upload von '{clean_title}': {str(e)}")
                
        # Upload-Zusammenfassung
        self._print_upload_summary(success_count, len(videos))
        
        return success_count > 0
    
    def _upload_single_video(self, video: Dict) -> Optional[str]:
        """Lädt ein einzelnes Video zu YouTube hoch"""
        try:
            # Erstelle Video-Metadaten
            body = self._create_video_metadata(video)
            
            # Erstelle Media Upload mit kleineren Chunks für bessere Progress-Updates
            chunk_size = 1024 * 1024 * 5  # 5MB Chunks für regelmäßigere Updates
            media = MediaFileUpload(
                video['file_path'],
                chunksize=chunk_size,
                resumable=True,
                mimetype='video/*'
            )
            
            # Starte Upload-Request
            request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Upload mit verbesserter Progress Bar
            response = None
            retry = 0
            
            # Erstelle Progress Bar basierend auf Dateigröße
            file_size_bytes = video['file_size']
            file_size_mb = video['file_size_mb']
            
            clean_title = self._clean_title_for_display(video['title'])
            print(f"{Fore.BLUE}📤 Starte Upload: {clean_title} ({file_size_mb:.1f} MB)")
            
            # Bereinige Titel für Progress Bar (entferne problematische Unicode-Zeichen)
            progress_title = clean_title
            
            # Entferne Unicode-Escape-Sequenzen
            import re
            progress_title = re.sub(r'\\udc[0-9a-fA-F]{2}', '', progress_title)
            
            # Fallback auf ASCII mit Replacement für saubere Darstellung
            progress_title = progress_title.encode('ascii', errors='replace').decode('ascii')
            
            # Entferne Replacement-Character
            progress_title = progress_title.replace('?', '').strip()
            
            with tqdm(
                total=file_size_bytes,
                desc=f"📤 {progress_title[:30]}",
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                colour='green',
                ncols=100,
                leave=True,
                dynamic_ncols=False,
                file=sys.stdout,
                ascii=False
            ) as pbar:
                
                last_uploaded_bytes = 0
                last_progress_percent = 0
                
                while response is None:
                    try:
                        status, response = request.next_chunk()
                        
                        if status:
                            # Berechne hochgeladene Bytes basierend auf Progress
                            uploaded_bytes = int(status.progress() * file_size_bytes)
                            progress_percent = status.progress() * 100
                            
                            # Update Progress Bar mit Delta (nur bei nennenswerten Änderungen)
                            bytes_increment = uploaded_bytes - last_uploaded_bytes
                            progress_increment = progress_percent - last_progress_percent
                            
                            if bytes_increment > 0:
                                pbar.update(bytes_increment)
                                last_uploaded_bytes = uploaded_bytes
                            
                            # Update Progress Info nur bei größeren Schritten (mindestens 1% Unterschied)
                            if progress_increment >= 1.0 or response:
                                pbar.set_postfix({
                                    'Prozent': f'{progress_percent:.1f}%',
                                    'Retry': retry if retry > 0 else None
                                }, refresh=False)  # refresh=False verhindert zu häufige Updates
                                last_progress_percent = progress_percent
                                
                        elif response:
                            # Upload complete - fülle die Bar auf
                            remaining_bytes = file_size_bytes - last_uploaded_bytes
                            if remaining_bytes > 0:
                                pbar.update(remaining_bytes)
                            pbar.set_postfix({'Status': '✅ Abgeschlossen'}, refresh=True)
                            pbar.refresh()  # Finale Aktualisierung
                            
                    except googleapiclient.errors.HttpError as e:
                        if e.resp.status in [500, 502, 503, 504]:
                            # Retriable errors
                            retry += 1
                            if retry > 3:
                                pbar.write(f"{Fore.RED}❌ Zu viele Wiederholungsversuche")
                                raise e
                            pbar.write(f"{Fore.YELLOW}⚠️  Retriable error {e.resp.status}, retry {retry}/3")
                            time.sleep(2 ** retry)
                        elif e.resp.status == 403 and 'quotaExceeded' in str(e):
                            # Quota exceeded - spezielle Behandlung
                            pbar.write(f"{Fore.RED}❌ YOUTUBE DATA API QUOTA ÜBERSCHRITTEN!")
                            pbar.write(f"{Fore.YELLOW}💡 Quota wird täglich um ~9:00 Uhr deutscher Zeit zurückgesetzt")
                            pbar.write(f"{Fore.YELLOW}🔧 Oder beantragen Sie eine Quota-Erhöhung in der Google Cloud Console")
                            raise e
                        else:
                            pbar.write(f"{Fore.RED}❌ HTTP Error: {e}")
                            raise e
            
            if 'id' in response:
                print(f"{Fore.GREEN}✅ Upload erfolgreich! Video-ID: {response['id']}")
                return response['id']
            else:
                print(f"{Fore.RED}❌ Upload fehlgeschlagen: {response}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Fehler beim Video-Upload: {str(e)}")
            return None
    
    def _create_video_metadata(self, video: Dict) -> Dict:
        """Erstellt Metadaten für YouTube-Video"""
        # Verwende den bereinigten Titel für YouTube
        clean_title = self._clean_title_for_display(video['title'])
        
        # Generiere Beschreibung mit bereinigtem Titel
        description = self._generate_description(video, clean_title)
        
        # Generiere Tags
        tags = self._generate_tags(video)
        
        # Video-Metadaten für YouTube API
        body = {
            'snippet': {
                'title': clean_title,  # Verwende bereinigten Titel
                'description': description,
                'tags': tags,
                'categoryId': '20',  # Gaming category
                'defaultLanguage': 'de',
                'defaultAudioLanguage': 'de'
            },
            'status': {
                'privacyStatus': self.default_visibility,
                'selfDeclaredMadeForKids': False,  # Explizit NICHT für Kinder
                'embeddable': True,
                'license': 'youtube',
                'publicStatsViewable': True
            }
        }
        
        return body
    
    def _generate_description(self, video: Dict, clean_title: Optional[str] = None) -> str:
        """Generiert automatische Beschreibung für das Video"""
        # Verwende bereinigten Titel falls verfügbar, sonst Original
        title_for_description = clean_title if clean_title else self._clean_title_for_display(video['title'])
        
        description_parts = [
            f"Gameplay Video: {title_for_description}",
            ""
        ]
        
        # Spiel-Information hinzufügen
        if video['playlist_info']['game_folder']:
            description_parts.append(f"Spiel: {video['playlist_info']['game_folder']}")
        
        # Kategorie hinzufügen (Unterordner)
        if video['playlist_info']['sub_folders']:
            category = video['playlist_info']['sub_folders'][-1]  # Letzter/spezifischster Unterordner
            description_parts.append(f"Kategorie: {category}")
        
        # Video-Status hinzufügen (merged/unmergable)
        if video['video_type'] == 'merged':
            description_parts.append("Status: Sound erfolgreich gemerged")
        else:  # unmergable
            description_parts.append("Status: Sound war nicht mergbar (Original-Audio)")
        
        # Aufnahmedatum
        record_date_str = video['record_date'].strftime('%d.%m.%Y - %H:%M Uhr')
        description_parts.append(f"Aufgenommen am: {record_date_str}")
        
        description_parts.append("")
        
        # Sammlung
        main_folder = video['playlist_info']['main_folder']
        description_parts.append(f'Automatisch hochgeladen aus der Sammlung "{main_folder}"')
        
        return '\n'.join(description_parts)
    
    def _generate_tags(self, video: Dict) -> List[str]:
        """Generiert Tags für das Video"""
        tags = ['Gaming', 'Gameplay', 'Deutsch', "Let's Play"]
        
        # Spiel-Name als Tag
        if video['playlist_info']['game_folder']:
            tags.append(video['playlist_info']['game_folder'])
        
        # Haupt-Ordner als Tag
        main_folder = video['playlist_info']['main_folder']
        if main_folder:
            tags.append(main_folder.replace(' ', ''))
        
        # Sub-Ordner als Tags
        for sub_folder in video['playlist_info']['sub_folders']:
            tags.append(sub_folder)
        
        return tags
    
    def _add_to_playlist(self, video_id: str, video: Dict):
        """Fügt Video zu allen entsprechenden Playlists hinzu (hierarchisch)"""
        try:
            playlist_info = video['playlist_info']
            potential_playlists = playlist_info['potential_playlists']
            clean_title = self._clean_title_for_display(video['title'])
            
            if not potential_playlists:
                print(f"{Fore.YELLOW}⚠️  Keine Playlists für Video '{clean_title}' gefunden")
                return
            
            print(f"{Fore.BLUE}📋 Füge Video zu {len(potential_playlists)} Playlist(s) hinzu...")
            
            successful_additions = 0
            
            # Füge zu allen potentiellen Playlists hinzu (vom spezifischsten zum allgemeinsten)
            for playlist_name in potential_playlists:
                try:
                    playlist_id = self._get_or_create_playlist(playlist_name)
                    
                    if playlist_id:
                        self._add_video_to_playlist(video_id, playlist_id)
                        print(f"{Fore.GREEN}   ✅ '{playlist_name}' - erfolgreich hinzugefügt")
                        successful_additions += 1
                    else:
                        print(f"{Fore.YELLOW}   ⚠️  '{playlist_name}' - Playlist konnte nicht erstellt werden")
                        
                except Exception as playlist_error:
                    print(f"{Fore.RED}   ❌ '{playlist_name}' - Fehler: {str(playlist_error)}")
            
            if successful_additions > 0:
                print(f"{Fore.GREEN}📋 Video erfolgreich zu {successful_additions}/{len(potential_playlists)} Playlist(s) hinzugefügt")
            else:
                print(f"{Fore.RED}❌ Video konnte zu keiner Playlist hinzugefügt werden")
                
        except Exception as e:
            clean_title = self._clean_title_for_display(video.get('title', 'Unbekannt'))
            print(f"{Fore.YELLOW}⚠️  Warnung: Playlist-Zuordnung für '{clean_title}' fehlgeschlagen: {str(e)}")
    
    def _get_or_create_playlist(self, playlist_name: str) -> Optional[str]:
        """Holt oder erstellt eine Playlist (mit Cache-Optimierung)"""
        try:
            # Lade Playlist-Cache einmalig falls noch nicht geschehen
            self._load_playlist_cache()
            
            # Prüfe ob Playlist bereits im Cache existiert
            if playlist_name in self.playlist_cache:
                if self.debug_mode:
                    print(f"{Fore.GREEN}📋 Playlist '{playlist_name}' aus Cache gefunden")
                return self.playlist_cache[playlist_name]
            
            # Erstelle neue Playlist
            if self.debug_mode:
                print(f"{Fore.CYAN}📋 Erstelle neue Playlist: {playlist_name}")
                
            request = self.youtube_service.playlists().insert(
                part='snippet,status',
                body={
                    'snippet': {
                        'title': playlist_name,
                        'description': f'Automatisch erstellte Playlist für {playlist_name} Videos',
                        'defaultLanguage': 'de'
                    },
                    'status': {
                        'privacyStatus': 'unlisted'
                    }
                }
            )
            
            response = request.execute()
            playlist_id = response['id']
            
            # Füge neue Playlist zum Cache hinzu
            self.playlist_cache[playlist_name] = playlist_id
            
            print(f"{Fore.CYAN}📋 Neue Playlist erstellt: {playlist_name}")
            
            return playlist_id
            
        except Exception as e:
            print(f"{Fore.RED}❌ Fehler bei Playlist-Verwaltung: {str(e)}")
            return None
    
    def _add_video_to_playlist(self, video_id: str, playlist_id: str):
        """Fügt Video zu einer Playlist hinzu"""
        try:
            request = self.youtube_service.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            )
            
            request.execute()
            
        except Exception as e:
            print(f"{Fore.RED}❌ Fehler beim Hinzufügen zur Playlist: {str(e)}")
    
    def _rename_uploaded_file(self, video: Dict):
        """Benennt eine hochgeladene Datei um"""
        try:
            original_path = Path(video['file_path'])
            original_name = original_path.name
            
            # Erstelle neuen Namen mit uploaded_ Präfix
            for prefix in self.VIDEO_PREFIXES:
                if original_name.startswith(prefix):
                    new_name = original_name.replace(prefix, self.UPLOADED_PREFIX, 1)
                    break
            else:
                new_name = f"{self.UPLOADED_PREFIX}{original_name}"
            
            new_path = original_path.parent / new_name
            
            # Handle Namenskonflikte
            counter = 1
            while new_path.exists():
                name_parts = new_name.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    new_name = f"{new_name}_{counter}"
                new_path = original_path.parent / new_name
                counter += 1
            
            # Benenne Datei um
            original_path.rename(new_path)
            
            print(f"{Fore.CYAN}📝 Datei umbenannt: {original_name} → {new_name}")
            
            if self.debug_mode:
                print(f"   Alter Pfad: {original_path}")
                print(f"   Neuer Pfad: {new_path}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Fehler beim Umbenennen der Datei: {str(e)}")
    
    def _confirm_upload(self, videos: List[Dict]) -> bool:
        """Bestätigung vor dem Upload"""
        print(f"\n{Fore.YELLOW}⚠️  Sie sind dabei, {len(videos)} Video(s) zu YouTube hochzuladen!")
        print(f"{Fore.YELLOW}⚠️  Sichtbarkeit: {self.default_visibility.upper()}")
        print(f"{Fore.YELLOW}⚠️  Nach dem Upload werden die Dateien umbenannt (Präfix 'uploaded_')")
        
        response = input(f"\n{Fore.WHITE}Fortfahren? (j/N): ").strip().lower()
        return response in ['j', 'ja', 'y', 'yes']
    
    def _print_upload_summary(self, success_count: int, total_count: int):
        """Druckt Upload-Zusammenfassung"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📊 UPLOAD-ZUSAMMENFASSUNG")
        print(f"{Fore.CYAN}{'='*70}")
        
        print(f"{Fore.GREEN}✅ Erfolgreich hochgeladen: {success_count}/{total_count}")
        print(f"{Fore.RED}❌ Fehlgeschlagen: {self.stats['failed_uploads']}")
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        print(f"{Fore.BLUE}📈 Erfolgsrate: {success_rate:.1f}%")
        
        print(f"\n{Fore.YELLOW}📋 Video-Typen:")
        print(f"   📹 Merged Videos: {self.stats['merged_videos']}")
        print(f"   📼 Unmergable Videos: {self.stats['unmergable_videos']}")
        
        print(f"\n{Fore.CYAN}🎉 Upload-Prozess abgeschlossen!")


def main():
    """Hauptfunktion des YouTube Uploaders"""
    # Lade Umgebungsvariablen
    load_dotenv()
    
    # Argument Parser
    parser = argparse.ArgumentParser(
        description='🎮 YouTube Gaming Video Uploader v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python uploader.py                    # Standard Upload aller Videos
  python uploader.py --preview          # Nur Vorschau, kein Upload
  python uploader.py --debug            # Debug-Modus aktivieren
  python uploader.py --path /pfad/zu/videos  # Alternativer Pfad

Konfiguration über .env-Datei:
  RECORDINGS_PATH=/pfad/zu/aufnahmen
  DEFAULT_VISIBILITY=unlisted
  DEBUG_MODE=false
        """
    )
    
    parser.add_argument(
        '--preview', 
        action='store_true',
        help='Zeigt nur eine Vorschau der gefundenen Videos (kein Upload)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Aktiviert den Debug-Modus für detaillierte Ausgaben'
    )
    
    parser.add_argument(
        '--path',
        type=str,
        help='Pfad zu den Aufnahmen (überschreibt RECORDINGS_PATH aus .env)'
    )
    
    args = parser.parse_args()
    
    # Validiere Pfad
    recordings_path = args.path or os.getenv('RECORDINGS_PATH')
    
    if not recordings_path:
        print(f"{Fore.RED}❌ Fehler: Kein Aufnahmen-Pfad angegeben!")
        print(f"{Fore.YELLOW}💡 Setzen Sie RECORDINGS_PATH in der .env-Datei oder verwenden Sie --path")
        print(f"{Fore.YELLOW}   Beispiel: RECORDINGS_PATH=/home/carst/n_drive/AUFNAHMEN")
        sys.exit(1)
    
    if not os.path.exists(recordings_path):
        print(f"{Fore.RED}❌ Fehler: Aufnahmen-Pfad nicht gefunden: {recordings_path}")
        print(f"{Fore.YELLOW}💡 Stellen Sie sicher, dass der SMB-Drive gemountet ist!")
        sys.exit(1)
    
    # Erstelle Uploader-Instanz
    uploader = YouTubeUploader(
        recordings_path=recordings_path,
        debug_mode=args.debug or os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    )
    
    try:
        # Suche Videos
        videos = uploader.find_videos()
        
        if not videos:
            print(f"{Fore.YELLOW}📭 Keine Videos zum Upload gefunden.")
            print(f"{Fore.YELLOW}💡 Überprüfen Sie, ob Videos mit den Präfixen 'merged_' oder 'unmergable_' vorhanden sind.")
            sys.exit(0)
        
        # Preview-Modus
        if args.preview:
            uploader.preview_videos(videos)
            
            # Teste auch die YouTube-Authentifizierung im Preview-Modus
            print(f"\n{Fore.CYAN}🔑 Teste YouTube-Authentifizierung...")
            if uploader.authenticate_youtube():
                print(f"{Fore.GREEN}✅ YouTube-Authentifizierung erfolgreich getestet!")
            else:
                print(f"{Fore.RED}❌ YouTube-Authentifizierung fehlgeschlagen!")
                print(f"{Fore.YELLOW}💡 Überprüfen Sie Ihre credentials.json Datei.")
                sys.exit(1)
            
            print(f"\n{Fore.CYAN}👁️  Preview-Modus: Kein Upload durchgeführt")
            sys.exit(0)
        
        # Zeige Vorschau
        uploader.preview_videos(videos)
        
        # Authentifizierung
        if not uploader.authenticate_youtube():
            print(f"{Fore.RED}❌ YouTube-Authentifizierung fehlgeschlagen!")
            sys.exit(1)
        
        # Upload
        success = uploader.upload_videos(videos)
        
        if success:
            print(f"\n{Fore.GREEN}🎉 Upload-Prozess erfolgreich abgeschlossen!")
            sys.exit(0)
        else:
            print(f"\n{Fore.RED}❌ Upload-Prozess mit Fehlern beendet!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️  Upload durch Benutzer abgebrochen.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Unerwarteter Fehler: {str(e)}")
        if args.debug:
            import traceback
            print(f"{Fore.RED}{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
