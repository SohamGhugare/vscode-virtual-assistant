import vscode
import pyttsx3
import random
import requests
from datetime import datetime
import wikipedia
import webbrowser


""" Obtain your own API_KEY from https://api.pgamerx.com/register (Shoutout to PGamerX for making the API)
    Note: You need to pass in the API_KEY as a header while requesting the API"""
API_KEY = "BwnlIBuo6kzz"
API_URL = "https://api.pgamerx.com/v4/ai?message=" # Append the message to the url (done in the `get_ai_response` function)

headers = {'x-api-key' : API_KEY}

""" Initialising tts engine and setting voice property to in-built male voice. """
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 140)

""" Speak function that converts string to audio """
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

""" Greet function based on current time """
def greet():
    time = int(datetime.now().hour)
    if time >= 0 and time < 12:
        speak("Hello, Good Morning!")
    elif time >= 12 and time <= 18:
        speak("Hi, Good Afternoon!")
    else:
        speak("Hey, Good Evening!")
    speak("I am your Virtual Assistant, how can I help you today?")

""" Wikipedia search function that is triggered when you pass in the keyword 'wikipedia' while chatting with the jarvis """
def search_wiki(query:str):
    search_res = wikipedia.search(query, results = 10)
    data=[]

    for res in search_res:
        title = str(res)
        option = vscode.ext.QuickPickItem(
            label = title,
            detail = None,
            link = f"https://en.wikipedia.org/wiki/{title}"
        )
        data.append(option)

    if len(data) == 0:
        return vscode.window.show_error_message("No Search Results Were Found... Please try again.")

    speak("Here's what I found!")
    options = vscode.ext.QuickPickOptions(match_on_detail=True)
    selected = vscode.window.show_quick_pick(data, options)
    
    if not selected:
        return

    webbrowser.open(selected.link)

""" Fetching AI Response from the API """
def get_ai_response(message:str) -> str:
    res = requests.get(API_URL+message, headers=headers)
    return res.json()[0]['message']


""" Creating a vscode extension instance """
ext = vscode.Extension(
    name="vscode-jarvis",
    display_name = "VS Code Virtual Assistant",
    version = "0.0.1",
    description = "An interactive virtual assistant with in-built AI chat responder. You can ask it questions, ask for a joke, casually chat with it, and do lots of more stuff."
)


@ext.command()
def about():
    return vscode.window.show_info_message('Hello, I am your Virtual Assistant. You can chat with me by executing `>Chat` command! Hope you enjoy having fun with me. Have a good day!')

""" Chat responding feature based on an API, also looks for specific keywords like 'wikipedia', etc """
@ext.command()
def chat():

    wiki_keywords = ['wikipedia', 'wiki']
    greet_keywords = ['hello', 'hey', 'hi', 'hemlo', 'hola', 'hoi']
    responding = False

    while not responding:
        input_box = vscode.InputBoxOptions(title="Listening.... ")
        res = vscode.window.show_input_box(input_box)

        if not res:
            return

        for word in wiki_keywords:
            if word in [w.lower() for w in res.split()]:
                responding = True
                speak("Searching, please wait.")                     
                search_wiki(res.replace(word, ''))
                

        for word in greet_keywords:
            if word in [w.lower() for w in res.split()]:
                responding = True
                greet()
                res.replace(word, '')

        if not responding:            
            ai_res = get_ai_response(res)
            speak(ai_res)

        responding = False

vscode.build(ext)