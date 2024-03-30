import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import dotenv
import json 

dotenv.load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))


prompt = PromptTemplate.from_template("""
Given topic name you should generate 10 mcqs in json string so can use json.loads() with keys question, information, options, answer. This is the topic name - {topic}. It should be in format of [
    {{
        "question": "What is the primary goal of artificial intelligence?",
        "information": "This field of computer science aims to create systems capable of performing tasks that would typically require human intelligence.",
        "options": ["To simulate human intelligence", "To enhance computer speed", "To replace human jobs", "To improve data storage"],
        "answer": "To simulate human intelligence"
    }},
    {{
        "question": "What is 'machine learning' in the context of artificial intelligence?",
        "information": "This is a subset of artificial intelligence that involves the creation of systems that can learn from and make decisions based on data.",
        "options": ["A new programming language", "A data processing method", "A subset of artificial intelligence", "A type of computer hardware"],
        "answer": "A subset of artificial intelligence"
    }}
]
""")

def import_title():
    try:
        with open("MainPoints.json", "r") as json_file:
            data = json.load(json_file)
            story_data = data.get("information", [])
            title = story_data.split('\n')[0]
            title = title.strip("**")
            return title
    except FileNotFoundError:
        print("File not found. No data imported.")
        return []
        
llm_chain = LLMChain(llm=llm, prompt=prompt)

title = import_title()

print(title)

# Fetch the quiz data only once

def generate_quiz_data(title):
    json_file_path = "MainPoints.json"

    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        quiz_data = data["information"]

        # Write quiz data to a separate JSON file
        quiz_file_path = f"quiz_data/{title}_quiz.json"
        with open('quiz_data.json', "w") as quiz_file:
            json.dump(quiz_data, quiz_file)




