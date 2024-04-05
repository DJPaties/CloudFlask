import random
import json
import torch
import os
from chatbot.model import NeuralNet
from chatbot.nltk_utils import bag_of_words, tokenize
import requests
from sentence_transformers import SentenceTransformer, util
import chatbot.chatgpt as chatgpt


global run_once
run_once = True
#load the text:
# Get the current script directory
script_dir = os.path.dirname(__file__)
json_path = os.path.join(script_dir, 'intents.json')

# Load JSON data from file
with open(json_path, 'r',encoding='utf-8') as file:
    data = json.load(file)

# Extract and print patterns
all_patterns = []
for intent in data['intents']:
    all_patterns.extend(intent['patterns'])
print(all_patterns)

#load the comparison model
api_token ="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"
API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/paraphrase-MiniLM-L6-v2"
# API_URL = API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": f"Bearer {api_token}"}

def query(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
    except ValueError as e:
        print(e)

    return response.json()

device = torch.device('cuda')#if torch.cuda.is_available() else 'cpu')

with open('chatbot/intents.json', 'r', encoding="utf8") as json_data:
    intents = json.load(json_data)

FILE = "chatbot/data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"
print("Let's chat! (type 'quit' to exit)")

# embedder = SentenceTransformer('sentence-transformers/bert-base-nli-mean-tokens').to(device)
embedder = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v1').to(device)
corpus_embeddings = embedder.encode(all_patterns, convert_to_tensor=True).to(device)
def search(msg):    
    # Query sentences:
    queries = [msg]


    # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
    top_k = min(1, len(all_patterns))
    for query in queries:
        query_embedding = embedder.encode(query, convert_to_tensor=True)

        # We use cosine-similarity and torch.topk to find the highest 5 scores
        cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
        top_results = torch.topk(cos_scores, k=top_k)

        for score, idx in zip(top_results[0], top_results[1]):
            print(all_patterns[idx], "(Score: {:.4f})".format(score))
            
        print(all_patterns[idx])
        return all_patterns[idx], "{:.4f}".format(score)

 

def receive_message(input_question):
    
    sentenceinput = input_question

    print(f"Received message from user: {sentenceinput}")
    print(sentenceinput)
    if sentenceinput == "quit":
        exit()
    print("enter query")
    try:
        data, score = search(sentenceinput)
        if float(score)<0.7:
            # response = chatgpt.chat(sentenceinput)
            data = {
                'success': True,
                'intent': "error",
                'text': "Question not found in the databse say another law"
                # "audio_path": "http://192.168.1.158:5000/static/test1.wav"
            }
            data = json.dumps(data)
            return data
        
        sentence = data
        print(sentence)
        
    except ValueError as e:
        print(e)
        
    # print("after data")
    sentence = tokenize(sentence)
    # print("Tokenize")
    # print(sentence)
    # sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    
    if prob.item() > 0.7:
        # print(prob.item())
        for intent in intents['intents']:
            if tag == intent["tag"]:
                print(f"{intent['tag']}")
                x = (f"{random.choice(intent['responses'])}")
                print("THIS IS THE ANSWER",x)
                message = {
                    'success': True,
                    "text": x,
                    "intent": intent['tag'],
                    # "audio_path": "http://192.168.1.158:5000/static/test1.wav"
                }
                data = json.dumps(message)
                # tts(x,"ar-LB")
                
                return data
    else:
        print(f"{bot_name}: I do not understand...")
        data = {
                    'error': True,
                    "text": f"{bot_name}: I do not understand...",
                    "intent":"error",
                    "audio_path": "http://192.168.1.158:5000/static/test1.wav"
                }
        return json.dumps(data)

# if run_once:
#     receive_message()


    
