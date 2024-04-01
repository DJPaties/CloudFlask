from flask import Flask,request, jsonify
import json
import TTSfunctions
import chatbot.chatcopy as ch
import subprocess
import os
from langdetect import detect_langs
from pydub import AudioSegment
from flask_cors import CORS
from base64 import b64decode
import io
import soundfile
from werkzeug.utils import secure_filename
import subprocess
import speech_recognition as sr



app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import os
from google.cloud import texttospeech
import glob
import time
import wave
def tts(response_message,lang_code):

    print("TTS")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'tts.json'
    try:        
        
        client = texttospeech.TextToSpeechClient()
        print("Client created successfully.")
    except Exception as e:
        print("Error:", str(e))
    print("TTS")
    text = '<speak>'+""+response_message['text']+""+'</speak>'
    synthesis_input = texttospeech.SynthesisInput(ssml=text)
    
    try:
        if lang_code == "en-US" or lang_code=="en":
            voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code ,
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        )
            audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3,
                    )
            response = client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config,
                    )


            filename = 'audioEnglish.wav'
            with open(f'static/{filename}', 'wb') as out:
                out.write(response.audio_content)
    
    #if lamguage is arabic then a whole new process is written 
        else:

            name = "ar-XA-Standard-B"
            text_input = texttospeech.SynthesisInput(text=response_message['text'])
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="ar-XA", name=name
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

            response = client.synthesize_speech(
                input=text_input,
                voice=voice_params,
                audio_config=audio_config,
            )
            

            filename = f"audioArabic.wav"
            print(filename)
            with open(f'static/{filename}', "wb") as out:
                out.write(response.audio_content)
                print(f'Generated speech saved to "{filename}"')
        
    except Exception as e:
        print("Error occured ", e)


@app.route("/",methods=['POST'])
def hello_world():
    print("Entered")
    response = request.json
    ans = response.get('language')
    print(ans)
    data = {
    "success": True,
    "audio_name": ans,
    }   
    return json.dumps(data)


@app.route("/answer_audio_web", methods=['POST'])
def get_audio_web():
    if request.method == 'POST':
        # try:
        try:
            os.remove(os.path.join('static/filename.wav'))
        except FileNotFoundError:
            print("File Not found Yet")
            pass
            
        audio_data = request.data
        # print(audio_data)
        # print(request.form)
        
        decoded_data = audio_data.decode()

        json_decoded_data = json.loads(decoded_data)
        # decoded_data = decoded_data.replace("\"","")
        # decoded_data = decoded_data.replace("{","")
        # decoded_data = decoded_data.replace("base64data:","")

        print(json_decoded_data['base64data'])

        dataAduio = b64decode(json_decoded_data['base64data'])
        print((dataAduio))

        with open('static/receivedSouzane.webm',mode="wb") as fi:
            fi.write(dataAduio)

            # import subprocess

    # Define the path
        path = r'C:\Users\WOB\Documents\testFlask\api\static'

        # Run the ffmpeg command to convert the webm file to wav
        process = subprocess.Popen(['ffmpeg', '-i', r'C:/Users/WOB/Documents/testFlask/api/static/receivedSouzane.webm', r'C:/Users/WOB/Documents/testFlask/api/static/filename.wav'], shell=True)

        # Wait until the process is finished
        process.communicate()

        def transcribe_audio_wav(lang):
            r = sr.Recognizer()
            # open the file
            try:
                
                with sr.AudioFile("static/filename.wav") as source:
                    # listen for the data (load audio to memory)
                    audio_data = r.record(source)
                    # recognize (convert from speech to text)
                    text = r.recognize_google(audio_data,language=lang)
                    print(text)
                    return text
            except sr.exceptions.UnknownValueError as e:
                text = str(e)
                print(e)

        print(f"Languague is {json_decoded_data['language']}")
        text = transcribe_audio_wav(json_decoded_data['language'])

        return jsonify({"success": True, "text": text}), 200




@app.route("/answer_audio",methods=['POST','GET'])
def get_audio():

    if 'messageFile' in request.files:
            file_result = request.files['messageFile']
            file_result.save("static/received.wav")
            print("File saved successfully.")
    else:
        print("No file found in the request.")
    # lang_result = TTSfunctions.transcribe_audio_wav('en')

    # Check if JSON data is included in the request
    print(request.form)
    if request.form:
        json_data = request.form.get('language')
        
        print("Language:", json_data)
        # Perform actions based on JSON data
        # Example: Call a function to process the JSON data
        lang_result = TTSfunctions.transcribe_audio_wav(json_data)
        
       
        
    else:
        print("No JSON data found in the request.")

    answer = ch.receive_message(lang_result)
    
    answer = json.loads(answer)
    tts(answer,json_data)
    print("SLDKFOJSDNFOUPSNFDOUPJSDFUOSF",  json_data)
    
    audio_name = ""
    if json_data == "ar":
        audio_name = "audioArabic.wav"
    elif json_data == "en":
        audio_name == 'audioEngish.wav'
        
    answer['audio_path'] = f"http://192.168.1.158:5000/static/{audio_name}"
    print(answer['audio_path'])
    
    return json.dumps(answer)

@app.route("/answer",methods=["POST","GET"])
def get_answer():
    print("/ANSWER")
    resp2 = request.get_json()
    # resp2 = request.form['build']
    print(resp2)
    
    #For Langauge Detection uncomment this block and configure it
    try:
        langs = detect_langs(resp2['question'])
       
        detectedlang = max(langs).lang
    except: detectedlang =  "err" 
    
    answer = ch.receive_message(resp2['question'])
    answer = json.loads(answer)
    print(detectedlang) 
    if detectedlang == 'en':
        answer['audio_path']="http://192.168.1.158:5000/static/audioEnglish.wav"
        tts(answer,"en-US")
    elif detectedlang == "ar":
        answer['audio_path']="http://192.168.1.158:5000/static/audioArabic.wav"
        tts(answer,"ar-LB")
    else:
        answer['audio_path']="http://192.168.1.158:5000/static/audioEnglish.wav"
        tts(answer,"en-US")

    return json.dumps(answer)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))