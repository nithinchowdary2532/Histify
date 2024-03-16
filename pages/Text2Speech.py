import streamlit as st
import os
import time
import glob
import tempfile
from gtts import gTTS
from PyPDF2 import PdfReader
import docx

try:
    os.mkdir("temp")
except:
    pass

LANGUAGES = {
    'English': 'en',
    'Hindi': 'hi',
    'Bengali': 'bn',
    'Korean': 'ko',
    'Chinese': 'zh-cn',
    'Japanese': 'ja',
    # Potentially add more languages here
}

def text_to_speech(output_language, text, tld, slow=False):
    tts = gTTS(text=text, lang=output_language, slow=slow, tld=tld)
    try:
        my_file_name = text[:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name

def read_pdf(file):
    text = ""
    pdf_reader = PdfReader(file)

    for page in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page].extract_text()

    return text

def read_docx(file):
    doc = docx.Document(file)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

remove_files(7)

st.title("Text to Speech")

text_input_method = st.radio("Select the text input method:", ("Type text", "Upload a document"))

if text_input_method == "Type text":
    text = st.text_area("Enter the text you want to convert to speech:")
else:
    file = st.file_uploader("Upload a document (PDF or DOCX):", type=["pdf", "docx"])
    if file:
        if file.type == "application/pdf":
            text = read_pdf(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(file)
    else:
        text = ""

out_lang = st.selectbox(
    "Select your output language",
    tuple(LANGUAGES.keys())
)

tld = ""  # Default value, it can be modified based on accent selection below

english_accent = st.selectbox(
    "Select your English accent",
    (
        "Default",
        "India",
        "United Kingdom",
        "United States",
        "Canada",
        "Australia",
        "Ireland",
        "South Africa",
    ),
)

if english_accent == "Default":
    tld = "com"
elif english_accent == "India":
    tld = "co.in"
elif english_accent == "United Kingdom":
    tld = "co.uk"
elif english_accent == "United States":
    tld = "com"
elif english_accent == "Canada":
    tld = "ca"
elif english_accent == "Australia":
    tld = "com.au"
elif english_accent == "Ireland":
    tld = "ie"
elif english_accent == "South Africa":
    tld = "co.za"

slow_speed = st.checkbox("Slow speed")

if st.button("Convert Text to Speech"):
    if text:
        result = text_to_speech(LANGUAGES[out_lang], text, tld, slow=slow_speed)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Your audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
    else:
        st.warning("Please enter some text or upload a document to convert.")
