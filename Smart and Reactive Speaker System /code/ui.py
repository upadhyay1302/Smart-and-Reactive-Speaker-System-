import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageColor
import requests
import time

class App:
    # Initialize the UI and all required files
    def __init__(self, root, conn_to_main):
        self.root = root
        self.root.title("Smert")
        self.root.geometry("800x480")
        self.root.overrideredirect(True)

        self.conn_to_main = conn_to_main

        # Load the not loaded image
        file_dir = "not_loaded.gif"
        if os.name == 'nt':
            file_dir = "\\" + file_dir
        elif os.name == 'posix':
            file_dir = "/" + file_dir
        image = Image.open(os.path.dirname(os.path.realpath(__file__)) + file_dir)  # Replace "music_icon.png" with your image file
        image = image.resize((300, 150))
        self.loading_photo = ImageTk.PhotoImage(image)

        self.progress = 0
        self.emotion = ''
        self.title = ''
        self.currentcolor = '#FFFFFF'
        self.time = time.time()
        self.length = 0

        self.create_widgets()
        self.updateLoading()

    def updateTitle(self, title):
        self.song_name_label.config(text=title)
        self.title = title

    def updateArtist(self, artist):
        self.song_artist_label.config(text=artist)

    def updateProgress(self):
        self.progressbar.config(value=self.progress * 100)

    def _change_progress(self, value):
        self.conn_to_main.send({'action': 'set_position',
                           'position': value})
    
    def _fast_forward(self):
        if self.progress < 0.95:
            self.progress += 0.05
        else:
            self.progress = 0.99
        self.updateProgress()
        self._change_progress(self.progress)
    
    def _fast_backward(self):
        if self.progress > 0.05:
            self.progress -= 0.05
        else:
            self.progress = 0
        self.updateProgress()
        self._change_progress(self.progress)
    
    def updateThumbnail(self, url):
        # Load the image
        image = Image.open(requests.get(url, stream=True).raw)  # Replace "music_icon.png" with your image file
        image = image.resize((300, 150))
        self.photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.photo)
    
    def updateVolume(self, volume):
        self.volume_slider.config(value=volume)

    def changeVolume(self, value):     
        volume = round(float(value))       
        self.conn_to_main.send({'action': 'set_volume',
                                'volume': volume})

    def nextSong(self):
        self.conn_to_main.send({'action': 'next_song'})
        self.title = ''
        self.emotion = ''
        self.updateLoading()

    def pauseAudio(self):
        self.conn_to_main.send({'action': 'pause'})

    def unpauseAudio(self):
        self.conn_to_main.send({'action': 'unpause'})

    def updateEmo(self, emo):
        self.emotion = emo
        self.emo_label.config(text="Detected emotion: " + emo)

    # Dynamic lighting implementation
    def updateEmoColor(self):
        step = 5

        # Set target color based on emo
        target = {'R': 255, 'G': 255, 'B': 255}
        if self.emotion == 'sad':
            target['R'] = 100
            target['G'] = 100
            target['B'] = 100 #Greyish
        elif self.emotion == 'happy':
            target['R'] = 238
            target['G'] = 173
            target['B'] = 34 #yellowish
        elif self.emotion == 'neutral':
            target['R'] = 190
            target['G'] = 190
            target['B'] = 190 #white/gray
        elif self.emotion == 'surprise':
            target['R'] = 107
            target['G'] = 142
            target['B'] = 35 #Greenish / olive green
        elif self.emotion == 'angry':
            target['R'] = 255
            target['G'] = 40
            target['B'] = 40 #Red
        elif self.emotion == 'disgust':
            target['R'] = 255
            target['G'] = 218
            target['B'] = 185 #Brownish
        elif self.emotion == 'fear':
            target['R'] = 255
            target['G'] = 130
            target['B'] = 170 #Pink
            
        rgb = list(ImageColor.getrgb(self.currentcolor))
        
        # Pulsing
        # Red
        if (rgb[0] - target['R'] > 70):
            rgb[0] -= random.randint(1, step)
        elif (target['R'] - rgb[0] > 70):
            rgb[0] += random.randint(1, step)
        else:
            rgb[0] += random.randint(-step, step)
        if (rgb[0] > 255):
            rgb[0] -= step
        elif (rgb[0] < 0):
            rgb[0] += step
        # Green
        if (rgb[1] - target['G'] > 70):
            rgb[1] -= random.randint(1, step)
        elif (target['G'] - rgb[2] > 70):
            rgb[1] += random.randint(1, step)
        else:
            rgb[1] += random.randint(-step, step)
        if (rgb[1] > 255):
            rgb[1] -= step
        elif (rgb[1] < 0):
            rgb[1] += step
        # Blue
        if (rgb[2] - target['B'] > 70):
            rgb[2] -= random.randint(1, step)
        elif (target['B'] - rgb[2] > 70):
            rgb[2] += random.randint(1, step)
        else:
            rgb[2] += random.randint(-step, step)
        if (rgb[2] > 255):
            rgb[2] -= step
        elif (rgb[2] < 0):
            rgb[2] += step

        self.currentcolor = '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])

    # Actually changes the color
    def updateBackgroud(self):
        self.root.config(bg=self.currentcolor)
        self.image_label.config(bg=self.currentcolor)
        self.song_name_label.config(bg=self.currentcolor)
        self.song_artist_label.config(bg=self.currentcolor)
        self.button_row_1.config(bg=self.currentcolor)
        self.button_row_2.config(bg=self.currentcolor)
        self.emo_label.config(bg=self.currentcolor)
        style = ttk.Style()
        style.configure('Vertical.TScale', background=self.currentcolor)
        style.configure('Horizontal.TProgressbar', background=self.currentcolor)

    def liked(self):
        if (self.title == '' or self.emotion == ''):
            return
        self.conn_to_main.send({'action': 'feedbacked', 'isLiked': True, 'emotion': self.emotion})

    def hated(self):
        if (self.title == '' or self.emotion == ''):
            return
        self.conn_to_main.send({'action': 'feedbacked', 'isLiked': False, 'emotion': self.emotion})

    def updateLoading(self):
        self.image_label.config(image=self.loading_photo)
        self.song_artist_label.config(text="Loading")
        self.song_name_label.config(text="Loading")
        if (self.emotion == ''):
            self.emo_label.config(text="Detected Emotion: Loading")
        self.progressbar.config(value=0)

    # Making the entire UI
    def create_widgets(self):

        self.volume_slider = ttk.Scale(self.root, from_=100, to=0, value=100, command=self.changeVolume, orient="vertical", length=400)
        self.volume_slider.pack(side=tk.RIGHT, padx=15, pady=10)

        # Display the image at the top
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=10)

        # Text label for song name
        self.song_name_label = tk.Label(self.root, text="Loading", font=("Arial", 25))
        self.song_name_label.pack(pady=5)

        self.song_artist_label = tk.Label(self.root, text="Loading", font=("Arial", 20))
        self.song_artist_label.pack(pady=5)  # Adjusting vertical padding and anchoring to the left

        self.progressbar = ttk.Progressbar(self.root,
                                           value=0,
                                           mode="determinate",
                                           orient="horizontal",
                                           length=700)
        self.progressbar.pack(padx=10, pady=10)

        # Create buttons
        self.button_row_1 = tk.Frame(self.root)
        self.button_row_1.pack(padx=10, pady=10)

        self.button_row_2 = tk.Frame(self.root)
        self.button_row_2.pack(padx=10, pady=10)

        self.backward_button = tk.Button(self.button_row_1, text="Fast backward", command=self._fast_backward, width=10, padx=5, pady=5, font=("Arial", 14))
        self.backward_button.pack(side=tk.LEFT, padx=5)

        self.play_button = tk.Button(self.button_row_1, text="Play", command=self.unpauseAudio, width=10, padx=5, pady=5, font=("Arial", 14))
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(self.button_row_1, text="Pause", command=self.pauseAudio, width=10, padx=5, pady=5, font=("Arial", 14))
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.forward_button = tk.Button(self.button_row_1, text="Fast forward", command=self._fast_forward, width=10, padx=5, pady=5, font=("Arial", 14))
        self.forward_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.button_row_2, text="Next", command=self.nextSong, width=8, padx=5, pady=5, font=("Arial", 12))
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.like_button = tk.Button(self.button_row_2, text="Like", command=self.liked, width=8, padx=5, pady=5, font=("Arial", 12))
        self.like_button.pack(side=tk.LEFT, padx=5)

        self.dislike_button = tk.Button(self.button_row_2, text="Dislike", command=self.hated, width=8, padx=5, pady=5, font=("Arial", 12))
        self.dislike_button.pack(side=tk.LEFT, padx=5)

        # Create status label
        self.emo_label = tk.Label(self.root)
        self.emo_label.pack(side=tk.BOTTOM, pady=10)

def ui(conn_to_main):
    root = tk.Tk()
    mp = App(root=root, conn_to_main=conn_to_main)
    root.update()
    # IMPORT WHILE FOR UPDATING THE UI ELEMENTS AND RECEIVING + SENDING INFO
    while True:
        if (1 - mp.progress < 0.005):
            # Change UI to loading state when song ends
            mp.updateLoading()
        if (not mp.emotion == '' and time.time() - mp.time > 0.5):
            mp.time = time.time()
            # Update color
            mp.updateEmoColor()
            mp.updateBackgroud()
        # Receiving info
        if conn_to_main.poll():
            info = conn_to_main.recv()
            for key in info:
                if (key == 'position'):
                    mp.progress = info[key]
                    mp.updateProgress()
                if (key == 'title'):
                    mp.updateTitle(title=info[key])
                if (key == 'thumbnailurl'):
                    mp.updateThumbnail(url=info[key])
                if (key == 'length'):
                    mp.length = info[key]
                if (key == 'artist'):
                    mp.updateArtist(artist=info[key])
                if (key == 'volume'):
                    mp.updateVolume(volume=info[key])
                if (key == 'emotion'):
                    mp.updateEmo(emo=info[key])
        # Update UI
        root.update()
