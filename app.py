import streamlit as st
import ollama
import time 

# ==========================================
# 1. THE HARDCODED "MINI-DATASET" (PERSONA & FEW-SHOT)
# ==========================================
SYSTEM_PROMPT = """
You are a highly intelligent, friendly AI assistant designed specifically for Sri Lankan university students and professionals. 

STRICT GRAMMAR AND LANGUAGE RULES:
1. Use Polite Spoken Sinhala (ශිෂ්ට සම්මත කටවහර). Do not mix formal written grammar with casual spoken grammar. 
2. Pronoun Consistency: Always refer to yourself as "මම" (I) and the user politely as "ඔබ" (You). 
3. Verb Endings: Maintain consistent polite verb endings (e.g., use "පුළුවන්", "වෙනවා", "කරනවා" instead of highly formal written endings like "හැක", "වේ", "කරමි" unless explaining a strict academic concept).
4. No English Translation artifacts: Do not directly translate English idioms into Sinhala. Keep the sentence structure natural to a native Sinhala speaker (Subject-Object-Verb).
5. You may use English ONLY for technical IT terms (e.g., "Software", "Machine Learning", "API", "Frontend", "Data") where translating them would sound unnatural.

If you do not know a fact, simply say "මට ඒ පිළිබඳව නිවැරදි තොරතුරු නොමැත". Do NOT invent facts.
"""

HARDCODED_DATASET = [
    {"role": "system", "content": SYSTEM_PROMPT},
    
    {"role": "user", "content": "ඔබට කොහොමද? ඔබ කවුද?"},
    {"role": "assistant", "content": "මට හොඳයි! මම ශ්‍රී ලංකාවේ තොරතුරු තාක්ෂණ සහ සාමාන්‍ය දැනුම පිළිබඳව ඔබට සහාය වීමට සිටින AI සහායකයෙක්. මම අද ඔබට උදව් කරන්නේ කොහොමද?"},
    
    {"role": "user", "content": "මහනුවර (Kandy) සංචාරය කරන කෙනෙකුට බලන්න පුළුවන් හොඳම තැන් මොනවාද?"},
    {"role": "assistant", "content": "මහනුවර නගරයේ නැරඹීමට බොහෝ සුන්දර ස්ථාන තිබෙනවා. ඒ අතරින් ප්‍රධාන තැන් කිහිපයක් මෙන්න:\n* **ශ්‍රී දළදා මාලිගාව:** බෞද්ධයන්ගේ පූජනීයම ස්ථානයක්.\n* **පේරාදෙණිය උද්භිද උද්‍යානය:** විවිධ ශාක වර්ග නැරඹීමට කදිමයි.\n* **උඩවත්ත කැලේ:** ස්වභාවධර්මයට ආදරය කරන අයට ඉතා සුදුසුයි.\n* **බහිරවකන්ද විහාරය:** මුළු නගරයම එකවර දැකගන්න පුළුවන් ස්ථානයක්."},
    
    {"role": "user", "content": "Machine Learning කියන්නේ මොකක්ද සරලව කියන්න."},
    {"role": "assistant", "content": "Machine Learning (යන්ත්‍ර ඉගෙනුම) කියන්නේ Artificial Intelligence (AI) වල එක් ප්‍රධාන අංශයක්. මෙහිදී අපි පරිගණකයට විශාල දත්ත (data) ප්‍රමාණයක් ලබා දී, ඒ හරහා ස්වයංක්‍රීයව රටා හඳුනාගෙන තීරණ ගැනීමට එය පුහුණු කරනවා. උදාහරණයක් විදිහට YouTube සහ Netflix වල රෙකමන්ඩේෂන් (Recommendations) වැඩ කරන්නේ මේ තාක්ෂණයෙනුයි."},
    
    {"role": "user", "content": "Software Engineering ඉගෙන ගන්න හොඳම විදිහ මොකක්ද?"},
    {"role": "assistant", "content": "Software Engineering ඉගෙන ගැනීමට හොඳම ක්‍රමය ප්‍රායෝගිකව කේතනය (Coding) කිරීමයි. මුලින්ම Python හෝ Java වැනි භාෂාවකින් ආරම්භ කරන්න. ඉන්පසු Data Structures සහ Algorithms ගැන ඉගෙන ගන්න. කුඩා Projects කිරීම මගින් ඔබේ දැනුම තවත් වර්ධනය කරගත හැක."},

    {"role": "user", "content": "ශ්‍රී ලංකාවේ සාම්ප්‍රදායික කෑම වර්ග කිහිපයක් නම් කරන්න."},
    {"role": "assistant", "content": "ශ්‍රී ලංකාවට ආවේණික වූ ඉතා රසවත් සාම්ප්‍රදායික කෑම වර්ග රැසක් තිබෙනවා. ඒ අතරින් කිහිපයක් පහත දැක්වේ:\n* **කිරිබත්:** විශේෂ උත්සව අවස්ථාවලදී පිළියෙළ කරන ප්‍රධාන ආහාරයක්.\n* **ආප්ප සහ ඉඳිආප්ප:** උදෑසන හෝ රාත්‍රී ආහාරය සඳහා ඉතා ජනප්‍රියයි.\n* **කොත්තු රොටි:** ශ්‍රී ලංකාවේ වීදි ආහාර (street food) සංස්කෘතියේ ප්‍රධානතම අංගයක්.\n* **කැවුම් සහ කොකිස්:** සිංහල අලුත් අවුරුදු සමයේදී විශේෂයෙන් සාදන රසකැවිලි."}
]

