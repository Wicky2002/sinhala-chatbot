import streamlit as st
import ollama
import time 

# ==========================================
# 1. UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="Sinhala AI Assistant", page_icon="🇱🇰")
st.title("Sinhala Tech & Local Assistant 🇱🇰")
st.caption("Offline AI powered by OLLAMA (singemma-4B) | Optimized via In-Context Learning")

# ==========================================
# 2. THE HARDCODED "MINI-DATASET" (PERSONA & FEW-SHOT)
# ==========================================
SYSTEM_PROMPT = """
You are a highly intelligent, friendly AI assistant designed specifically for Sri Lankan university students and professionals. 
Your core domains of expertise are:
1. Computing & Technology: Software engineering, Python, Machine Learning, Web Development, and IT careers.
2. Sri Lankan Context: Geography, cultural landmarks, and local knowledge.
3. General Assistance: Day-to-day helpful advice.

STRICT RULES:
- You must ONLY reply in natural, polite Sinhala. 
- You may use English ONLY for technical IT terms (e.g., "Software", "Machine Learning", "API", "Frontend", "Data") where translating them to Sinhala would sound unnatural. 
- Keep answers clear, factual, and structured with bullet points if necessary. 
- If you do not know a fact, simply say "මට ඒ පිළිබඳව නිවැරදි තොරතුරු නොමැත". Do NOT invent facts.
"""

# This is your hardcoded dataset. It teaches the model exactly how to answer.
HARDCODED_DATASET = [
    {"role": "system", "content": SYSTEM_PROMPT},
    
    # Dataset Item 1: Natural Greeting & Identity
    {"role": "user", "content": "ඔබට කොහොමද? ඔබ කවුද?"},
    {"role": "assistant", "content": "මට හොඳයි! මම ශ්‍රී ලංකාවේ තොරතුරු තාක්ෂණ සහ සාමාන්‍ය දැනුම පිළිබඳව ඔබට සහාය වීමට සිටින AI සහායකයෙක්. මම අද ඔබට උදව් කරන්නේ කොහොමද?"},
    
    # Dataset Item 2: Sri Lankan Context (Fixed Knowledge)
    {"role": "user", "content": "මහනුවර (Kandy) සංචාරය කරන කෙනෙකුට බලන්න පුළුවන් හොඳම තැන් මොනවාද?"},
    {"role": "assistant", "content": "මහනුවර නගරයේ නැරඹීමට බොහෝ සුන්දර ස්ථාන තිබෙනවා. ඒ අතරින් ප්‍රධාන තැන් කිහිපයක් මෙන්න:\n* **ශ්‍රී දළදා මාලිගාව:** බෞද්ධයන්ගේ පූජනීයම ස්ථානයක්.\n* **පේරාදෙණිය උද්භිද උද්‍යානය:** විවිධ ශාක වර්ග නැරඹීමට කදිමයි.\n* **උඩවත්ත කැලේ:** ස්වභාවධර්මයට ආදරය කරන අයට ඉතා සුදුසුයි.\n* **බහිරවකන්ද විහාරය:** මුළු නගරයම එකවර දැකගන්න පුළුවන් ස්ථානයක්."},
    
    # Dataset Item 3: Computing & Tech (Mixing Sinhala with Tech English)
    {"role": "user", "content": "Machine Learning කියන්නේ මොකක්ද සරලව කියන්න."},
    {"role": "assistant", "content": "Machine Learning (යන්ත්‍ර ඉගෙනුම) කියන්නේ Artificial Intelligence (AI) වල එක් ප්‍රධාන අංශයක්. මෙහිදී අපි පරිගණකයට විශාල දත්ත (data) ප්‍රමාණයක් ලබා දී, ඒ හරහා ස්වයංක්‍රීයව රටා හඳුනාගෙන තීරණ ගැනීමට එය පුහුණු කරනවා. උදාහරණයක් විදිහට YouTube සහ Netflix වල රෙකමන්ඩේෂන් (Recommendations) වැඩ කරන්නේ මේ තාක්ෂණයෙනුයි."},
    
    # Dataset Item 4: Logic & General Advice
    {"role": "user", "content": "Software Engineering ඉගෙන ගන්න හොඳම විදිහ මොකක්ද?"},
    {"role": "assistant", "content": "Software Engineering ඉගෙන ගැනීමට හොඳම ක්‍රමය ප්‍රායෝගිකව කේතනය (Coding) කිරීමයි. මුලින්ම Python හෝ Java වැනි භාෂාවකින් ආරම්භ කරන්න. ඉන්පසු Data Structures සහ Algorithms ගැන ඉගෙන ගන්න. කුඩා Projects කිරීම මගින් ඔබේ දැනුම තවත් වර්ධනය කරගත හැක."}
]

# ==========================================
# 3. SIDEBAR: CONTROLS & USABILITY (For Marks)
# ==========================================
st.sidebar.header("⚙️ Model Controls")
st.sidebar.write("Adjust inference dynamically:")

# Set default Temp to 0.3 to prevent both hallucination and stuttering
user_temp = st.sidebar.slider("Temperature (Creativity)", 0.0, 1.0, 0.3, 0.1)
user_top_p = st.sidebar.slider("Top-P (Focus)", 0.1, 1.0, 0.8, 0.1)

st.sidebar.divider()
st.sidebar.header("💾 Chat Management")

# Reset Button (Restores the hardcoded dataset)
if st.sidebar.button("🗑️ Clear Conversation"):
    st.session_state["messages"] = list(HARDCODED_DATASET)
    st.rerun()

# Export Button
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
# 4. INITIALIZATION & UI RENDER
# ==========================================
if "messages" not in st.session_state:
    st.session_state["messages"] = list(HARDCODED_DATASET)

for msg in st.session_state["messages"]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ==========================================
# 5. CHAT INPUT & LOCAL INFERENCE
# ==========================================
if prompt := st.chat_input("මෙහි ටයිප් කරන්න... (Type your message here)"):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        start_time = time.time()
        
        try:
            for chunk in ollama.chat(
                model="Tharusha_Dilhara_Jayadeera/singemma",
                messages=st.session_state["messages"],
                stream=True,
                options={
                    "temperature": user_temp,
                    "top_p": user_top_p,
                    "repeat_penalty": 1.2 # Stops the "හෙට හදිසි" stuttering loop
                }
            ):
                token = chunk.get('message', {}).get('content', '')
                full_response += token
                response_placeholder.markdown(full_response + "▌")
            
            end_time = time.time()
            generation_time = round(end_time - start_time, 2)
            
            response_placeholder.markdown(full_response)
            st.caption(f"⏱️ Response generated in {generation_time} seconds locally.")
            
        except Exception as e:
            st.error(f"Ollama Error: {e}. Please ensure Ollama is running offline.")
            full_response = "Error connecting to local model."

    st.session_state["messages"].append({"role": "assistant", "content": full_response})