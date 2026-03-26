import streamlit as st
import time
# FIX: Ensure we import from answer.py (your actual current backend file)
from answer import answer_question

# --- PAGE CONFIG ---
# Wide mode looks better for chat interfaces
st.set_page_config(
    page_title="Insurellm Dark",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DARK MODE CUSTOM CSS ---
st.markdown("""
<style>
    /* 1. GLOBAL TEXT & HEADERS */
    h1, h2, h3, h4, h5, h6 {
        color: #FAFAFA !important;
        font-family: 'Inter', sans-serif;
    }
    p, div, label, .stMarkdown {
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif;
    }
    hr {
        border-color: #334155 !important;
    }

    /* 2. HIDE STREAMLIT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 3. CHAT BUBBLE STYLING */
    .stChatMessage {
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border: none;
    }
    
    /* USER Bubble (Right side, Dark Grey) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E293B; /* Slate 800 */
        border: 1px solid #334155;
    }
    
    /* AI Bubble (Left side, Deep Blue accent) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1D4ED8; /* Darker Blue */
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    /* Force text inside AI bubble to be pure white for contrast */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) * {
        color: white !important;
    }

    /* 4. INPUT CONTAINER STYLING */
    /* Makes the bottom input area blend into the dark background */
    .stChatInput {
        background-color: #0E1117;
        padding-bottom: 2rem;
    }
    /* Style the actual input box */
    .stTextInput input {
        background-color: #161B22 !important;
        color: #FAFAFA !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
    }

    /* 5. SIDEBAR POLISH */
    section[data-testid="stSidebar"] {
        background-color: #161B22; /* Slightly lighter dark */
        border-right: 1px solid #334155;
    }
    
    /* 6. EXPANDER (Sources) STYLING */
    .streamlit-expanderHeader {
        background-color: #1E293B !important;
        color: #FAFAFA !important;
        border-radius: 10px;
    }
    .streamlit-expanderContent {
        background-color: #161B22 !important;
        border: 1px solid #334155;
        border-radius: 0 0 10px 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTENT ---
with st.sidebar:
    # Using a white icon version for dark mode contrast
    st.image("https://cdn-icons-png.flaticon.com/512/9625/9625034.png", width=70)
    st.title("Insurellm Pro")
    st.caption("Enterprise Knowledge Cortex")
    st.markdown("---")
    
    # Dark mode metrics
    col1, col2 = st.columns(2)
    col1.metric("System", "Online", delta_color="off")
    col2.metric("Model", "Gemini 2.0", delta_color="off")
    
    st.markdown("### Control Panel")
    if st.button("🔄 Reset Conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.info("💡 **Tip:** The system can distinguish between greetings (like 'hi') and complex queries requiring database lookup.")

# --- MAIN CHAT LOGIC ---

# Initial Welcome Screen (only if history is empty)
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>Insurellm Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8 !important; font-size: 1.2rem;'>Secure access to policy documents, claims data, and operational guidelines.</p>", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    # Set different avatars for user vs AI
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Handle User Input
if prompt := st.chat_input("Query the knowledge base..."):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # 2. Assistant Response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        
        # A nice dark-mode spinner
        with st.spinner("Processing query..."):
            # Format history for backend
            history_formatted = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages[:-1]
            ]
            
            try:
                # Call your updated backend with the router
                answer, sources = answer_question(prompt, history_formatted)
                
                # Typing effect animation
                full_response = ""
                for chunk in answer.split():
                    full_response += chunk + " "
                    time.sleep(0.015) 
                    message_placeholder.markdown(full_response + "ꔷ")
                message_placeholder.markdown(full_response)
                
                # Dark Mode Source Citations
                if sources:
                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.expander(f"📚 Verified Sources ({len(sources)})"):
                        for i, source in enumerate(sources):
                            st.markdown(f"**Source {i+1}: {source.metadata.get('source', 'Unknown')}**")
                            # Using blockquote for source text distinction
                            st.markdown(f"> {source.page_content[:300]}...")
                            st.divider()
            
            except Exception as e:
                st.error(f"System Error: {e}")

    # 3. Save Assistant Message
    st.session_state.messages.append({"role": "assistant", "content": answer})