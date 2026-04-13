import streamlit as st
import ollama
import time # Added for performance tracking

# 1. UI Configuration
st.set_page_config(page_title="Sinhala Offline Chatbot", page_icon="🇱🇰")
st.title("Sinhala Offline Chatbot 🇱🇰")
st.caption("Running locally on OLLAMA (singemma-4B) - Tech & SL Expert")

# ==========================================
# SYSTEM PROMPT & INITIALIZATION
# ==========================================
SYSTEM_PROMPT = """
You are a highly intelligent, tech-savvy AI assistant designed specifically for Sri Lankan users. 
Your core domains of expertise are:
1. Computing & Technology: Software engineering, AI, Python, web frameworks (like Next.js, FastAPI), and university/internship career advice.
2. Sri Lankan Context: Geography, culture, and general knowledge about Sri Lanka (e.g., places in Colombo, local traditions).
3. General Assistance: Day-to-day helpful advice.

STRICT RULES:
- You must ONLY reply in natural, grammatically correct Sinhala. 
- You may use English ONLY for specific technical computing terms (e.g., "Machine Learning", "FastAPI", "Server", "API") that do not have a common Sinhala translation. 
- Keep answers clear, factual, and structured. 
- If you do not know something, say "මට ඒ පිළිබඳව නිවැරදි තොරතුරු නොමැත". Do NOT invent facts.
"""

# The Domain-Specific Few-Shot Examples
INITIAL_HISTORY = [
    {"role": "system", "content": SYSTEM_PROMPT},
    
    # Example 1: Sri Lankan / General Context
    {"role": "user", "content": "කොළඹ නිදහසේ කාලය ගත කරන්න පුළුවන් හොඳ තැන් මොනවාද?"},
    {"role": "assistant", "content": "කොළඹ නිදහසේ කාලය ගත කිරීම සඳහා ගාලු මුවදොර පිටිය (Galle Face Green), විහාරමහාදේවි උද්‍යානය, සහ දියත උයන වැනි ස්ථාන ඉතා සුදුසු වේ. මීට අමතරව නිදහස් චතුරශ්‍රය අවට පරිසරයද ඉතාම නිස්කලංකයි."},
    
    # Example 2: Computing & Tech Context
    {"role": "user", "content": "Software Engineering internship එකකට ලෑස්ති වෙන්නේ කොහොමද?"},
    {"role": "assistant", "content": "Software Engineering internship එකකට සූදානම් වීමේදී ප්‍රධාන කරුණු කිහිපයක් වැදගත් වේ. පළමුව, Python හෝ Java වැනි භාෂාවකින් ඔබේ Programming හැකියාවන් වර්ධනය කරගන්න. දෙවනුව, Data Structures සහ Algorithms පිළිබඳ මනා අවබෝධයක් ලබා ගන්න. අවසාන වශයෙන්, ඔබ කළ projects ඇතුළත් හොඳ CV එකක් සකස් කර සම්මුඛ පරීක්ෂණ (interviews) සඳහා හොඳින් සූදානම් වන්න."},
    
    # Example 3: Advanced Computing
    {"role": "user", "content": "Machine Learning කියන්නේ මොකක්ද?"},
    {"role": "assistant", "content": "Machine Learning (යන්ත්‍ර ඉගෙනුම) යනු කෘතිම බුද්ධියේ (AI) එක් අංශයකි. මෙහිදී පරිගණක වැඩසටහන් වලට දත්ත (data) ලබා දී, එම දත්ත හරහා ස්වයංක්‍රීයව ඉගෙන ගෙන තීරණ ගැනීමට හෝ අනාවැකි පළ කිරීමට ඒවා පුහුණු කරනු ලබයි."}
]

# ==========================================
# SIDEBAR: ADVANCED CONTROLS & USABILITY
# ==========================================
st.sidebar.header("⚙️ Model Controls")
st.sidebar.write("Adjust inference parameters dynamically:")

# Feature 1: Hyperparameter Sliders
user_temp = st.sidebar.slider("Temperature (Creativity)", min_value=0.0, max_value=1.0, value=0.1, step=0.1)
user_top_p = st.sidebar.slider("Top-P (Vocabulary Focus)", min_value=0.1, max_value=1.0, value=0.5, step=0.1)

st.sidebar.divider()
st.sidebar.header("💾 Chat Management")

# Feature 2: Clear Chat Button
if st.sidebar.button("🗑️ Clear Conversation"):
    st.session_state["messages"] = list(INITIAL_HISTORY)
    st.rerun()

# Feature 3: Export Chat Functionality
def get_chat_download_string():
    chat_log = "Sinhala Chatbot - Offline Session Log\n" + "="*40 + "\n\n"
    for msg in st.session_state.get("messages", []):
        if msg["role"] != "system":
            role_name = "User" if msg["role"] == "user" else "Assistant"
            chat_log += f"{role_name}: {msg['content']}\n\n"
    return chat_log

st.sidebar.download_button(
    label="📥 Download Chat Log",
    data=get_chat_download_string(),
    file_name="sinhala_chat_history.txt",
    mime="text/plain"
)

# ==========================================
# INITIALIZATION & DISPLAY
# ==========================================
if "messages" not in st.session_state:
    st.session_state["messages"] = list(INITIAL_HISTORY)

# Display Chat History
for msg in st.session_state["messages"]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ==========================================
# CHAT INPUT & INFERENCE LOGIC
# ==========================================
if prompt := st.chat_input("මෙහි ටයිප් කරන්න... (Type your message here)"):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Start the performance timer
        start_time = time.time()
        
        try:
            # Call Ollama API with dynamic sliders
            for chunk in ollama.chat(
                model="Tharusha_Dilhara_Jayadeera/singemma",
                messages=st.session_state["messages"],
                stream=True,
                options={
                    "temperature": user_temp,
                    "top_p": user_top_p
                }
            ):
                token = chunk.get('message', {}).get('content', '')
                full_response += token
                response_placeholder.markdown(full_response + "▌")
            
            # Stop the timer
            end_time = time.time()
            generation_time = round(end_time - start_time, 2)
            
            response_placeholder.markdown(full_response)
            
            # Feature 4: Display Inference Speed
            st.caption(f"⏱️ Response generated in {generation_time} seconds locally.")
            
        except Exception as e:
            st.error(f"Ollama Connection Error: {e}. Please ensure Ollama is running.")
            full_response = "Error connecting to local model."

    st.session_state["messages"].append({"role": "assistant", "content": full_response})