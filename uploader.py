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
        print(f"{Fore.CYAN}{'='*70}\n")
        
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
                    # Rekursiv in Unterordner
                    sub_path = current_path + [item.name]
                    sub_videos = self._scan_folder_recursive(item, main_folder, sub_path)
                    videos.extend(sub_videos)
                    
        except PermissionError:
            if self.debug_mode:
                print(f"{Fore.YELLOW}⚠️  Keine Berechtigung für: {folder_path}")
                
        return videos
    
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
                'WINDM?LE': 'WINDMÜHLE'
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
        if len(folder_structure) > 2:
            # Verwende spezifischsten Unterordner als primäre Playlist
            playlist_info['primary_playlist'] = folder_structure[-1]
            playlist_info['potential_playlists'] = folder_structure[1:]  # Ohne Hauptordner
            playlist_info['additional_playlists'] = folder_structure[1:-1]  # Ohne Haupt- und primäre Playlist
            
        elif len(folder_structure) > 1:
            # Verwende Spiel-Ordner als primäre Playlist
            playlist_info['primary_playlist'] = folder_structure[1]
            playlist_info['potential_playlists'] = folder_structure
            playlist_info['additional_playlists'] = [folder_structure[0]]
            
        else:
            # Nur Hauptordner verfügbar
            playlist_info['primary_playlist'] = folder_structure[0]
            playlist_info['potential_playlists'] = folder_structure
            playlist_info['additional_playlists'] = []
        
        return playlist_info
    
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
            print(f"\n{Fore.WHITE}{i}. {Fore.YELLOW}{video['title']}")
            print(f"   📁 Pfad: {video['folder_structure']}")
            print(f"   📊 Größe: {video['file_size_mb']} MB")
            print(f"   📅 Aufnahme: {video['record_date'].strftime('%d.%m.%Y - %H:%M Uhr')}")
            
            # Playlist-Analyse
            playlist_info = video['playlist_info']
            print(f"\n{Fore.BLUE}🔍 Playlist-Analyse für '{video['title']}':")
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
    
    def upload_videos(self, videos: List[Dict]) -> bool:
        """Lädt alle Videos zu YouTube hoch"""
        if not videos:
            print(f"{Fore.YELLOW}📭 Keine Videos zum Upload gefunden.")
            return True
            
        if not self.youtube_service:
            print(f"{Fore.RED}❌ YouTube-Service nicht authentifiziert!")
            return False
            
        print(f"\n{Fore.GREEN}🚀 Starte Upload von {len(videos)} Video(s)...")
        
        # Bestätige Upload
        if not self._confirm_upload(videos):
            print(f"{Fore.YELLOW}⏹️  Upload abgebrochen durch Benutzer.")
            return False
        
        success_count = 0
        
        for i, video in enumerate(videos, 1):
            print(f"\n{Fore.CYAN}{'='*70}")
            print(f"{Fore.CYAN}📤 Upload {i}/{len(videos)}: {video['title']}")
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
                    
                    print(f"{Fore.GREEN}✅ '{video['title']}' erfolgreich als {self.default_visibility.upper()} hochgeladen!")
                    
                else:
                    self.stats['failed_uploads'] += 1
                    print(f"{Fore.RED}❌ Upload fehlgeschlagen für: {video['title']}")
                
                # Pause zwischen Uploads
                if i < len(videos):
                    print(f"{Fore.YELLOW}⏳ Warte 10 Sekunden vor nächstem Upload...")
                    time.sleep(10)
                    
            except Exception as e:
                self.stats['failed_uploads'] += 1
                print(f"{Fore.RED}❌ Fehler beim Upload von '{video['title']}': {str(e)}")
                
        # Upload-Zusammenfassung
        self._print_upload_summary(success_count, len(videos))
        
        return success_count > 0
    
    def _upload_single_video(self, video: Dict) -> Optional[str]:
        """Lädt ein einzelnes Video zu YouTube hoch"""
        try:
            # Erstelle Video-Metadaten
            body = self._create_video_metadata(video)
            
            # Erstelle Media Upload
            media = MediaFileUpload(
                video['file_path'],
                chunksize=-1,
                resumable=True,
                mimetype='video/*'
            )
            
            # Starte Upload-Request
            request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Upload mit tqdm Progress Bar
            response = None
            retry = 0
            
            # Erstelle Progress Bar mit Dateigröße
            file_size_mb = video['file_size_mb']
            
            with tqdm(
                total=100,
                desc=f"📤 {video['title'][:30]}",
                unit="%",
                bar_format="{l_bar}{bar}| {n:.1f}% [{elapsed}<{remaining}, {rate_fmt}]",
                colour='green'
            ) as pbar:
                
                last_progress = 0
                
                while response is None:
                    try:
                        status, response = request.next_chunk()
                        
                        if status:
                            progress = int(status.progress() * 100)
                            # Update Progress Bar
                            increment = progress - last_progress
                            if increment > 0:
                                pbar.update(increment)
                                last_progress = progress
                                
                        elif response:
                            # Upload complete
                            pbar.update(100 - last_progress)
                            
                    except googleapiclient.errors.HttpError as e:
                        if e.resp.status in [500, 502, 503, 504]:
                            # Retriable errors
                            retry += 1
                            if retry > 3:
                                pbar.write(f"{Fore.RED}❌ Zu viele Wiederholungsversuche")
                                raise e
                            pbar.write(f"{Fore.YELLOW}⚠️  Retriable error {e.resp.status}, retry {retry}/3")
                            time.sleep(2 ** retry)
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
        # Generiere Beschreibung
        description = self._generate_description(video)
        
        # Generiere Tags
        tags = self._generate_tags(video)
        
        # Video-Metadaten für YouTube API
        body = {
            'snippet': {
                'title': video['title'],
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
    
    def _generate_description(self, video: Dict) -> str:
        """Generiert automatische Beschreibung für das Video"""
        description_parts = [
            f"Gameplay Video: {video['title']}",
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
        """Fügt Video zu entsprechenden Playlists hinzu"""
        try:
            primary_playlist = video['playlist_info']['primary_playlist']
            
            if primary_playlist:
                playlist_id = self._get_or_create_playlist(primary_playlist)
                
                if playlist_id:
                    self._add_video_to_playlist(video_id, playlist_id)
                    print(f"{Fore.GREEN}📋 Video zur Playlist '{primary_playlist}' hinzugefügt")
                    
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Warnung: Playlist-Zuordnung fehlgeschlagen: {str(e)}")
    
    def _get_or_create_playlist(self, playlist_name: str) -> Optional[str]:
        """Holt oder erstellt eine Playlist"""
        try:
            # Suche nach existierenden Playlists
            request = self.youtube_service.playlists().list(
                part='snippet',
                mine=True,
                maxResults=50
            )
            
            response = request.execute()
            
            # Prüfe ob Playlist bereits existiert
            for playlist in response.get('items', []):
                if playlist['snippet']['title'] == playlist_name:
                    return playlist['id']
            
            # Erstelle neue Playlist
            request = self.youtube_service.playlists().insert(
                part='snippet,status',
                body={
                    'snippet': {
                        'title': playlist_name,
                        'description': f'Automatisch erstellte Playlist für {playlist_name} Videos',
                        'defaultLanguage': 'de'
                    },
                    'status': {
                        'privacyStatus': 'public'
                    }
                }
            )
            
            response = request.execute()
            print(f"{Fore.CYAN}📋 Neue Playlist erstellt: {playlist_name}")
            
            return response['id']
            
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
