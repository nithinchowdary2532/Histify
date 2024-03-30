import os
import PyPDF2
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
import replicate
from PIL import Image
import requests
from gtts import gTTS
import json
import time
from io import BytesIO
from generate_quiz import generate_quiz_data, import_title
import easyocr as ocr
import numpy as np
from easyocr import Reader
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

if not firebase_admin._apps:
    cred = credentials.Certificate(r"serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

page_bg_img="""
<style>
[data-testid="stApp"] {
    opacity: 0.8;
    background: rgb(148,0,150);
    background: linear-gradient(0deg, rgba(148,0,150,1) 0%, rgba(0,0,80,1) 100%);
    background-repeat: repeat;
}
</style>
"""
st.markdown (page_bg_img, unsafe_allow_html=True)


# Load environment variables
on = st.toggle('OpenDyslexic')
if on:
    with open("style.css") as css:
        st.markdown(f'<style>{css.read()}</style>' , unsafe_allow_html= True)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PDFS_DIR = "pdfs"

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
api = replicate.Client(api_token=REPLICATE_API_TOKEN)
st.sidebar.image("images/newlogo.jpg", use_column_width=True)

# Initialize language model and summarization chains
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
prompt = PromptTemplate.from_template(
    "You are a text summarizer. You will be given a pdf of a subject chapter, give my the description of each subtopic in points and explain them. Mention any important dates, formulae or methodologies if given. The data should be such that reading the keypoints would need to give me an entire jist of the chapter with the important pointers. After each heading mention the important dates given or the important formaule along with their significance or the functionality. The dates or formulae should not be missed if there are some. And and the end make a seperate column for all the dates and formuale along with their significance. Also return the title of the data given. The data is given here : {topic}.")
prompt2 = PromptTemplate.from_template(
    "You are a story maker. You will be fed some key points of a subject. Your task is to covert these key points into an interative fun story which will help even a grade schooler understand the subject data given. Make sure to include all the necessary information and dont leave any behind. Make sure it is simillar to a novel, without pointers. Make the story for each subtopic atleast 3 to 4 pages long, in a pragraph format. If there are any important information such as dates or formula, incorporate them into the story. Make sure that the story clearly explains the subject through the story. Also add the title. The keypoints are given here : {keypoints}")
prompt3 = PromptTemplate.from_template(
    "You are a prompt maker for image generation model. You will be given a story summary of a chapter from any subject and you have to create a prompt describing the story in a way that the image generation model can understand and generate an image for the story. The story is given here : {story}.")
llm_chain = LLMChain(llm=llm, prompt=prompt)
llm_chain2 = LLMChain(llm=llm, prompt=prompt2)
llm_chain3 = LLMChain(llm=llm, prompt=prompt3)

chain = load_summarize_chain(
    llm,
    chain_type='map_reduce',
    verbose=False
)


# Function to get audio
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    playsound.playsound("output.mp3")


# Function to split text into chunks
def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=20)
    chunks = text_splitter.create_documents([text])
    return chunks


