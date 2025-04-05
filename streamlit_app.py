import streamlit as st
import os
import time
import json
from conversation_manager import loadConversations, createNewChat, getChat, deleteChat, getConversationsForClient
from endpoints import handleUserMessage

def loadClients():
    json_path = "clients.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        st.error("Fajl clients.json nije pronađen!")
        return {"users": []}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Korisničko ime")
    password = st.text_input("Lozinka", type="password")
    if st.button("Prijavi se"):
        clients = loadClients()
        valid = any(user["username"] == username and user["password"] == password for user in clients.get("users", []))
        if valid:
            st.session_state.logged_in = True
            st.session_state.client_id = username
            st.rerun()
        else:
            st.error("Neispravno korisničko ime ili lozinka")
    st.stop()

chats = getConversationsForClient(st.session_state.client_id)

if "selected_chat_id" not in st.session_state:
    st.session_state.selected_chat_id = None
if "initialized" not in st.session_state:
    new_chat = createNewChat("Novi Chat", st.session_state.client_id)
    st.session_state.selected_chat_id = new_chat["id"]
    st.session_state.initialized = True

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

st.sidebar.header("Chat istorija")

if st.sidebar.button("Kreiraj novi chat"):
    new_chat = createNewChat("Novi Chat", st.session_state.client_id)
    st.session_state.selected_chat_id = new_chat["id"]
    st.rerun()

st.sidebar.write("---")

if chats:
    for chat in chats:
        cols = st.sidebar.columns([0.8, 0.2])
        with cols[0]:
            if st.button(f"{chat['chatName']} ({chat['id'][:8]})", key=f"select_{chat['id']}"):
                st.session_state.selected_chat_id = chat["id"]
                st.rerun()
        with cols[1]:
            if st.button("🗑️", key=f"delete_{chat['id']}"):
                deleteChat(chat["id"], st.session_state.client_id)
                chats = getConversationsForClient(st.session_state.client_id)
                st.session_state.selected_chat_id = chats[0]["id"] if chats else None
                st.rerun()
else:
    st.sidebar.write("Nema kreiranih chat-ova. Kliknite 'Kreiraj novi chat'.")

selected_chat = getChat(st.session_state.selected_chat_id, st.session_state.client_id) if st.session_state.selected_chat_id else None

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
if selected_chat:
    if selected_chat.get("messages"):
        for msg in selected_chat["messages"]:
            alignment = "user" if msg["sender"] == "User" else "bot"
            st.markdown(
                f"""
                <div class="message-wrapper {alignment}">
                    <div class="chat-bubble {alignment}">{msg['content']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.markdown("<p>Nema poruka u ovom chatu.</p>", unsafe_allow_html=True)
else:
    st.markdown("<h1><strong>Dobrodošli na chatbot Akademij!<br>Kreirajte novi chat da započnete konverzaciju.</strong></h1>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if selected_chat:
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Poruka", placeholder="Unesite poruku...", key="user_input", label_visibility="collapsed")
        send_button = st.form_submit_button("Pošalji")

    if send_button and user_input.strip():
        with st.spinner("Molim sačekajte, obrađujem vašu poruku..."):
            handleUserMessage(st.session_state.selected_chat_id, user_input)
            time.sleep(1)
        st.rerun()
