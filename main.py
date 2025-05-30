import requests
import re
import yt_dlp
import os
import sys
import time
from typing import List, Optional
from datetime import datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC, TPE2
import urllib.request
from io import BytesIO
from PIL import Image


class Colors:
    """Classe per i colori del terminale"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ProgressBar:
    """Classe per gestire la barra di progresso"""

    def __init__(self, total: int, width: int = 50):
        self.total = total
        self.width = width
        self.current = 0

    def update(self, increment: int = 1):
        """Aggiorna la barra di progresso"""
        self.current += increment
        percent = (self.current / self.total) * 100
        filled = int(self.width * self.current // self.total)
        bar = '█' * filled + '░' * (self.width - filled)

        print(f'\r{Colors.OKCYAN}[{bar}] {percent:.1f}% ({self.current}/{self.total}){Colors.ENDC}', end='', flush=True)

        if self.current >= self.total:
            print()  # Nuova riga quando completato


class YouTubePlaylistDownloader:
    """Classe principale per il download delle playlist YouTube"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def print_banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        """Stampa il banner di benvenuto"""
        banner = f"""
{Colors.HEADER}{'=' * 70}
    🎵 YOUTUBE PLAYLIST DOWNLOADER - VERSIONE PRO 🎵
{'=' * 70}{Colors.ENDC}
{Colors.OKCYAN}Scarica la tua playlist preferita in formato MP3 di alta qualità!{Colors.ENDC}
"""
        print(banner)

    def get_playlist_id(self, youtube_link: str) -> Optional[str]:
        """Estrae l'ID della playlist dal link YouTube"""
        patterns = [
            r"(?:list=|youtu\.be\/playlist\?list=)([a-zA-Z0-9_-]+)",
            r"youtube\.com\/playlist\?list=([a-zA-Z0-9_-]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, youtube_link)
            if match:
                return match.group(1)
        return None

    def extract_playlist_videos(self, playlist_id: str) -> List[str]:
        """Estrae tutti i video dalla playlist"""
        print(f"\n{Colors.OKBLUE}🔍 Ricerca video nella playlist...{Colors.ENDC}")

        base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
        params = {
            'part': 'snippet',
            'playlistId': playlist_id,
            'maxResults': 50,
            'key': self.api_key
        }

        video_links = []
        page_count = 0

        try:
            while True:
                print(f"\r{Colors.OKCYAN}📄 Caricamento pagina {page_count + 1}...{Colors.ENDC}", end='', flush=True)

                response = self.session.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                # Controllo errori API
                if 'error' in data:
                    raise Exception(f"Errore API: {data['error']['message']}")

                for item in data.get('items', []):
                    snippet = item.get('snippet', {})
                    resource = snippet.get('resourceId', {})
                    video_id = resource.get('videoId')
                    if video_id:
                        video_links.append(f'https://www.youtube.com/watch?v={video_id}')

                page_count += 1

                # Controllo paginazione
                if 'nextPageToken' in data:
                    params['pageToken'] = data['nextPageToken']
                    time.sleep(0.1)  # Rate limiting
                else:
                    break

        except requests.exceptions.RequestException as e:
            print(f"\n{Colors.FAIL}❌ Errore di connessione: {e}{Colors.ENDC}")
            return []
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Errore durante l'estrazione: {e}{Colors.ENDC}")
            return []

        print(f"\n{Colors.OKGREEN}✅ Trovati {len(video_links)} video!{Colors.ENDC}")
        return video_links

    def create_download_folder(self, folder_path: str) -> bool:
        """Crea la cartella di download se non esiste"""
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"{Colors.OKGREEN}📁 Cartella creata: {folder_path}{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}❌ Impossibile creare la cartella: {e}{Colors.ENDC}")
            return False

    def download_audio(self, urls: List[str], download_folder: str):
        """Scarica l'audio dai video YouTube"""
        if not self.create_download_folder(download_folder):
            return

        # Configurazione yt-dlp migliorata con metadati
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                }
            ],
            'noplaylist': True,
            'writethumbnail': True,  # Scarica thumbnail
            'writeinfojson': True,  # Scarica info per metadati
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
            'extractaudio': True,
        }

        # Aggiungi ffmpeg path se specificato
        ffmpeg_path = self.find_ffmpeg()
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path

        print(f"\n{Colors.HEADER}🎵 INIZIO DOWNLOAD{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📂 Cartella: {download_folder}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🎯 Video da scaricare: {len(urls)}{Colors.ENDC}\n")

        # Barra di progresso
        progress = ProgressBar(len(urls))
        successful_downloads = 0
        failed_downloads = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for i, url in enumerate(urls, 1):
                try:
                    # Ottieni info del video
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Titolo sconosciuto')[:50]

                    print(f"\n{Colors.OKBLUE}⬇️  [{i}/{len(urls)}] {title}...{Colors.ENDC}")

                    # Download
                    ydl.download([url])

                    # Aggiungi metadati personalizzati
                    self.add_metadata_to_mp3(info, download_folder)

                    successful_downloads += 1
                    print(f"{Colors.OKGREEN}✅ Completato con metadati!{Colors.ENDC}")

                except Exception as e:
                    error_msg = str(e)[:100]
                    failed_downloads.append((url, error_msg))
                    print(f"{Colors.FAIL}❌ Errore: {error_msg}{Colors.ENDC}")

                progress.update()
                time.sleep(0.5)  # Pausa per evitare rate limiting

        # Riepilogo finale
        self.print_summary(successful_downloads, failed_downloads, download_folder)

    def find_ffmpeg(self) -> Optional[str]:
        """Cerca ffmpeg nel sistema"""
        possible_paths = [
            'C:\\ffmpeg\\bin',
            'C:\\ffmpeg\\ffmpeg-7.0.2-essentials_build\\bin',
            '/usr/local/bin',
            '/usr/bin',
        ]

        for path in possible_paths:
            if os.path.exists(os.path.join(path, 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')):
                return path
        return None

    def add_metadata_to_mp3(self, video_info: dict, download_folder: str):
        """Aggiunge metadati completi al file MP3"""
        try:
            # Costruisci il nome del file MP3
            title = video_info.get('title', 'Unknown')
            # Pulisci il titolo da caratteri non validi per il filesystem
            clean_title = re.sub(r'[<>:"/\\|?*]', '', title)
            mp3_file = os.path.join(download_folder, f"{clean_title}.mp3")

            # Se il file non esiste, prova varianti
            if not os.path.exists(mp3_file):
                # Cerca file che iniziano con il titolo
                for file in os.listdir(download_folder):
                    if file.startswith(clean_title[:30]) and file.endswith('.mp3'):
                        mp3_file = os.path.join(download_folder, file)
                        break

            if not os.path.exists(mp3_file):
                print(f"{Colors.WARNING}⚠️  File MP3 non trovato per aggiungere metadati{Colors.ENDC}")
                return

            # Carica il file MP3
            audio = MP3(mp3_file, ID3=ID3)

            # Aggiungi ID3 tag se non esistono
            if audio.tags is None:
                audio.add_tags()

            # Estrai informazioni dal video
            title = video_info.get('title', 'Unknown Title')
            uploader = video_info.get('uploader', 'Unknown Artist')
            upload_date = video_info.get('upload_date', '')
            duration = video_info.get('duration', 0)
            view_count = video_info.get('view_count', 0)
            description = video_info.get('description', '')[:500]  # Limita descrizione

            # Pulisci il nome dell'artista (rimuove "- Topic" comune nei canali musicali)
            artist = re.sub(r'\s*-\s*Topic\s*$', '', uploader)

            # Estrai album/artista dal titolo se possibile (formato: "Artista - Titolo")
            if ' - ' in title:
                parts = title.split(' - ', 1)
                if len(parts) == 2:
                    extracted_artist = parts[0].strip()
                    extracted_title = parts[1].strip()
                    if len(extracted_artist) < 50:  # Ragionevole per essere un artista
                        artist = extracted_artist
                        title = extracted_title

            # Formatta la data
            year = ''
            if upload_date and len(upload_date) >= 4:
                year = upload_date[:4]

            # Aggiungi metadati ID3
            audio.tags.add(TIT2(encoding=3, text=title))  # Titolo
            audio.tags.add(TPE1(encoding=3, text=artist))  # Artista principale
            audio.tags.add(TPE2(encoding=3, text=uploader))  # Artista album (uploader originale)
            audio.tags.add(TALB(encoding=3, text="YouTube Download"))  # Album

            if year:
                audio.tags.add(TDRC(encoding=3, text=year))  # Anno

            # Aggiungi thumbnail come copertina
            thumbnail_added = self.add_thumbnail_to_mp3(audio, video_info, download_folder, clean_title)

            # Salva le modifiche
            audio.save()

            # Pulizia file temporanei
            self.cleanup_temp_files(download_folder, clean_title)

            print(f"{Colors.OKCYAN}🎯 Metadati aggiunti: {artist} - {title[:30]}...{Colors.ENDC}")
            if thumbnail_added:
                print(f"{Colors.OKGREEN}🖼️  Copertina aggiunta!{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Errore aggiunta metadati: {str(e)[:50]}...{Colors.ENDC}")

    def add_thumbnail_to_mp3(self, audio: MP3, video_info: dict, download_folder: str, clean_title: str) -> bool:
        """Aggiunge la thumbnail come copertina del file MP3"""
        try:
            # Cerca file thumbnail
            possible_thumbnails = [
                f"{clean_title}.jpg",
                f"{clean_title}.webp",
                f"{clean_title}.png"
            ]

            thumbnail_file = None
            for thumb_name in possible_thumbnails:
                thumb_path = os.path.join(download_folder, thumb_name)
                if os.path.exists(thumb_path):
                    thumbnail_file = thumb_path
                    break

            # Se non trova file locali, usa URL thumbnail
            if not thumbnail_file and 'thumbnail' in video_info:
                thumbnail_url = video_info['thumbnail']
                try:
                    # Scarica thumbnail da URL
                    response = urllib.request.urlopen(thumbnail_url, timeout=10)
                    img_data = response.read()

                    # Converti e ridimensiona immagine
                    img = Image.open(BytesIO(img_data))

                    # Ridimensiona se troppo grande (ottimizzazione per Android)
                    max_size = (500, 500)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)

                    # Converti in JPEG se necessario
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background

                    # Salva immagine ottimizzata
                    img_buffer = BytesIO()
                    img.save(img_buffer, format='JPEG', quality=85, optimize=True)
                    img_data = img_buffer.getvalue()

                except Exception:
                    return False
            else:
                # Leggi file thumbnail locale
                if thumbnail_file:
                    try:
                        with open(thumbnail_file, 'rb') as f:
                            img_data = f.read()

                        # Ottimizza immagine locale
                        img = Image.open(BytesIO(img_data))
                        max_size = (500, 500)
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)

                        if img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background

                        img_buffer = BytesIO()
                        img.save(img_buffer, format='JPEG', quality=85, optimize=True)
                        img_data = img_buffer.getvalue()

                    except Exception:
                        return False
                else:
                    return False

            # Aggiungi copertina ai metadati ID3
            audio.tags.add(APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',
                type=3,  # Cover (front)
                desc='Cover',
                data=img_data
            ))

            return True

        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Errore thumbnail: {str(e)[:30]}...{Colors.ENDC}")
            return False

    def cleanup_temp_files(self, download_folder: str, clean_title: str):
        """Rimuove file temporanei dopo l'elaborazione"""
        temp_extensions = ['.webp', '.jpg', '.png', '.info.json', '.part']

        for file in os.listdir(download_folder):
            if file.startswith(clean_title):
                for ext in temp_extensions:
                    if file.endswith(ext):
                        try:
                            os.remove(os.path.join(download_folder, file))
                        except:
                            pass  # Ignora errori di rimozione

    def print_summary(self, successful: int, failed: List, folder: str):
        """Stampa il riepilogo finale"""
        print(f"\n{Colors.HEADER}{'=' * 70}")
        print("🎉 DOWNLOAD COMPLETATO!")
        print(f"{'=' * 70}{Colors.ENDC}")

        print(f"{Colors.OKGREEN}✅ Download riusciti: {successful}{Colors.ENDC}")

        if failed:
            print(f"{Colors.FAIL}❌ Download falliti: {len(failed)}{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠️  File con errori:{Colors.ENDC}")
            for url, error in failed[:5]:  # Mostra solo i primi 5 errori
                print(f"   • {url[:50]}... - {error[:50]}...")

        print(f"\n{Colors.OKCYAN}📂 I file sono stati salvati in:{Colors.ENDC}")
        print(f"   {folder}")

        print(f"\n{Colors.OKGREEN}🎵 Buon ascolto! I file sono ottimizzati per Android 📱{Colors.ENDC}")


