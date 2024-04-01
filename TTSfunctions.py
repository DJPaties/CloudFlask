import speech_recognition as sr


def transcribe_audio_wav(lang):
    r = sr.Recognizer()
    # open the file
    with sr.AudioFile("static/received.wav") as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data,language=lang)
        print(text)
        return text