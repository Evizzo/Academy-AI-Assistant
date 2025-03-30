import os
from dotenv import load_dotenv
from consts import MODEL_NAME, EXAM_DATES_FILE
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from prompts import examPrompt, generalPrompt
from logger import logger

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
logger.info("Google API key učitan iz .env okruženja.")

globalModel = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.05, google_api_key=google_api_key)
logger.info(f"Inicijalizovan globalModel sa modelom {MODEL_NAME}.")

def formatPrompt(promptTemplate, **variables):
    formatted = promptTemplate.format(**variables)
    logger.debug(f"Formatiran prompt: {formatted}")
    return formatted

def getExamDates():
    try:
        with open(EXAM_DATES_FILE, "r", encoding="utf-8") as f:
            examDates = json.load(f)
        logger.info("Učitani exam datumi.")
        return ", ".join([f"{name}: {date}" for name, date in examDates.items()])
    except Exception as e:
        logger.error(f"Greška pri učitavanju exam datuma: {e}")
        return ""

def orchestrateAgent(query, conversationHistory):
    logger.info(f"Orkestriram agenta za upit: {query}")
    if "ispit" in query.lower():
        return examAgent(query, conversationHistory)
    else:
        return generalAgent(query, conversationHistory)

def runAgent(query, conversationHistory, promptTemplate, **promptVars):
    formattedPrompt = formatPrompt(promptTemplate, **promptVars) if promptVars else promptTemplate

    shortTermMemory = "\n".join([f'{msg["sender"]}: {msg["content"]}' for msg in conversationHistory])

    messages = [
        {"role": "system", "content": formattedPrompt + "\nShort term memory:\n" + shortTermMemory},
        {"role": "user", "content": query}
    ]
    logger.debug(f"Pozivam globalModel sa porukama: {messages}")

    try:
        response = globalModel.invoke(messages).content.strip()
    except Exception as e:
        logger.error(f"Greška pri pozivu globalModel.invoke: {e}")
        response = "Došlo je do greške."

    logger.info("Odgovor primljen od globalModel-a.")
    return response

def examAgent(query, conversationHistory):
    logger.info("Korišćenje exam agenta.")
    return runAgent(query, conversationHistory, examPrompt, examDates=getExamDates())

def generalAgent(query, conversationHistory):
    logger.info("Korišćenje general agenta.")
    return runAgent(query, conversationHistory, generalPrompt)