# Function to process PDF and generate summary
def process_pdf(file):
    all_text = ""
    with open(file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for i, page in enumerate(pdf_reader.pages):
            content = page.extract_text()
            if content:
                all_text += content
    return all_text


# Function to apply summarization to each chunk
def summarize_chunks(chunks):
    summaries = []
    for chunk in chunks:
        try:
            summary = llm_chain.run(topic=chunk)
            summaries.append(summary)
        except Exception as e:
            st.error(f"Error summarizing chunk: {e}")
    return summaries


# Function to aggregate summaries
def aggregate_summaries(summaries):
    aggregated_summary = "\n".join(summaries)
    return aggregated_summary


def generate_image(prompt):
    output = replicate.run(
        "lucataco/ssd-1b:b19e3639452c59ce8295b82aba70a231404cb062f2eb580ea894b31e8ce5bbb6",
        input={
            "prompt": prompt,
            "disable_safety_checker": True,
            "negative_prompt": "blurry, ugly, distorted, text",
        }
    )

    return output


# Function to generate a story with accompanying images
# Function to generate a story with accompanying image

subtopic_story_pairs = {}
# Streamlit session state initialization
session_state = st.session_state

# Check if data exists in session state, if not initialize to an empty string
if 'data' not in session_state:
    session_state.data = ""
    session_state.storyData = ""


def generate_story_with_image(summary):
    try:
        global generate_story_with_image
        global story

        story = generate_story(summary)
        session_state.storyData = story
        story_data = {"story": story}
        if os.path.exists("story.json"):
            os.remove("story.json")

        with open("story.json", "w") as json_file:
            json.dump(story_data, json_file)

        # st.write(story)
        story_broken = story.split("\n")
        # Store subtopic and its corresponding story
        current_subtopic = None
        for line in story_broken:
            if line.startswith("**"):
                if ":" in line:
                    current_subtopic = line.split(":")[1].strip()
                else:
                    current_subtopic = line.strip()
                current_subtopic = current_subtopic.strip("**")
                print(current_subtopic)
                subtopic_story_pairs[current_subtopic] = ""
            elif not line.startswith("**"):
                if len(line[:]) > 0:
                    subtopic_story_pairs[current_subtopic] += line[:].strip() + "\n"
                else:
                    continue

            # Generate image for the subtopic here using generate_image function


    except Exception as e:
        st.error(f"Error generating story with image: {e}")
        return summary, None


# Function to generate a story
def generate_story(summary):
    try:
        story = llm_chain2.run(keypoints=summary)
        return story
    except Exception as e:
        st.error(f"Error generating story: {e}")

def perform_ocr(image):
    # OCR model loading
    @st.cache(allow_output_mutation=True)
    def load_model():
        return ocr.Reader(["en"], model_storage_directory=".")

    reader = load_model()
    result = reader.readtext(np.array(image))
    result_text = ""
    for text in result:
        result_text += text[1] + " "  # Concatenate the text with a space
    return result_text



st.title("Chapter Summarizer")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
uploaded_image=st.file_uploader("Upload an image", type=["png","jpg","jpeg"])


if uploaded_image is not None:
        # Button to perform OCR
        if st.button("Perform OCR and Summarise"):
            # Open the uploaded image
            input_image = Image.open(uploaded_image)
            st.image(input_image, caption='Uploaded Image', use_column_width=True)

            # Perform OCR
            with st.spinner("Performing OCR..."):
                result_text = perform_ocr(input_image)
                st.write("OCR Result:")
                st.write(result_text)

            chunks = chunk_text(result_text)
            summaries = summarize_chunks(chunks)
            aggregated_summary = aggregate_summaries(summaries)
            session_state.data = aggregated_summary

            json_file_path = os.path.join("pdf_data", "chapter_data.json")

            if len(session_state.data) > 0:
                data = {"information": session_state.data}
                
                if os.path.exists(json_file_path):
                    os.remove(json_file_path)
                
                if not os.path.exists("pdf_data"):
                    os.makedirs("pdf_data")
                
                json_file_path = os.path.join("pdf_data", "chapter_data.json")
                with open(json_file_path, "w") as json_file:
                    json.dump(data, json_file)



st.write("Or")

disabled = True

if st.button("Take a Photo"):
    disabled = False

picture = st.camera_input("", disabled = disabled)

if picture is not None:
            if st.button("Perform OCR and Summarise"):
                # Open the uploaded image
                input_image = Image.open(picture)
                # st.image(input_image, caption='Uploaded Image', use_column_width=True)

                # Perform OCR
                with st.spinner("Performing OCR..."):
                    result_text = perform_ocr(input_image)
                    st.write("OCR Result:")
                    st.write(result_text)

                chunks = chunk_text(result_text)
                summaries = summarize_chunks(chunks)
                aggregated_summary = aggregate_summaries(summaries)
                session_state.data = aggregated_summary

if uploaded_file is not None:
    if st.button("Get Summary"):
        if not os.path.exists(PDFS_DIR):
            os.makedirs(PDFS_DIR)

        with st.spinner("Processing PDF..."):
            with open(os.path.join(PDFS_DIR, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getvalue())

            topic = process_pdf(os.path.join(PDFS_DIR, uploaded_file.name))
            # st.header("Here's a breakdown of all the important information in the uploaded chapter:")
            chunks = chunk_text(topic)
            summaries = summarize_chunks(chunks)
            aggregated_summary = aggregate_summaries(summaries)
            session_state.data = aggregated_summary
            # st.write(aggregated_summary)
            json_file_path = os.path.join("pdf_data", "chapter_data.json")

            if len(session_state.data) > 0:
                data = {"information": session_state.data}
                
                if os.path.exists(json_file_path):
                    os.remove(json_file_path)
                
                if not os.path.exists("pdf_data"):
                    os.makedirs("pdf_data")
                
                json_file_path = os.path.join("pdf_data", "chapter_data.json")
                with open(json_file_path, "w") as json_file:
                    json.dump(data, json_file)

                
                
                if os.path.exists("MainPoints.json"):
                        os.remove("MainPoints.json")

                with open("MainPoints.json", "w") as json_file:
                        json.dump(data, json_file)
            

if len(session_state.data) > 0:
    st.header("Here's a breakdown of all the important information in the uploaded chapter:")
    st.write(session_state.data)
    print(session_state.data)

    st.success('Summary Generated!', icon="✅")
    data = {"information": session_state.data}

    if os.path.exists("MainPoints.json"):
        os.remove("MainPoints.json")

    with open("MainPoints.json", "w") as json_file:
        json.dump(data, json_file)


    title = import_title()
    generate_quiz_data(title)
    
    #firebase
    doc_ref = db.collection(u'Sumarries').document(title)
    doc_ref.set(data)


if len(session_state.data) > 0:
    if st.button("Generate Story"):
        with st.spinner("Generating Story..."):
            generate_story_with_image(session_state.data)


def export_story_data(story_data,title):
    data = {"information": story_data}

    if os.path.exists("story_data.json"):
        os.remove("story_data.json")

    with open("story_data.json", "w") as json_file:
        json.dump(data, json_file)
    
    doc_ref = db.collection(u'Stories').document(title)
    doc_ref.set(data)


if len(session_state.storyData) > 0:

    data = []
    title = None
    st.header("It's story time!")
    for subtopic, story in subtopic_story_pairs.items():
        subtopic_data = {
            "title": subtopic,
            "text": story,
            "img": ""
        }

        st.header(subtopic)

        if title == None:
            title = subtopic

        print("subtopic", subtopic)
        print("subtopic data", subtopic_data)
        if len(story) > 0:
            image = generate_image(story)
            st.image(image)
            subtopic_data["img"] = image[0]
        else:
            continue
        st.write(story)
        data.append(subtopic_data)
    export_story_data(data,title)
    
    st.success('Story Generation Successful!', icon="✅")

