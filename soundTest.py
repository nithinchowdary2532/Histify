from gtts import gTTS
import playsound
from langdetect import detect

def text_to_speech(text  ):
    tts = gTTS(text=text, lang= 'en')
    tts.save("output.mp3")
    playsound.playsound("output.mp3")

def main():
    print("Enter the text you want to convert to speech:")
    text = input()
    
    # Detect language
    lang = detect(text)
    print(type(lang))
    print(f"Detected language: {lang}")
    
    text_to_speech(text ,)

if __name__ == "__main__":
    main()
