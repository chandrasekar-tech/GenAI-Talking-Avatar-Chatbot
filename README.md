# GenAI Avatar Chat

GenAI Avatar Chat is a web application that allows users to interact with an AI-powered talking chatbot with a static avatar. The chatbot uses AWS Bedrock for generating responses and Google Text-to-Speech (gTTS) for voice output. The backend is built with FastAPI, and the frontend uses Streamlit for the user interface.

# Major Use Cases
# API Backend (api.py):

- Provides an API endpoint to handle chat requests.
- Uses AWS Bedrock to generate AI responses in a specified JSON format.
- Ensures the responses include the message, avatar expression, and voice tone.
- Includes a health check endpoint to verify the API status.

# Chat UI (chat_frontend.py):
- Chat Interface: Provides a chat interface where users can input their queries and receive responses from the AI assistant.
- Avatar Display: Displays an avatar that changes expressions based on the AI assistant's responses and actions (e.g., thinking, speaking).
- AI Response Handling: Sends user queries to an AI backend server and processes the responses to display clean messages in the chat interface.
- Text-to-Speech: Converts the AI assistant's text responses into speech using Google Text-to-Speech (gTTS) and plays the audio using Pygame.
- Session Management: Maintains the chat history and current avatar expression using Streamlit's session state.
- Error Handling: Handles errors gracefully, displaying appropriate error messages to the user.

## Project Structure

```
README.md
requirements.txt
src/
    __pycache__/
    api.py
    assets/
    chat_frontend.py
```

## Requirements

- Python 3.8+
- AWS credentials configured in `~/.aws/config` and `~/.aws/credentials`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/genai-avatar-chat.git
    cd genai-avatar-chat
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Start the API Server

1. Navigate to the `src` directory:
    ```sh
    cd src
    ```

2. Start the FastAPI server:
    ```sh
    uvicorn api:app --reload  or  python -m uvicorn api:app --reload
    ```

### Start the Chat Frontend

1. Open another terminal and navigate to the `src` directory:
    ```sh
    cd src
    ```

2. Start the Streamlit application:
    ```sh
    streamlit run chat_frontend.py  or  python -m streamlit run chat_frontend.py
    ```

### Access the Application

- Open your web browser and go to `http://localhost:8501` to interact with the chatbot.

## Configuration

Ensure your AWS credentials are correctly configured in `~/.aws/config` and `~/.aws/credentials`:

`~/.aws/config`:
```
[default]
region = us-east-1
```

## Project Files

- `src/api.py`: FastAPI server that handles chat requests and interacts with AWS Bedrock.
- `src/chat_frontend.py`: Streamlit frontend for the chatbot.
- `requirements.txt`: List of required Python packages.

## License

This project is licensed under the MIT License.