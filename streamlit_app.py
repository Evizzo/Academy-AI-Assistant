import streamlit as st
import os
from conversation_manager import loadConversation
from endpoints import handleUserMessage

def load_custom_css():
    css_path = os.path.join(".streamlit", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error("Nedostaje .streamlit/styles.css fajl!")

st.set_page_config(
    page_title="Chatbot – Akademija",
    page_icon="images/favicon.png",
    layout="wide"
)
load_custom_css()

st.sidebar.header("Istorija četa")
conversationData = loadConversation()
for msg in conversationData["messages"]:
    prefix = "Vi:" if msg["sender"] == "User" else "Bot:"
    short_content = msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
    st.sidebar.markdown(f"**{prefix}** {short_content}")

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in conversationData["messages"]:
    alignment = "user" if msg["sender"] == "User" else "bot"
    st.markdown(
        f"""
        <div class="message-wrapper {alignment}">
            <div class="chat-bubble {alignment}">{msg['content']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown("</div>", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Poruka", placeholder="Unesite poruku...", key="user_input", label_visibility="collapsed")
    send_button = st.form_submit_button("Pošalji")

if send_button and user_input.strip():
    handleUserMessage(user_input)
    st.rerun()
