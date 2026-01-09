import streamlit as st
import requests

API_URL = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []


def ask(query: str) -> dict:
    try:
        with st.spinner("Asking the chatbot..."):
            response = requests.get(f"{API_URL}/ask", params={"query": query})
        
        if response.status_code == 200:
            data = response.json()
            return {
                "answer": data.get("answer", "No answer available"),
                "sources": data.get("sources", [])
            }
        else:
            return {"answer": "Error: Could not get response", "sources": []}
            
    except Exception as e:
        st.error(f"API Error: {e}")
        return {"answer": "Failed to connect to backend", "sources": []}

def clear_chat():
    """Clear all chat messages from session state"""
    st.session_state.messages = []

st.set_page_config(page_title="Airport RAG Assistant", page_icon="🤖")

# Header with Clear button
col1, col2 = st.columns([0.7, 0.3])   # give the button column more space
with col1:
    st.title("Chatbot RAG")
with col2:
    st.button(
        "🗑️ Clear Chat",
        on_click=clear_chat,
        type="secondary",            # or "primary" if you want stronger color
        use_container_width=True     # stretch to full column width
    )

st.divider()

# Chat input at TOP
query = st.chat_input(placeholder="Type your question here...")

if query:
    # Get AI response
    result = ask(query)
    answer = result.get("answer", "No answer available")
    sources = result.get("sources", [])
    
    # Insert AI answer FIRST (position 0)
    st.session_state.messages.insert(0, {
        "role": "assistant", 
        "content": answer,
        "sources": sources
    })
    
    # Then insert user question ABOVE it (also position 0)
    st.session_state.messages.insert(0, {
        "role": "user", 
        "content": query
    })
    
    st.rerun()
# Display messages (newest at top)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
# Initial greeting (only if no messages)
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.write("Hello! I'm your RAG Assistant. How can I help you today?")