def main():
    """Funzione principale"""
    # Configurazione
    API_KEY = 'API_KEY'  # ⚠️ CAMBIA CON LA TUA API KEY
    DEFAULT_FOLDER = os.path.join(os.path.expanduser("~"), "Download", "Youtube MP3")

    # Verifica dipendenze
    missing_deps = []
    try:
        import mutagen
    except ImportError:
        missing_deps.append('mutagen')

    try:
        from PIL import Image
    except ImportError:
        missing_deps.append('Pillow')

    if missing_deps:
        print(f"{Colors.FAIL}❌ Dipendenze mancanti: {', '.join(missing_deps)}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Installa con: pip install {' '.join(missing_deps)}{Colors.ENDC}")
        return

    downloader = YouTubePlaylistDownloader(API_KEY)
    downloader.print_banner()

    print(f"{Colors.OKGREEN}📱 Ottimizzato per Android - Include metadati e copertine!{Colors.ENDC}\n")

    try:
        # Input utente
        print(f"{Colors.OKBLUE}🔗 Inserisci il link della playlist YouTube:{Colors.ENDC}")
        playlist_link = input("➤ ").strip()

        if not playlist_link:
            print(f"{Colors.FAIL}❌ Link non valido!{Colors.ENDC}")
            return

        # Estrai ID playlist
        playlist_id = downloader.get_playlist_id(playlist_link)
        if not playlist_id:
            print(f"{Colors.FAIL}❌ ID playlist non trovato nel link!{Colors.ENDC}")
            return

        print(f"{Colors.OKGREEN}✅ ID Playlist: {playlist_id}{Colors.ENDC}")

        # Estrai video
        video_links = downloader.extract_playlist_videos(playlist_id)
        if not video_links:
            print(f"{Colors.FAIL}❌ Nessun video trovato nella playlist!{Colors.ENDC}")
            return

        # Cartella di download
        print(f"\n{Colors.OKBLUE}📁 Cartella di download predefinita:{Colors.ENDC}")
        print(f"   {DEFAULT_FOLDER}")

        use_default = input(f"\n{Colors.OKCYAN}Usare questa cartella? (s/n): {Colors.ENDC}").strip().lower()

        if use_default in ['s', 'si', 'y', 'yes', '']:
            download_folder = DEFAULT_FOLDER
        else:
            download_folder = input(f"{Colors.OKBLUE}Inserisci il percorso della cartella: {Colors.ENDC}").strip()

        # Conferma download
        print(
            f"\n{Colors.WARNING}⚠️  Stai per scaricare {len(video_links)} file MP3 con metadati completi{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📋 Include: titolo, artista, anno, copertina album{Colors.ENDC}")
        confirm = input(f"{Colors.OKCYAN}Continuare? (s/n): {Colors.ENDC}").strip().lower()

        if confirm not in ['s', 'si', 'y', 'yes']:
            print(f"{Colors.WARNING}❌ Download annullato.{Colors.ENDC}")
            return

        # Avvia download
        downloader.download_audio(video_links, download_folder)

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Download interrotto dall'utente.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Errore inaspettato: {e}{Colors.ENDC}")


if __name__ == "__main__":
    main()