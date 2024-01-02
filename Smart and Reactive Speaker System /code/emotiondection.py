import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import cv2
from deepface import DeepFace

def emotion_detect(conn_to_main):
    # Classifier gives (x,y), width and height
    face_classifier = cv2.CascadeClassifier()
    file_dir = "haarcascade_frontalface_default.xml"
    if os.name == 'nt':
        file_dir = "\\" + file_dir
    elif os.name == 'posix':
        file_dir = "/" + file_dir
    face_classifier.load(cv2.samples.findFile(os.path.dirname(os.path.realpath(__file__)) + file_dir))

    # Capture video source (laptop webcam, external webcam, etc)
    cap = cv2.VideoCapture(0)

    # Bigus while loop for sending and receiving info
    while True:
        if (conn_to_main.poll()):
            order = conn_to_main.recv()
            if (order['action'] == 'get_emotion'):
                ret, frame = cap.read()
                # RGB to grayscale then pass to classifier
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(frame_gray)

                # Give deepface an image so that it returns an emotion
                response = DeepFace.analyze(frame, actions=("emotion",), enforce_detection=False)

                conn_to_main.send({'emotion': response[0]['dominant_emotion']})

                continue
            elif (order['action'] == 'terminate'):
                cap.release()
                cv2.destroyAllWindows()
                
                conn_to_main.send({'result': 'ok'})
