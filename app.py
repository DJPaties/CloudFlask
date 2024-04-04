from flask import Flask,request, jsonify
import json
import TTSfunctions
import chatbot.chatcopy as ch
import subprocess
import os
from langdetect import detect_langs
from flask_cors import CORS
from base64 import b64decode

import subprocess
import speech_recognition as sr



app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
temp_answers = {}
import os
from google.cloud import texttospeech
import glob
import time
import wave
def tts(response_message,lang_code,userId):

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


            # filename = 'audioEnglish.wav'
            filename = f'{userId}-text.wav'
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
            

            # filename = f"audioArabic.wav"
            filename = f'{userId}-textAr.wav'
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


@app.route("/get_audio_web", methods=['POST','GET'])
def get_audio_web():
    if request.method == "GET":
        userID = request.args.get('id')

        # print("USRE IDDD:",userID)
        # print("USRE IDDD:",request.data)
        print("USRE IDDD:",userID)
        # print ()
        print(temp_answers[int(userID)])
        return jsonify(temp_answers[int(userID)])
        


@app.route("/post_audio_web", methods=['POST'])
def post_audio_web():
    if request.method == 'POST' or request.method=='GET':
        # try:
        
            
        audio_data = request.data

        decoded_data = audio_data.decode()

        json_decoded_data = json.loads(decoded_data)
        dataAduio = b64decode(json_decoded_data['base64data'])
        # print((dataAduio))
        print("Audio Decoded")
        userId = json_decoded_data['id']
        try:
            os.remove(os.path.join(f'static/{userId}.wav'))
        except FileNotFoundError:
            print("File Not found Yet")
            pass
        
        with open(f'static/{userId}.webm',mode="wb") as fi:
            fi.write(dataAduio)

            # import subprocess

    # Define the path
        path = r'C:\Users\WOB\Documents\testFlask\api\static'

        # Run the ffmpeg command to convert the webm file to wav
        # process = subprocess.Popen(['ffmpeg', '-i', f'C:\Users\WOB\Documents\testFlask\api\static\{userId}.webm' , f'C:\Users\WOB\Documents\testFlask\api\static\{userId}.wav'], shell=True)
        # Define the FFmpeg command as a list of strings
        process = subprocess.Popen([
            'ffmpeg',
            '-i', f'C:\\Users\\WOB\\Documents\\testFlask\\api\\static\\{userId}.webm',
            f'C:\\Users\\WOB\\Documents\\testFlask\\api\\static\\{userId}.wav'
        ], shell=True)
        # Wait until the process is finished
        process.communicate()

        def transcribe_audio_wav(lang):
            r = sr.Recognizer()
            # open the file
            try:
                
                with sr.AudioFile(f"static/{userId}.wav") as source:
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
        
    
        answer = ch.receive_message(text)
        answer = json.loads(answer)
        audio_generate = {'text':answer['text']}
        tts(audio_generate,json_decoded_data['language'],userId)
        if json_decoded_data['language'] == 'en':
            answer['audio_path']=f"http://192.168.1.158:5000/static/{userId}-textAr.wav"
            
        elif json_decoded_data['language'] == "ar":
            answer['audio_path']=f"http://192.168.1.158:5000/static/{userId}-textAr.wav"
        answer['type'] = "audio"
        # return json.dumps(answer)
        temp_answers[userId] = answer
        print(temp_answers)
        return jsonify({"success": True}), 200




@app.route("/answer_audio",methods=['POST','GET'])
def get_audio():

    if 'messageFile' in request.files:
            file_result = request.files['messageFile']
            file_result.save("static/received.wav")
            print("File saved successfully.")
    else:
        print("No file found in the request.")

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
    answer['type'] = "audio"
    
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
    except: detectedlang =   "err" 
    
    userID = resp2['id']
    answer = ch.receive_message(resp2['question'])
    answer = json.loads(answer)
    print(detectedlang) 
    if detectedlang == 'en':
        # model_path = 'en_US-lessac-medium.onnx'
        # model_json_path = 'en_en_US_lessac_medium_en_US-lessac-medium.onnx.json'
        answer['audio_path']=f"http://192.168.1.158:5000/static/{userID}-text.wav"
        tts(answer,"en-US",userID)
    elif detectedlang == "ar":
        # model_path = 'ar_JO-kareem-medium.onnx'
        # model_json_path = 'ar_ar_JO_kareem_medium_ar_JO-kareem-medium.onnx.json'
        answer['audio_path']=f"http://192.168.1.158:5000/static/{userID}-textAr.wav"
        tts(answer,"ar-LB",userID)
    else:
        model_path = 'en_US-lessac-medium.onnx'
        model_json_path = 'en_en_US_lessac_medium_en_US-lessac-medium.onnx.json'
        answer['audio_path']=f"http://192.168.1.158:5000/static/{userID}-text.wav"
        tts(answer,"en-US",userID)
    
    answer['type'] = "text"

    return json.dumps(answer)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))