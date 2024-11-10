import streamlit as st
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
AVATAR_ID = os.getenv("YOUR_AVATAR_ID")
HEYGEN_API_ENDPOINT = "https://api.heygen.com/v2/video/generate"

# Function to create a video with HeyGen API
def create_treatment_video(text):
    # Ensure avatar ID is set
    avatar_id = "Daisy-inskirt-20220818"  # Default to a known ID if missing
    
    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": text,
                    "voice_id": "2d5b0e6cf36f460aa7fc47e3eee4ba54"  # Example professional voice ID
                },
                "background": {
                    "type": "color",
                    "value": "#FFFFFF"
                }
            }
        ],
        "dimension": {
            "width": 1280,
            "height": 720
        },
        "aspect_ratio": "16:9",
        "test": True  # Set to True for testing mode
    }

    # Call HeyGen API
    st.write("Calling HeyGen API to generate video...")
    response = requests.post(
        HEYGEN_API_ENDPOINT,
        headers={
            'X-Api-Key': HEYGEN_API_KEY,
            'Content-Type': 'application/json'
        },
        json=payload
    )

    # Check API response
    if response.status_code == 200:
        response_data = response.json()
        video_id = response_data["data"].get("video_id")
        st.write(f"Video ID received: {video_id}")
        return video_id
    else:
        st.error("Error generating video. Please check your HeyGen API settings.")
        st.write("Response status code:", response.status_code)
        st.write("Response content:", response.json())
        return None

# Function to poll for video completion and get video URL
def check_video_status(video_id):
    if not video_id:
        st.error("Invalid video ID.")
        return None

    status_url = f'https://api.heygen.com/v1/video_status.get?video_id={video_id}'
    headers = {'X-Api-Key': HEYGEN_API_KEY}
    
    st.write("Checking video status...")
    while True:
        response = requests.get(status_url, headers=headers)
        data = response.json()
        
        if data['data']['status'] == 'completed':
            video_url = data['data']['video_url']
            st.write(f"Video URL received: {video_url}")
            return video_url
        elif data['data']['status'] == 'failed':
            st.error("Video generation failed.")
            return None
        else:
            st.info("Generating video... please wait.")
            time.sleep(10)

# Streamlit UI
def main():
    st.title("HeyGen Video Test")
    
    # Input for sample text
    sample_text = st.text_area("Enter sample text for the video", 
                               "This is a test video created using HeyGen's API.")
    
    # Generate video on button click
    if st.button("Generate Video"):
        video_id = create_treatment_video(sample_text)
        
        if video_id:
            st.write("Video generation in progress. This may take a few minutes...")
            video_url = check_video_status(video_id)
            
            if video_url:
                st.write("Streaming the generated video below:")
                st.video(video_url)
            else:
                st.error("Failed to retrieve video URL.")
        else:
            st.error("Failed to generate video ID.")

if __name__ == "__main__":
    main()
