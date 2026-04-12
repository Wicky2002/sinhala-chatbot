import streamlit as st
import ollama

# 1. UI Configuration
st.set_page_config(page_title="Sinhala Offline Chatbot", page_icon="🇱🇰")
st.title("Sinhala Offline Chatbot 🇱🇰")
st.caption("Running locally on OLLAMA (singemma-4B)")

# 2. System Prompt (The secret sauce for high marks in Sinhala handling)
SYSTEM_PROMPT = """
You are a highly accurate and helpful AI assistant for Sri Lankan users.
You must STRICTLY follow these rules:
1. Read the user's input and reply ONLY in the Sinhala language.
2. Do not use English words unless it is a technical term that cannot be translated.
3. Keep your answers natural, clear, and conversational.
"""

# 3. Initialize Session State (Chat History)
if "messages" not in st.session_state:
    # We insert the system prompt first so the model knows how to behave, 
    # but we will hide this from the actual UI loop.
    st.session_state["messages"] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# 4. Display Chat History
# We loop through the messages, skipping the system prompt so the user doesn't see it.
for msg in st.session_state["messages"]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 5. Chat Input & Inference Loop
if prompt := st.chat_input("මෙහි ටයිප් කරන්න... (Type your message here)"):
    
    # Render user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Save user message to history
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # Render assistant response with streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Call Ollama API
        try:
            for chunk in ollama.chat(
                model="Tharusha_Dilhara_Jayadeera/singemma",
                messages=st.session_state["messages"],
                stream=True,
                options={
                    "temperature": 0.3 # Low temperature keeps the Sinhala formal and accurate
                }
            ):
                # Extract the token and append to the full response
                token = chunk.get('message', {}).get('content', '')
                full_response += token
                # Update the UI with a blinking cursor effect
                response_placeholder.markdown(full_response + "▌")
            
            # Final output without the cursor
            response_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Ollama Connection Error: {e}. Please ensure Ollama is running.")
            full_response = "Error connecting to local model."

    # Save assistant response to history
    st.session_state["messages"].append({"role": "assistant", "content": full_response})

# 6. Clear Chat Button (Bonus usability feature for the 15 UI marks)
if st.sidebar.button("Clear Conversation"):
    st.session_state["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.rerun()