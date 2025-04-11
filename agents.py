import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from db import getDbConnection
from prompts import examPrompt, generalPrompt, orchestrationAgent
from logger import logger
from vectorSearch import search_context

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

globalModel = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=0.75, google_api_key=GOOGLE_API_KEY)
logger.info(f"Inicijalizovan globalModel sa modelom {LLM_MODEL_NAME}.")

def runAgentSimple(query, promptTemplate):
    messages = [
        {"role": "system", "content": promptTemplate},
        {"role": "user", "content": query}
    ]

    try:
        response = globalModel.invoke(messages).content.strip()
    except Exception as e:
        logger.error(f"Greška pri pozivu globalModel.invoke: {e}")
        response = "Došlo je do greške."
    return response

def formatPrompt(promptTemplate, **variables):
    formatted = promptTemplate.format(**variables)
    logger.debug(f"Formatiran prompt: {formatted}")
    return formatted

def getExamDates():
    try:
        connection = getDbConnection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT predmet, profesor, datum, vise_detalja FROM examDates"
        cursor.execute(query)
        rows = cursor.fetchall()
        formatted_details = []
        for exam in rows:
            predmet = exam.get("predmet", "Nepoznato")
            profesor = exam.get("profesor", "Nepoznat")
            datum = exam.get("datum", "Nepoznat")
            vise_detalja = exam.get("vise_detalja", "Nema dodatnih informacija")
            formatted_details.append(
                f"Predmet: {predmet}, Profesor: {profesor}, Datum: {datum}, Detalji: {vise_detalja}"
            )
        cursor.close()
        connection.close()
        logger.info("Učitani exam detalji iz baze.")
        return "\n".join(formatted_details)
    except Exception as e:
        logger.error(f"Greška pri učitavanju exam detalja iz baze: {e}")
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

def runAgent(query, conversationHistory, promptTemplate, vector_search=False, **promptVars):
    if vector_search:
        vector_context = search_context(query)
        promptVars["context"] = vector_context

    formattedPrompt = formatPrompt(promptTemplate, **promptVars) if promptVars else promptTemplate

    shortTermMemory = "\n".join([f'{msg["sender"]}: {msg["content"]}' for msg in conversationHistory])

    messages = [
        {"role": "system", "content": formattedPrompt + "\nShort term memory:\n" + shortTermMemory},
        {"role": "user", "content": query}
    ]

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
    return runAgent(query, conversationHistory, generalPrompt, vector_search=True)
