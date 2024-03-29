import streamlit as st
from streamlit_carousel import carousel
import json

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

def import_story_data():
    try:
        with open("story_data.json", "r") as json_file:
            data = json.load(json_file)
            story_data = data.get("information", [])
            return story_data
    except FileNotFoundError:
        print("File not found. No data imported.")
        return []

story_pairs = import_story_data()

carousel(items=story_pairs, width=1.2, height=1000)
