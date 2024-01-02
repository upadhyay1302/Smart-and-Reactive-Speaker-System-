# Smart and Reactive Speaker System 

Embedded system - consisting of a small display, speaker, and camera. The camera would scan the user’s face for a dominant emotion- which is used to select music associated with 
that emotion. Relevant information would be displayed: music, mood, volume. 

All the operations are run on the PI. A GUI was properly implemented.

User feedback will be used to dictate which songs are more suitable for which moods. User feedback is taken into account for each song and stored for future applications and 
improvements on song-emotion association. We have a Like-Dislike button for the same purpose.

Dynamic screen lighting which changes based on emotion of song playing and audio level. Dynamic lighting has been incorporated with the screen color changing relative to the user’s
perceived emotion. The color also pulses as the song plays to give a sense of liveliness to the user experience.

The system was designed from the very beginning to be very modular and feature modules that we can add and remove at any point in time. The composition of the system thus contains: 

## Main Module: 
The main module is responsible for starting the system and linking all other modules together into a cohesive and unified system. When the OS boots up, a shell script which sets 
up the running environment and calls the main module is run. The main module, which was called by the shell script, starts up and begins initializing the backend, UI and emotion 
detection modules. These modules are run as sub-processes (using Python’s built-in subprocess module) of the main module to allow for responsive and parallel processing. 
The communication being the modules is handled using Pipes() (from the subprocess module) which is a part of the sub-processes. The main module acts as the main control and 
communication hub. Any inter-module information needing to be sent will first be sent from the origin module to the main module which will then be processed and forwarded to the 
destination module. This configuration allowed for enhanced flexibility of the system and easier debugging. Different modules can be developed semi-independently from each other 
as they can rely on the main module to resolve any differences being the modules. 

## Backend Module: 

The backend module consists of the music recommendation subsystem, the audio subsystem and the feedback subsystem. The backend would receive commands or “orders” from the main 
module which would then trigger certain functions of certain subsystems. When an emotion is detected, the music recommendation subsystem, as the name suggests, would recommend a
certain song based on that emotion. The backend module would receive the emotion information from the main module which would then trigger the look up of a song for that
particular mood using the YouTube Music API (ytmusicapi and yt-dlp) and set that as the song to play. Then the audio subsystem would then be triggered to play the song over the 
internet (streaming) using VLC (python-vlc). The reason VLC was chosen to be the audio player is because the VLC player has great control over the audio stream and that it is 
significantly less resource intensive than, for example, a browser. After the song is set, its information such as the title, artist, etc. is sent back to the main module to be 
sent to the UI module for displaying. When any audio commands were received, the backend would then translate those commands into VLC commands to manipulate the audio. 
When feedback commands (like/dislike) were received, the feedback subsystem would then record the currently playing song’s information such as videoId, playtime, percentage 
listened, and the feedback itself into a JSON file on the disk. This would be analyzed to better recommend songs in the future. 

## Emotion Detection Module: 

The emotion detection module is responsible for detecting the user’s expression and emotion. This is done using OpenCV and Deepface, a library created by Meta to detect emotions. 
When the module is called, it uses OpenCV to capture video source of the user’s face (from the laptop webcam, external webcam, etc). Next, each frame is read in grayscale and 
passed to the Deepface library which returns many emotions, each with a corresponding float value from 0-1, based on the dominance of each emotion. The most dominant emotion 
(the emotion with the greatest float value) is then transported to the main module so that it can be forwarded to both the backend and the UI module. 

## UI Module: 

The UI module is responsible for rendering the UI, displaying relevant information and showcasing the dynamic lighting feature. 
The UI module, at start up, will render a basic UI using Tkinter (for performance reasons). Once the UI module receives updated song information and emotion state, the UI will 
responsively update to reflect the new information. The dynamic lighting feature will consume the received emotion state to dynamically set a target color to change to for a 
specific emotion. The background and UI elements would then slowly change to the new color. Once the target color is reached, the color would then pulse slowly around the target
color to give a feeling of liveliness to the user. Due to time constraints, reactive color based on loudness was not implemented. Any user input would trigger callback functions 
which would send relevant commands or information back to the main module to be processed or forwarded. 


## Programming language: Python – BSD License 
## Library used: opencv-python, deepface, yt-dlp, ytmusicapi, python-vlc, Pillow, Tkinter 

Tkinter: Python/BSD License 
Pillow: HPND License 
python-vlc: LGPLv2+ License 
ytmusicapi, deepface: MIT License 
yt-dlp: Public Domain 
opencv-python: Apache 2.0 

Considering all the different licenses, their common ground and the most restrictive conditions, I have decided to open source our code with the Apache 2.0 License.

## Professionalism: 

There are no apparent or serious security issues with the system. 
Privacy is also considered as we do not store user biometric date or any recording of the user. Song feedback is only considered with respect to song and not individual users.  

 
