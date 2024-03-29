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

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))



import google.generativeai as genai

def get_gemini_response(question):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not question:
        st.warning('Please enter a non empty question.', icon="⚠")
        return None  # or return ''
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

def user_input(user_question, conversation_history):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)

    conversation_history.append({"user_question": user_question, "gemini_response": response["output_text"]})
    st.write("Reply: ", response["output_text"])
    
    # Save updated conversation history to session state
    st.session_state.conversation_history = conversation_history
    
    return response["output_text"] 

def get_gemini_response2(question):
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
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

    # Initialize conversation history
    conversation_history = st.session_state.get("conversation_history", [])

    question_counter = 0  # Counter to generate unique keys for text inputs
    button_counter = 0  # Counter to generate unique keys for buttons

    while True:
        question_counter += 1
        user_question = st.text_input(f"Ask a Question from the PDF Files {question_counter}")

        if user_question:
            response_from_gemini = user_input(user_question, conversation_history)
            ask_button_key = f"ask_button_{question_counter}"  # Unique key for ask button
            if not response_from_gemini:
                # Display placeholder text while waiting for response
                st.write("Generating response...")
            elif "Do you want to explore more resources?" in response_from_gemini:
                button_counter += 1
                if st.button(f"Explore more resources {button_counter}"):
                    # Get response from Gemini and store it in a variable
                    gemini_response = get_gemini_response2(user_question + "in detail")
                    formatted_gemini_response = format_gemini_response(gemini_response)
                    st.write("Answer: ", formatted_gemini_response)
                    # Record the exploration in conversation history along with the Gemini response
                    conversation_history.append({"user_question": user_question, "explore_more_resources": True, "gemini_response": formatted_gemini_response})
                    continue  # Skip directly to the next iteration without showing "Ask another question" button

            # Display input bar for the next question
            continue_next_question = st.button("Ask another question", key=ask_button_key)
            if continue_next_question:
                continue
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
                    button_counter += 1
                    if st.button(f"Explore more resources {button_counter}"):
                        # Get response from Gemini and store it in a variable
                        gemini_response = get_gemini_response2(user_question)
                        formatted_gemini_response = format_gemini_response(gemini_response)
                        st.write("Answer: ", formatted_gemini_response)
                        # Record the exploration in conversation history along with the Gemini response
                        conversation_history.append({"user_question": user_question, "explore_more_resources": True, "gemini_response": formatted_gemini_response})

            ask_button_key = f"ask_button_{question_counter}"  # Unique key for ask button
            if not st.button("Ask another question", key=ask_button_key):
                break
    
    # Save conversation history to session state
    st.session_state.conversation_history = conversation_history

if __name__ == "__main__":
    main()
