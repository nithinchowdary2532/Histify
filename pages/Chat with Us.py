import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import json
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>' , unsafe_allow_html= True)

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(question):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not question:
        st.warning('Please enter a non empty question.', icon="⚠")
        return None
    
    
    genai.configure(api_key=api_key)  # Pass the API key as a keyword argument
    
    # Initialize the generative model
    model = genai.GenerativeModel('gemini-pro')

    # Generate content based on the question
    response = model.generate_content(question)

    # Return the generated response
    return response.text



def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
    return  text



def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():

    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details,if the answer is not in
    provided context just say, "answer is not available in the context" ,  don't provide the wrong answer\n\n
    If the answer is not avalaibe in the context ,always append this line to the end of the response you give , "Do you want to explore more resources?".
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",
                             temperature=0.3)

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain



def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)

    print(response)
    st.write("Reply: ", response["output_text"])
    
    return response["output_text"] 

model=genai.GenerativeModel("gemini-pro")

def get_gemini_response2(question):
    chat = model.start_chat(history=[])
    response=chat.send_message(question,stream=True)
    return response

def format_gemini_response(response):
    response.resolve()  # Ensure response iteration is complete
    candidates = response.candidates
    text_parts = [candidate.content.parts[0].text for candidate in candidates]
    generated_text = '\n'.join(text_parts)
    return generated_text


def main():
    st.set_page_config("Chat PDF")
    st.header("Any Doubts ?")

    user_question = st.text_input("Ask a Question from the PDF Files")

    if user_question:
        response_from_gemini = user_input(user_question)
        
        if st.button("Explore more resources"):
            response = get_gemini_response2(user_question + "in detail")
            formatted_response = format_gemini_response(response)
            st.write("Answer: ", formatted_response)
    else:
        # Read text from chapter_data.json
        with open("pdf_data/chapter_data.json", "r") as json_file:
            chapter_data = json.load(json_file)
            raw_text = chapter_data["information"]

        # Process the text
        text_chunks = get_text_chunks(raw_text)
        get_vector_store(text_chunks)

        response_from_gemini = get_gemini_response(user_question)
        st.write("Reply: ", response_from_gemini)  

        if response_from_gemini is not None:
            if "Do you want to explore more resources?" in response_from_gemini:
                response = get_gemini_response2(user_question)
                formatted_response = format_gemini_response(response)
                st.write("Answer: ", formatted_response)



if __name__ == "__main__":
    main()