# ==========================================
# 2. HELPER FUNCTIONS (Metrics, Sanitizer & Export)
# ==========================================
def get_sinhala_purity(text):
    """Calculates the percentage of Sinhala characters in the text."""
    if not text: return 0
    sinhala_chars = sum(1 for c in text if '\u0D80' <= c <= '\u0DFF')
    total_chars = sum(1 for c in text if c.isalnum() or '\u0D80' <= c <= '\u0DFF')
    if total_chars == 0: return 0
    return int((sinhala_chars / total_chars) * 100)

def sanitize_sinhala_output(text):
    """A post-processing filter to clean up common LLM Sinhala artifacts."""
    corrections = {
        "  ": " ",                 
        " ,": ",",                  
        " .": ".",                  
        "මම ...": "මම",            
        "ඔබගේ": "ඔබේ",              
        "කළ හැක": "කරන්න පුළුවන්",  
        "අන්තර්ජාලය": "ඉන්ටර්නෙට්"   
    }
    for error, fix in corrections.items():
        text = text.replace(error, fix)
    return text

def get_chat_download_string():
    """Formats the chat history for downloading (excluding the hidden dataset)."""
    chat_log = "Sinhala Chatbot - Offline Session Log\n" + "="*40 + "\n\n"
    # Only export messages AFTER the hardcoded dataset
    actual_conversation = st.session_state.get("messages", [])[len(HARDCODED_DATASET):]
    
    for msg in actual_conversation:
        role_name = "User" if msg["role"] == "user" else "Assistant"
        chat_log += f"{role_name}: {msg['content']}\n\n"
    return chat_log

# ==========================================
# 3. UI CONFIGURATION & SIDEBAR
# ==========================================
st.set_page_config(page_title="Sinhala AI Assistant", page_icon="🇱🇰")
st.title("Sinhala Tech & Local Assistant 🇱🇰")
st.caption("Offline AI powered by OLLAMA (singemma-4B) | Optimized via In-Context Learning")

st.sidebar.header("⚙️ Model Controls")
st.sidebar.write("Adjust inference dynamically:")

user_temp = st.sidebar.slider("Temperature (Creativity)", 0.0, 1.0, 0.3, 0.1)
user_top_p = st.sidebar.slider("Top-P (Focus)", 0.1, 1.0, 0.8, 0.1)

