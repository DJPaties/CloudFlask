import requests
import os
import json
import pyaudio  
import wave
# audiofile = r"C:\Users\WOB\Downloads\qs1.wav"
audiofile = r"C:\Users\WOB\Desktop\piper\test1.wav"



url = "https://genix.pythonanywhere.com/api/audio"

# with open(audiofile, 'rb') as fobj:
#     response = requests.post(url, files={'messageFile': fobj})
#     response= response.content.decode()
#     print(response)
    # response = json.loads(response)
    # value = response.get('text')
    # if value is not None:
    #     print(value)
    
import requests

# Define the URL to which you want to send the POST request
url = 'http://127.0.0.1:5000/answer'

json_data = {
    'question': "Hey"
}
json_data = json.dumps(json_data)

# Define headers
headers = {'Content-Type': 'application/json'}

# Send the POST request with the JSON data
response = requests.post(url, data=json_data, headers=headers)

print(response.json())