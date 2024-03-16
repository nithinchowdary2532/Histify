import streamlit as st
from streamlit_carousel import carousel
import json

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
