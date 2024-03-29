import streamlit as st
import os
import time
import glob
import tempfile
from gtts import gTTS
from PyPDF2 import PdfReader
import docx
import json


page_bg_img="""
<style>
[data-testid="stApp"] {
    opacity: 0.8;
    background-image: url("https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/fd6a542d-ade9-45c7-afed-38d6dde42ed3/det8vca-35996a6f-d2fc-4c75-92cb-ff3e17e346eb.png/v1/fill/w_1280,h_720,q_80,strp/sunset_gradient_wallpaper_3840_x_2160_4k_by_themusicalhypeman_det8vca-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NzIwIiwicGF0aCI6IlwvZlwvZmQ2YTU0MmQtYWRlOS00NWM3LWFmZWQtMzhkNmRkZTQyZWQzXC9kZXQ4dmNhLTM1OTk2YTZmLWQyZmMtNGM3NS05MmNiLWZmM2UxN2UzNDZlYi5wbmciLCJ3aWR0aCI6Ijw9MTI4MCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.bT1n6nWrYxubG7TiqrvShc4cGD1_FpCeSzcrXIWTuE8");
    background-repeat: repeat;
}
</style>
"""
st.markdown (page_bg_img, unsafe_allow_html=True)

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

def import_keypoints():
    try:
        with open("MainPoints.json", "r") as json_file:
            data = json.load(json_file)
            story_data = data.get("information", [])
            return story_data
    except FileNotFoundError:
        print("File not found. No data imported.")
        return []

keypoints = import_keypoints()

def import_story():
    try:
        with open("story.json", "r") as json_file:
            data = json.load(json_file)
            story_data = data.get("story", [])
            return story_data
    except FileNotFoundError:
        print("File not found. No data imported.")
        return []

story = import_story()


def text_to_speech(output_language, text, tld, slow=False):
    tts = gTTS(text=text, lang=output_language, slow=slow, tld=tld)
    try:
        my_file_name = "audio"
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
    st.header("Main Points")
    text  = keypoints
    st.write(text)
    
else:
    st.header("Story Time")
    text  = story
    st.write(text)

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
