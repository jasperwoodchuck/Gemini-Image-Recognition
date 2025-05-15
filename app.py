import os
import cv2
import google.generativeai as genai
from flask import Flask, render_template, Response
import PIL.Image
import threading
import pyttsx3

PROMPT = "What's in the image (in 10 words)?"
API_KEY = os.getenv("GEMINI_API_KEY") #"AIzaSyCWjo7_g2buhRwF73HXNMfaW7wXlDdNR5o"
IMAGE_PATH = "img.jpg"

genai.configure(api_key=API_KEY)

APP = Flask(__name__)

LAST_FRAME = None

def captionImage(image_path:str = None) -> str:
    if image_path is None:
        image_path = IMAGE_PATH

    model = genai.GenerativeModel()
    image = PIL.Image.open(image_path)

    caption = model.generate_content([PROMPT, image])

    return caption.text

def saveAndCaptionImage(image_path:str = None, frame=None) -> str:
    if frame is None:
        raise Exception("Image isn't available to caption")

    cv2.imwrite(image_path, frame)
    return captionImage(image_path)

def gen_frame():
    video = cv2.VideoCapture(0)

    video.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    

    while True:
        ret, frame = video.read()
        if not ret:
            raise Exception("Failed to grab frame")

        global LAST_FRAME
        LAST_FRAME = frame

        _, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
        
def speak_caption(text: str):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

@APP.route('/')
def index():
    return render_template('index.html')

@APP.route('/video_feed')
def video_feed():
    return Response(gen_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@APP.route('/generate_caption')
def generate_caption():
    if LAST_FRAME is not None:
        caption = saveAndCaptionImage(IMAGE_PATH, LAST_FRAME)

        threading.Thread(target=speak_caption, args=(caption,)).start()

        return caption
    return "No frame captured!"

if __name__ == "__main__":
    APP.run(debug=True, threaded=True)
