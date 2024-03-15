import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from PIL import Image
import streamlit as st

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# for m in genai.list_models():
#     print(m.name)

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro-vision")

def get_response(input , image):
    if input != "" :
        response = model.generate_content([input,image])
    else:
        response = model.generate_content(image)
    return response.text    

st.set_page_config(page_title = "Demo")

st.header("Testing")
input = st.text_input("Enter the input" , key = "input")
uploaded_file = st.file_uploader("Choose an Image" , type = ["jpg", "png" , "jpeg"])
image  = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image)

submit = st.button("Click Here")

if submit:
    response = get_response(input , image)
    st.write(response)
