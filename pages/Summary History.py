import streamlit as st
import firebase_admin
from firebase_admin import firestore

db = firestore.client()
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
