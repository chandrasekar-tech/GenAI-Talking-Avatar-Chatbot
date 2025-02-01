import streamlit as st
import requests
from PIL import Image
import os
import tempfile
from gtts import gTTS
import base64
import asyncio
import pygame
import json

# Must be the first Streamlit command
st.set_page_config(
    page_title="Talking AI Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

class ChatUI:
    def __init__(self):
        self.setup_page()
        self.API_URL = "http://localhost:8000"
        self.load_avatars()
        self.avatar_cache = {}

    def setup_page(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_expression" not in st.session_state:
            st.session_state.current_expression = "neutral"

    def load_avatars(self):
        avatar_dir = "assets"
        self.avatars = {
            "neutral": f"{avatar_dir}/avatar_neutral.png",
            "happy": f"{avatar_dir}/avatar_happy.png",
            "thinking": f"{avatar_dir}/avatar_thinking.png",
            "speaking1": f"{avatar_dir}/avatar_speaking1.png",
            "speaking2": f"{avatar_dir}/avatar_speaking2.png",
            "excited": f"{avatar_dir}/avatar_happy.png.png",
            "sad": f"{avatar_dir}/avatar_sad.gif",
            "angry": f"{avatar_dir}/avatar_angry.gif"
        }

    def display_avatar(self, container):
        try:
            expression = st.session_state.current_expression
            if expression in self.avatar_cache:
                container.image(self.avatar_cache[expression], width=225)  # Reduced size to 75%
            elif expression in self.avatars and os.path.exists(self.avatars[expression]):
                img = Image.open(self.avatars[expression])
                self.avatar_cache[expression] = img
                container.image(img, width=225)  # Reduced size to 75%
            else:
                img = Image.open(self.avatars["neutral"])
                self.avatar_cache["neutral"] = img
                container.image(img, width=225)  # Reduced size to 75%
        except Exception as e:
            container.error(f"Error displaying avatar: {str(e)}")

    def get_ai_response(self, message: str):
        try:
            response = requests.post(
                f"{self.API_URL}/chat",
                json={"message": message}
            )
            if response.status_code == 200:
                data = response.json()
                
                # If the response is a string containing JSON
                if isinstance(data.get("response"), str):
                    try:
                        # Remove the prefix text if it exists
                        if "Here is my response" in data["response"]:
                            start_idx = data["response"].find("{")
                            end_idx = data["response"].rfind("}") + 1
                            if (start_idx != -1) and (end_idx != -1):
                                json_str = data["response"][start_idx:end_idx]
                                parsed_response = json.loads(json_str)
                                # Extract just the message from nested response if needed
                                if isinstance(parsed_response.get("response"), str):
                                    parsed_response["response"] = parsed_response["response"].strip()
                                return parsed_response
                    except json.JSONDecodeError:
                        pass
                    
                    # If direct JSON string
                    try:
                        parsed_response = json.loads(data["response"])
                        if isinstance(parsed_response.get("response"), str):
                            parsed_response["response"] = parsed_response["response"].strip()
                        return parsed_response
                    except json.JSONDecodeError:
                        # If all parsing fails, return cleaned text
                        return {
                            "response": data["response"].replace('{ "response": "', '')
                                                       .replace('"}', '')
                                                       .replace('"expression": "happy",', '')
                                                       .replace('"voice_tone": "calm"', '')
                                                       .replace('{', '')
                                                       .replace('}', '')
                                                       .strip(),
                            "expression": "neutral",
                            "voice_tone": "calm"
                        }
                
                return data
            else:
                st.error(f"API Error: Status {response.status_code}")
                return None
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    async def speak_text(self, text, voice_tone="calm"):
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
                # Generate speech first
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(fp.name)
                temp_file_path = fp.name
                
            # Initialize pygame mixer
            pygame.mixer.init()
            print("Pygame mixer initialized")
            
            # Load and play the audio file
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
            print("Playing audio")
            
            # Set speaking expression
            speaking_avatars = ["speaking1", "speaking2"]
            avatar_index = 0
            st.session_state.current_expression = speaking_avatars[avatar_index]
            self.display_avatar(st.session_state.avatar_container)
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.5)  # Adjust the delay as needed
                avatar_index = (avatar_index + 1) % len(speaking_avatars)
                st.session_state.current_expression = speaking_avatars[avatar_index]
                self.display_avatar(st.session_state.avatar_container)
            
            # Set expression back to neutral after audio finishes
            st.session_state.current_expression = "neutral"
            self.display_avatar(st.session_state.avatar_container)
            
            # Stop the mixer and uninitialize it
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            
            # Add a small delay to ensure the file is released
            await asyncio.sleep(1)
            
            # Clean up file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Error deleting temporary file: {str(e)}")
                
        except Exception as e:
            st.error(f"Error generating speech: {str(e)}")
            print(f"Error generating speech: {str(e)}")

    async def run(self):
        st.markdown("<h1 style='text-align: left; margin-top: 0;'>Talking AI Assistant</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Chat input
            if prompt := st.chat_input("Ask me anything..."):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": prompt
                })
                
                st.session_state.current_expression = "thinking"
                self.display_avatar(st.session_state.avatar_container)
                
                with st.spinner(""):
                    response = self.get_ai_response(prompt)
                
                if response:
                    cleaned_response = response["response"]
                    # Remove any remaining JSON formatting or prefixes
                    if "Here is my response" in cleaned_response:
                        cleaned_response = cleaned_response.split("{")[0].strip()
                    
                    with st.chat_message("assistant"):
                        st.write(cleaned_response)  # Display only the clean message
                        await self.speak_text(cleaned_response,  # Use clean message for audio
                                              response.get("voice_tone", "calm"))
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": cleaned_response  # Store clean message in session
                    })
            
            # # Chat messages with vertical scrollbar
            # messages_container = st.container()
            # with st.expander("Chat Messages", expanded=True):
            #     for message in reversed(st.session_state.messages):
            #         with st.chat_message(message["role"]):
            #             st.write(message["content"])
        
        with col2:
            # Avatar container without header
            avatar_container = st.empty()
            st.session_state.avatar_container = avatar_container
            self.display_avatar(avatar_container)

def main():
    chat_ui = ChatUI()
    asyncio.run(chat_ui.run())

if __name__ == "__main__":
    main()