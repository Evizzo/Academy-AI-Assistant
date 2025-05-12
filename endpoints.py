from consts import MAX_INPUT_TOKENS, MAX_SIZE_SHORT_TERM_MEMORY
from conversation_manager import createMessage, getLastMessages
from agents import orchestrateAgent
from inputValidation import numTokens
from scrapeAndVectorise import cyrillicToLatin


def handleUserMessage(chat_id, user_text):
    if numTokens(user_text) > MAX_INPUT_TOKENS:
        warning = "Vaša poruka je prevelika za obradu. Molimo Vas, pokušajte je skratiti."
        createMessage(chat_id, warning, "Bot")
        return
    createMessage(chat_id, user_text, "User")
    history = getLastMessages(chat_id, n=MAX_SIZE_SHORT_TERM_MEMORY)
    response = orchestrateAgent(user_text, history)
    createMessage(chat_id, cyrillicToLatin(response), "Bot")