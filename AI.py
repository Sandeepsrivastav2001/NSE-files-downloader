import speech_recognition as sr
import pyttsx3
from openai import OpenAI
import datetime

openai_api_key = "YOUR_OPENAI_API_KEY"
client = OpenAI(api_key=openai_api_key)

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def ask_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content":prompt}]
    )
    return response.choices[0].message.content.strip()

while True:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
            query = recognizer.recognize_google(audio, language='en-IN')
            print("You said:", query)

            if "time" in query.lower():
                time_str = datetime.datetime.now().strftime("%H:%M")
                speak(f"The time is {time_str}")
            else:
                answer = ask_gpt(query)
                speak(answer)

    except Exception as e:
        print("Error:", e)