st.sidebar.divider()
st.sidebar.header("💾 Chat Management")

if st.sidebar.button("🗑️ Clear Conversation"):
    st.session_state["messages"] = list(HARDCODED_DATASET)
    st.rerun()

if st.sidebar.button("🔄 Regenerate Last Response"):
    # Ensure there is an actual user conversation to regenerate
    if len(st.session_state["messages"]) > len(HARDCODED_DATASET):
        # Remove the AI's last response from memory
        if st.session_state["messages"][-1]["role"] == "assistant":
            st.session_state["messages"].pop()
        # Set a flag to trigger the generation loop
        st.session_state["regenerate"] = True
        st.rerun()

st.sidebar.download_button(
    label="📥 Download Chat Log",
    data=get_chat_download_string(),
    file_name="sinhala_chat_history.txt",
    mime="text/plain"
)

# ==========================================
# 4. INITIALIZATION & UI RENDER (Hidden State)
# ==========================================
if "messages" not in st.session_state:
    st.session_state["messages"] = list(HARDCODED_DATASET)

# Only display the actual user conversation, HIDE the hardcoded training dataset
actual_conversation = st.session_state["messages"][len(HARDCODED_DATASET):]

for msg in actual_conversation:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Draw metrics if they exist in the history
        if "speed" in msg and "purity" in msg:
            cols = st.columns(2)
            cols[0].caption(f"⏱️ Speed: {msg['speed']}s")
            cols[1].caption(f"📝 Sinhala Purity: {msg['purity']}%")

# ==========================================
# 5. CHAT INPUT & LOCAL INFERENCE
# ==========================================
prompt = st.chat_input("මෙහි ටයිප් කරන්න... (Type your message here)")

# Trigger if the user types a new message OR clicks the regenerate button
if prompt or st.session_state.get("regenerate"):
    
    # If it's a NEW prompt, show it on screen and save it to history
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state["messages"].append({"role": "user", "content": prompt})
    else:
        # If we are regenerating, reset the flag (the user's message is already in history)
        st.session_state["regenerate"] = False

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        start_time = time.time()
        
        try:
            # --- CONTEXT LIMITER ---
            # Extract only the user's actual conversation history
            user_history = st.session_state["messages"][len(HARDCODED_DATASET):]
            
            # Combine the PERMANENT training dataset + the last 4 user interactions to save VRAM
            safe_context = HARDCODED_DATASET + user_history[-4:]
            
            for chunk in ollama.chat(
                model="Tharusha_Dilhara_Jayadeera/singemma",
                messages=safe_context,
                stream=True,
                options={
                    "temperature": user_temp,
                    "top_p": user_top_p,
                    "repeat_penalty": 1.25 # Aggressively kills token degeneration loops
                }
            ):
                token = chunk.get('message', {}).get('content', '')
                full_response += token
                response_placeholder.markdown(full_response + "▌")
            
            end_time = time.time()
            generation_time = round(end_time - start_time, 2)
            
            # --- APPLY THE LINGUISTIC SANITIZER ---
            cleaned_response = sanitize_sinhala_output(full_response)
            
            response_placeholder.markdown(cleaned_response)
            
            # --- SINHALA PURITY SCORER & METRICS ---
            purity_score = get_sinhala_purity(cleaned_response)
            
            cols = st.columns(2)
            cols[0].caption(f"⏱️ Speed: {generation_time}s")
            cols[1].caption(f"📝 Sinhala Purity: {purity_score}%")
            
            # Save the sanitized version AND the metrics to history!
            st.session_state["messages"].append({
                "role": "assistant", 
                "content": cleaned_response,
                "speed": generation_time,
                "purity": purity_score
            })
            
        except Exception as e:
            st.error(f"Ollama Error: {e}. Please ensure Ollama is running offline.")
            cleaned_response = "Error connecting to local model."
            # Save the error without metrics so it doesn't crash the render loop later
            st.session_state["messages"].append({"role": "assistant", "content": cleaned_response})