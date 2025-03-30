from conversation_manager import createMessage, getLastMessages
from agents import orchestrateAgent

def handleUserMessage(query):
    createMessage(query, "User")
    lastMessages = getLastMessages(5)
    response = orchestrateAgent(query, lastMessages)
    createMessage(response, "Bot")
    return response
