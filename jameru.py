from datetime import datetime
from logging.config import listen
import speech_recognition as sr
import pyttsx3 
import webbrowser
import wikipedia
import wolframalpha
import pyaudio
 
# Speech engine initialisation
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # 0 = male, 1 = female
activationWord = 'Jameru' # Single word
 
# Configure browser
# Set the path
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
 
# Wolfram Alpha client
appId = '5R49J7-J888YX9J2V'
wolframClient = wolframalpha.Client(appId)
 
def speak(text, rate = 120):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()
 
def parseCommand():
    listener = sr.Recognizer()
    print('What can I do to you today?')
 
    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)
 
    try: 
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en_gb')
        print(f'Master: {query}')
    except Exception as exception:
        print('Master, I did not catch that one.')
        speak('Master, I did not catch that one.')
        print(exception)
        return 'None'
 
    return query
 
def search_wikipedia(query = ''):
    searchResults = wikipedia.search(query)
    if not searchResults:
        print('No wikipedia result')
        return 'No result received'
    try: 
        wikiPage = wikipedia.page(searchResults[0])
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary
 
def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']
 
def search_wolframAlpha(query = ''):
    response = wolframClient.query(query)
 
    # @success: Wolfram Alpha was able to resolve the query
    # @numpods: Number of results returned
    # pod: List of results. This can also contain subpods
    if response['@success'] == 'false':
        return 'Could not compute'
    
    # Query resolved
    else:
        result = ''
        # Question 
        pod0 = response['pod'][0]
        pod1 = response['pod'][1]
        # May contain the answer, has the highest confidence value
        # if it's primary, or has the title of result or definition, then it's the official result
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            # Get the result
            result = listOrDict(pod1['subpod'])
            # Remove the bracketed section
            return result.split('(')[0]
        else: 
            question = listOrDict(pod0['subpod'])
            # Remove the bracketed section
            return question.split('(')[0]
            # Search wikipedia instead
            speak('Computation failed. Querying universal databank.')
            return search_wikipedia(question)
 
 
 
# Main loop
if __name__ == '__main__':
    speak('Master, Jameru`s sytem is ready.')
 
    while True:
        # Parse as a list
        query = parseCommand().lower().split()
 
        if query[0] == activationWord:
            query.pop(0)
 
            # List commands
            if query[0] == 'say':
                if 'hello' in query:
                    speak('Greetings, all.')
                else: 
                    query.pop(0) # Remove say
                    speech = ' '.join(query)
                    speak(speech)
 
            # Navigation
            if query[0] == 'go' and query[1] == 'to':
                speak('Opening...Please wait...')
                query = ' '.join(query[2:])
                webbrowser.get('edge').open_new(query)
 
            # Wikipedia 
            if query[0] == 'search':
                query = ' '.join(query[1:])
                speak('Searching for queries... Please wait...')
                speak(search_wikipedia(query))
                
            # Wolfram Alpha
            if query[0] == 'compute' or query[0] == 'Jameru':
                query = ' '.join(query[1:])
                speak('Computing')
                try: 
                    result = search_wolframAlpha(query)
                    speak(result)
                except:
                    speak('Unable to compute.')
 
            # Note taking
            if query[0] == 'log':
                speak('Ready to record your note')
                newNote = parseCommand().lower()
                now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                with open('note_%s.txt' % now, 'w') as newFile:
                    newFile.write(newNote)
                speak('Note written')
 
            if query[0] == 'exit':
                speak('Goodbye, I`m glad to serve you today.')
                break