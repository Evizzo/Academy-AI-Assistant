import os
from dotenv import load_dotenv
from consts import EXAM_DATES_FILE
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from prompts import examPrompt, generalPrompt, orchestrationAgent
from logger import logger

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

globalModel = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=0.05, google_api_key=GOOGLE_API_KEY)
logger.info(f"Inicijalizovan globalModel sa modelom {LLM_MODEL_NAME}.")

def formatPrompt(promptTemplate, **variables):
    formatted = promptTemplate.format(**variables)
    logger.debug(f"Formatiran prompt: {formatted}")
    return formatted

def getExamDates():
    try:
        with open(EXAM_DATES_FILE, "r", encoding="utf-8") as f:
            examDetails = json.load(f)
        logger.info("Učitani exam detalji.")
        formatted_details = []
        for exam in examDetails:
            predmet = exam.get("predmet", "Nepoznato")
            profesor = exam.get("profesor", "Nepoznat")
            datum = exam.get("datum", "Nepoznat")
            vise_detalja = exam.get("vise_detalja", "Nema dodatnih informacija")
            formatted_details.append(
                f"Predmet: {predmet}, Profesor: {profesor}, Datum: {datum}, Detalji: {vise_detalja}"
            )
        return "\n".join(formatted_details)
    except Exception as e:
        logger.error(f"Greška pri učitavanju exam detalja: {e}")
        return ""

def orchestrateAgent(query, conversationHistory):
    logger.info(f"Orkestriram agente za upit: {query}")
    response = runAgent(query, conversationHistory, orchestrationAgent)
    logger.info(f"Odabrani agent je: **{response}**")
    if response == "Ne znam.":
        return "Molim pokusajte ponovo"
    if response == 'exam':
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
    return runAgent(query, conversationHistory, examPrompt, examDetails=getExamDates())

def generalAgent(query, conversationHistory):
    logger.info("Korišćenje general agenta.")
    return runAgent(query, conversationHistory, generalPrompt)
