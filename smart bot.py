from gtts import gTTS
import os
from playsound import playsound
import tkinter as tk
from tkinter import messagebox

def speak_text():
    text = entry.get()
    if not text.strip():
        messagebox.showerror("Error", "Please enter some text.")
        return

    tts = gTTS(text=text, lang='en')  # You can change lang to 'hi' for Hindi
    filename = "output.mp3"
    tts.save(filename)
    playsound(filename)

# GUI setup
root = tk.Tk()
root.title("Smart Voice Bot – Google TTS")
root.geometry("400x200")

label = tk.Label(root, text="Enter text to speak:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

speak_btn = tk.Button(root, text="Speak (Google TTS)", command=speak_text)
speak_btn.pack(pady=20)

root.mainloop()