from multiprocessing import Process, Pipe
from backend import backend
from emotiondection import emotion_detect
from ui import ui

if __name__ == '__main__':
    # Start UI module
    conn_to_ui,conn_to_main = Pipe()
    backend_process = Process(target=ui, args=(conn_to_main,))
    backend_process.start()
    # Start backend module
    conn_to_backend,conn_to_main = Pipe()
    backend_process = Process(target=backend, args=(conn_to_main,))
    backend_process.start()
    # Start emo dection module
    conn_to_emotion_detection,conn_to_main = Pipe()
    backend_process = Process(target=emotion_detect, args=(conn_to_main,))
    backend_process.start()
    # Init emo check
    conn_to_emotion_detection.send({'action': 'get_emotion'})
    emotion = ''
    position = -1
    enddecting = False
    shouldnextsong = True
    # Very very important while loop to send and receive + process info
    while True:
        if (emotion != '' and shouldnextsong):
            conn_to_backend.send({'action': 'set_new_mood', 'mood': emotion})
            conn_to_ui.send({'emotion': emotion})
            emotion = ''
            enddecting = False
            shouldnextsong = False
            continue
                
        # Receiving info
        if conn_to_backend.poll():
            info = conn_to_backend.recv()
            sending_info = {}
            for key in info:
                if (key == 'position'):
                    position = info[key]
                    if (position > 0.9 and enddecting == False):
                        conn_to_emotion_detection.send({'action': 'get_emotion'})
                        enddecting = True
                    if (position == -1 or position == 1 or 1 - position < 0.0025):
                        shouldnextsong = True
                    sending_info['position'] = position
                if (key == 'title'):
                    sending_info['title'] = info[key]
                if (key == 'thumbnailurl'):
                    sending_info['thumbnailurl'] = info[key]
                if (key == 'length'):
                    sending_info['length'] = info[key]
                if (key == 'artist'):
                    sending_info['artist'] = info[key]
                conn_to_ui.send(sending_info)
        if conn_to_emotion_detection.poll():
            info = conn_to_emotion_detection.recv()
            for key in info:
                if (key == 'emotion'):
                    emotion = info[key]
        if conn_to_ui.poll():
            order = conn_to_ui.recv()
            if (order['action'] == 'next_song'):
                conn_to_backend.send({'action': 'pause'})
                conn_to_emotion_detection.send({'action': 'get_emotion'})
                enddecting = True
                shouldnextsong = True
                continue

            sending_info = {'action': order['action']}
            if (order['action'] == 'set_volume'):
                sending_info['volume'] = order['volume']
            elif (order['action'] == 'set_position'):
                sending_info['position'] = order['position']
            elif (order['action'] == 'feedbacked'):
                sending_info['emotion'] = order['emotion']
                sending_info['isLiked'] = order['isLiked']
            conn_to_backend.send(sending_info)
