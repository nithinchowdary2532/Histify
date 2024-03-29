import replicate
import os
import streamlit as st
from PIL import Image
import requests

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
api = replicate.Client(api_token=REPLICATE_API_TOKEN)


def genreate_image(prompt):
    output = replicate.run(
    "lucataco/ssd-1b:b19e3639452c59ce8295b82aba70a231404cb062f2eb580ea894b31e8ce5bbb6",
    input={
        "prompt": prompt,
        "disable_safety_checker" : True,
        "negative_prompt" : "blurry, ugly, distorted, text",
    }
    )
    return output

def generate_story_with_image(summary):
    try:
        # story = generate_story(summary)
        story_broken = summary.split("\n")

        anecdotes = ""
        for i, line in enumerate(story_broken):
            if i % 2 == 0:
                anecdotes += line + "\n"
            else:
                image = genreate_image(anecdotes)
                st.image(image)
                st.write(anecdotes)
                anecdotes = ""
        # Check if there are any remaining lines
        if anecdotes:
            # Generate an image for the remaining anecdotes
            image = genreate_image(anecdotes)
            # Display the image
            st.image(image)
            # Display the remaining anecdotes
            st.write(anecdotes)

    except Exception as e:
        st.error(f"Error generating story with image: {e}")
        return summary, None


image = ""
st.title("Testing")
prompt = st.text_area("Enter the prompt")
submit = st.button("Click Here")
if submit:
    generate_story_with_image(prompt)
    
    
    

