import streamlit as st
import firebase_admin
from firebase_admin import firestore

db = firestore.client()

st.title("View Your Past Stories")

def fetch_stories():
    docs = db.collection("Stories").stream()
    stories_list = []
    for doc in docs:
        stories_list.append(doc.id)
    return stories_list

stories = fetch_stories()
recent_stories = stories[::-1]
print(recent_stories)

selected_story_title = st.selectbox("Select Story", recent_stories)

if selected_story_title:
    docs = db.collection("Stories").stream()
    for doc in docs:
        if(doc.id == selected_story_title):
            selected_story_data = doc.to_dict()
            story_dict = selected_story_data['information']
            for story in story_dict:
                st.write(story['title'])
                st.image(story['img'])
                st.write(story["text"])
