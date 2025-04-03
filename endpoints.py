from conversation_manager import createMessage, getLastMessages
from agents import orchestrateAgent

def handleUserMessage(chat_id, user_text):
    createMessage(chat_id, user_text, "User")
    history = getLastMessages(chat_id, n=5)
    response = orchestrateAgent(user_text, history)
    createMessage(chat_id, response, "Bot")