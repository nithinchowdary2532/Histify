import streamlit as st
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import dotenv
from generate_quiz import generate_quiz_data , import_title

def run():
    st.set_page_config(
        page_title="Streamlit quizz app",
        page_icon="❓",
    )

if __name__ == "__main__":
    run()
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
# Custom CSS for the buttons
st.markdown("""
<style>
div.stButton > button:first-child {
    display: block;
    margin: 0 auto;
</style>
""", unsafe_allow_html=True)

# Initialize session variables if they do not exist
default_values = {'current_index': 0, 'current_question': 0, 'score': 0, 'selected_option': None, 'answer_submitted': False}
for key, value in default_values.items():
    st.session_state.setdefault(key, value)

# Load quiz data
with open('./quiz_data.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

def restart_quiz():
    title = import_title()
    print(title)
    generate_quiz_data(title)

    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False


def submit_answer():

    # Check if an option has been selected
    if st.session_state.selected_option is not None:
        # Mark the answer as submitted
        st.session_state.answer_submitted = True
        # Check if the selected option is correct
        if st.session_state.selected_option == quiz_data[st.session_state.current_index]['answer']:
            st.session_state.score += 10
    else:
        # If no option selected, show a message and do not mark as submitted
        st.warning("Please select an option before submitting.")

def next_question():
    st.session_state.current_index += 1
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False

# Title and description
st.title("Test yourself")

# Progress bar
progress_bar_value = (st.session_state.current_index + 1) / len(quiz_data)
st.metric(label="Score", value=f"{st.session_state.score} / {len(quiz_data) * 10}")
st.progress(progress_bar_value)

# Display the question and answer options
question_item = quiz_data[st.session_state.current_index]
st.subheader(f"Question {st.session_state.current_index + 1}")
st.title(f"{question_item['question']}")

hint_shown = False

if st.button("Confused? Here's a hint!"):
    hint_shown = True
    
    if st.button("x"):
        hint_shown = False

if hint_shown:
    
    print("Hint shown:", hint_shown)  # Print the current state of hint_shown
    if hint_shown:
        st.write(question_item.get('information', ''))
else:
        st.write("")


st.markdown(""" ___""")

# Answer selection
options = question_item['options']
correct_answer = question_item['answer']

if st.session_state.answer_submitted:
    for i, option in enumerate(options):
        label = option
        if option == correct_answer:
            st.success(f"{label} (Correct answer)")
        elif option == st.session_state.selected_option:
            st.error(f"{label} (Incorrect answer)")
        else:
            st.write(label)
else:
    for i, option in enumerate(options):
        with st.container():
            if st.button(option, key=i):
                st.session_state.selected_option = option


st.markdown(""" ___""")

# Submission button and response logic
if st.session_state.answer_submitted:
    if st.session_state.current_index < len(quiz_data) - 1:
        st.button('Next', on_click=next_question)
    else:
        st.write(f"Quiz completed! Your score is: {st.session_state.score} / {len(quiz_data) * 10}")
        if st.button('Restart', on_click=restart_quiz):
            pass
else:
    if st.session_state.current_index < len(quiz_data):
        st.button('Submit', on_click=submit_answer)