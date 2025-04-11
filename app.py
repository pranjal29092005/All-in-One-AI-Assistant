import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now this will work
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

# Page configuration
st.set_page_config(page_title="All-in-One AI Assistant", page_icon="🤖")

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize Groq client: {str(e)}")
    client = None

# Function to generate response
def generate_response(messages):
    try:
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=messages,
            temperature=0.3,
            max_completion_tokens=4096,
            top_p=0.90,
            stream=True,
            stop=None,
        )

        # Create a placeholder for streaming response
        response_placeholder = st.empty()
        full_response = ""

        # Stream the response
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                # Update the placeholder with the growing response
                response_placeholder.markdown(full_response)

        return full_response

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Main UI
st.title("All-in-One AI Assistant")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("This chatbot uses the Groq API with the deepseek-r1-distill-llama-70b model.")

    # Model settings
    st.markdown("## Model Settings")
    temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.6, step=0.01)

    # Clear conversation button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.experimental_rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask something..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        messages_for_api = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        response = generate_response(messages_for_api)

        if response:
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})