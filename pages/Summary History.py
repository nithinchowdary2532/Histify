import streamlit as st
import firebase_admin
from firebase_admin import firestore

db = firestore.client()

st.title("View Your Past Summaries")

def fetch_summaries():
    docs = db.collection("Sumarries").stream()
    summaries_list = []
    for doc in docs:
        summaries_list.append(doc.id)
    return summaries_list

summaries = fetch_summaries()
recent_summaries = summaries[::-1]
print(recent_summaries)

selected_summary_title = st.selectbox("Select Summary", recent_summaries)

if selected_summary_title:
    docs = db.collection("Sumarries").stream()
    for doc in docs:
        if(doc.id == selected_summary_title):
            selected_summary_data = doc.to_dict()
            print(selected_summary_data)
            print(type(selected_summary_data))
            st.write(selected_summary_data["information"])
