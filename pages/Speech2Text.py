import streamlit as st
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
import replicate
import requests
import json
import time
from io import BytesIO
from generate_quiz import generate_quiz_data, import_title
load_dotenv()

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
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PDFS_DIR = "pdfs"

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
api = replicate.Client(api_token=REPLICATE_API_TOKEN)
st.title("Speech to Text")

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

def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=20)
    chunks = text_splitter.create_documents([text])
    return chunks

def summarize_chunks(chunks):
    summaries = []
    for chunk in chunks:
        try:
            summary = llm_chain.run(topic=chunk)
            summaries.append(summary)
        except Exception as e:
            st.error(f"Error summarizing chunk: {e}")
    return summaries

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


state = st.session_state

if 'text_received' not in state:
    state.text_received = []


text = speech_to_text(language='en', use_container_width=True, just_once=True, key='STT')

if text:
    state.text_received.append(text)

for text in state.text_received:
    st.text(text)


st.write("Record your voice, and play the recorded audio:")
audio = mic_recorder(start_prompt="⏹️", stop_prompt="🔴", key='recorder')

if audio:
    st.audio(audio['bytes'])

    st.download_button(
        label="Download Audio",
        data=audio['bytes'],
        file_name="recorded_audio.wav",
        mime="audio/wav"
    )

if text is not None:
        # Button to perform OCR
        if st.button("Summarise"):
            st.write(text)
            chunks = chunk_text(text)
            summaries = summarize_chunks(chunks)
            aggregated_summary = aggregate_summaries(summaries)
            session_state.data = aggregated_summary


if len(session_state.data) > 0:
    st.header("Here's a breakdown of all the important information in the uploaded chapter:")
    st.write(session_state.data)
    st.success('Summary Generated!', icon="✅")
    data = {"information": session_state.data}

    if os.path.exists("MainPoints.json"):
        os.remove("MainPoints.json")

    with open("MainPoints.json", "w") as json_file:
        json.dump(data, json_file)

    title = import_title()
    print(title)
    generate_quiz_data(title)
if len(session_state.data) > 0:
    if st.button("Generate Story"):
        with st.spinner("Generating Story..."):
            generate_story_with_image(session_state.data)


def export_story_data(story_data):
    data = {"information": story_data}

    if os.path.exists("story_data.json"):
        os.remove("story_data.json")

    with open("story_data.json", "w") as json_file:
        json.dump(data, json_file)


if len(session_state.storyData) > 0:

    data = []
    st.header("It's story time!")
    st.subheader("Check out the carasouel to see the story !!")
    for subtopic, story in subtopic_story_pairs.items():
        subtopic_data = {
            "title": subtopic,
            "text": story,
            "img": ""
        }

        st.header(subtopic)
        if len(story) > 0:
            image = generate_image(story)
            st.image(image)
            subtopic_data["img"] = image[0]
        else:
            continue
        st.write(story)
        data.append(subtopic_data)
    export_story_data(data)
    st.success('Story Generation Successful!', icon="✅")