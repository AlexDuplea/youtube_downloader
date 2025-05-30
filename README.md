# YouTube Playlist Downloader - Versione Pro

Un potente strumento Python per scaricare intere playlist YouTube in formato MP3 di alta qualità con metadati completi e copertine ottimizzate per dispositivi mobili.

## Caratteristiche Principali

- **Download Playlist Completo**: Scarica tutte le canzoni da una playlist YouTube in un solo comando
- **Audio di Alta Qualità**: Output MP3 a 320 kbps per la migliore esperienza d'ascolto
- **Ottimizzato per Android**: Metadati ID3 completi compatibili con tutti i player musicali
- **Copertine Album**: Thumbnail YouTube convertite automaticamente in copertine MP3
- **Barra di Progresso**: Monitoraggio in tempo reale del download
- **Metadati Completi**: Titolo, artista, album, anno e copertina per ogni brano
- **Gestione Errori Avanzata**: Continua il download anche se alcuni video falliscono
- **Pulizia Automatica**: Rimozione automatica dei file temporanei

## Requisiti

### Dipendenze Python
```bash
pip install requests yt-dlp mutagen Pillow
```

### Software Aggiuntivo
- **FFmpeg**: Richiesto per la conversione audio
  - Windows: Scaricare da [ffmpeg.org](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`

### API Key YouTube
È necessaria una chiave API di YouTube Data v3:
1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o seleziona uno esistente
3. Abilita l'API YouTube Data v3
4. Genera una chiave API
5. Sostituisci `API_KEY` nel codice con la tua chiave

## Installazione

1. Clona il repository:
```bash
git clone <repository-url>
cd youtube-playlist-downloader
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

3. Configura la tua API Key nel file `main.py`:
```python
API_KEY = 'LA_TUA_API_KEY_QUI'
```

4. (Opzionale) Modifica la cartella di download predefinita:
```python
DEFAULT_FOLDER = "percorso/alla/tua/cartella"
```

## Utilizzo

1. Esegui il programma:
```bash
python main.py
```

2. Inserisci il link della playlist YouTube quando richiesto

3. Scegli la cartella di destinazione (o usa quella predefinita)

4. Conferma per iniziare il download

### Formati Link Supportati
- `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- `https://youtube.com/playlist?list=PLAYLIST_ID`
- `https://youtu.be/playlist?list=PLAYLIST_ID`

## Configurazione Avanzata

### Personalizzazione Output
Il programma può essere configurato modificando le seguenti opzioni in `main.py`:

- **Qualità Audio**: Modifica `preferredquality` in `ydl_opts`
- **Formato Output**: Cambia `preferredcodec` per altri formati
- **Template Nome File**: Personalizza `outtmpl` per la struttura dei nomi

### Ottimizzazioni
- **Rate Limiting**: Pause automatiche per evitare limitazioni API
- **Retry Logic**: Tentativi multipli per download falliti
- **Memory Management**: Gestione efficiente della memoria per playlist grandi

## Struttura Metadati

Ogni file MP3 scaricato include:
- **Titolo**: Nome del video YouTube
- **Artista**: Nome del canale (pulito da suffissi come "- Topic")
- **Album**: "YouTube Download"
- **Anno**: Anno di pubblicazione del video
- **Copertina**: Thumbnail del video ottimizzata (max 500x500px)

## Gestione Errori

Il programma gestisce automaticamente:
- Video privati o rimossi
- Errori di rete temporanei
- Problemi di conversione audio
- Limitazioni rate API
- File corrotti o non accessibili

## Risoluzione Problemi

### Errore "FFmpeg not found"
- Assicurati che FFmpeg sia installato e nel PATH di sistema
- Su Windows, aggiungi la cartella bin di FFmpeg alle variabili d'ambiente

### Errore API Key
- Verifica che la chiave API sia corretta
- Controlla che l'API YouTube Data v3 sia abilitata nel tuo progetto Google Cloud
- Verifica i limiti di quota giornaliera

### Download Lenti
- Riduci la qualità audio se necessario
- Verifica la connessione internet
- Controlla se ci sono limitazioni del provider internet

## Limitazioni

- Rispetta i termini di servizio di YouTube
- Limitato dalla quota API di Google (10.000 unità/giorno di default)
- Non può scaricare contenuti con restrizioni geografiche
- Richiede connessione internet stabile

## Contributi

Per contribuire al progetto:
1. Fork del repository
2. Crea un branch per la tua feature
3. Commit delle modifiche
4. Push del branch
5. Apri una Pull Request

## Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per i dettagli.

## Disclaimer

Questo strumento è destinato esclusivamente per uso personale e educativo. Gli utenti sono responsabili del rispetto delle leggi sul copyright e dei termini di servizio di YouTube. L'autore non si assume responsabilità per l'uso improprio del software.
