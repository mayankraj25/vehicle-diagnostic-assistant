import pyttsx3
import threading

engine = pyttsx3.init()

engine.setProperty("rate", 165)   
engine.setProperty("volume", 0.9)

voices = engine.getProperty("voices")
for voice in voices:
    if "samantha" in voice.name.lower() or "karen" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        print(f"Using voice: {voice.name}")
        break

def speak(text):
    print(f"Speaking: {text}")
    engine.say(text)
    engine.runAndWait()