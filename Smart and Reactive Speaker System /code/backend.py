import vlc, ytmusicapi, yt_dlp, random, json, time

class Backend:
    # Initialize the backend
    def __init__(self):
        self.player = vlc.MediaPlayer()
        self.prevposition = 0
        self.ispause = True
        self.song = ''
        self.songinfo = ''
        self.audiourl = ''
        self.time = time.time()

    # Assign emotion to playlist and get a song from playlist
    def find_song_based_on_mood(self, mood):
        mood_index = 0
        with ytmusicapi.YTMusic() as ytmusic:
            if mood == 'happy':
                mood_index = 8
            elif mood == 'sad':
                mood_index = 11
            elif mood == 'surprise':
                mood_index = 1
            elif mood == 'neutral':
                mood_index = 4
            elif mood == 'angry':
                mood_index = 1
            elif mood == 'disgust':
                mood_index = 5
            elif mood == 'fear':
                mood_index = 7
            playlistlist = ytmusic.get_mood_playlists(params=ytmusic.get_mood_categories()["Moods & moments"][mood_index]['params'])
            luckyplaylist = ytmusic.get_playlist(playlistId=playlistlist[random.randint(0,len(playlistlist) - 1)]['playlistId'])
            luckysong = luckyplaylist['tracks'][random.randint(0, len(luckyplaylist['tracks']) - 1)]
        self.song = luckysong

    # Get the audo stream url from the videoId to feed to vlc to stream music
    def get_audio_stream(self):
        ydl_opts = {
            'extractor_args': {
                'youtube': {
                    'skip': ['hls,dash,translated_subs'],
                    'player_client': ['android_music']
                    }
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for format in ydl.sanitize_info(ydl.extract_info(f"https://music.youtube.com/watch?v=" + self.song['videoId'], download=False, process=False, ie_key="Youtube"))['formats']:
                if format['format_id'] == '251':
                    self.audiourl = format['url']

    # Assign the audio stream url to the vlc and play it
    def play_audio_stream(self):
        self.player.set_mrl(self.audiourl)
        self.player.play()
        self.ispause = False

    # Pauses
    def pause_audio_stream(self):
        if not self.ispause:
            self.player.pause()
            self.ispause = True

    # Unpauses
    def unpause_audio_stream(self):
        if self.ispause:
            self.player.pause()
            self.ispause = False

    # Change volume
    def set_audio_stream_volume(self, volume):
        self.player.audio_set_volume(volume)

    # Get position of audio
    def get_stream_position(self):
        return self.player.get_position()
    
    # Set position of audio (fast backward/forward)
    def set_stream_position(self, position):
        self.prevposition = position
        self.player.set_position(position)

    # Save feedbacked song to JSON file for future analysis
    def save_current_song_for_analyzing(self, emotion, isLiked):
        data = {}

        try:
            with open('song_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            pass

        data[self.song['videoId']] = {'isLiked': isLiked,
                                      'emotion': emotion,
                                      'listened_percentage': self.get_stream_position(),
                                      'time_spent': time.time() - self.time}
        
        try:
            with open('song_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass

def backend(conn_to_main):
    backend = Backend()
    # Very important while loop to send and receive info
    while True:
        # Sending info
        currentposition = backend.get_stream_position()
        if (currentposition - backend.prevposition > 0.001):
            backend.prevposition = currentposition
            conn_to_main.send({'position': currentposition})

        # Receiving info
        if conn_to_main.poll():
            order = conn_to_main.recv()
            if (order['action'] == 'unpause'):
                backend.unpause_audio_stream()
            elif (order['action'] == 'pause'):
                backend.pause_audio_stream()
            elif (order['action'] == 'set_new_mood'):
                backend.find_song_based_on_mood(order['mood'])
                backend.get_audio_stream()
                backend.play_audio_stream()
                backend.time = time.time()

                backend.prevposition = 0

                # Send to main song info
                conn_to_main.send({'title': backend.song['title'], 
                                   'thumbnailurl': backend.song['thumbnails'][0]['url'], 
                                   'length': backend.song['duration_seconds'], 
                                   'artist': backend.song['artists'][0]['name'], 
                                   'position': backend.get_stream_position()})
            elif (order['action'] == 'set_volume'):
                backend.set_audio_stream_volume(volume=order['volume'])
            elif (order['action'] == 'set_position'):
                backend.set_stream_position(order['position'])
            elif (order['action'] == 'feedbacked'):
                backend.save_current_song_for_analyzing(emotion=order['emotion'], isLiked=order['isLiked'])
