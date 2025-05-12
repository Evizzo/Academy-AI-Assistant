# 📘 Project Name: **Academy Assistant**

A professional multilingual chatbot tailored for the needs of students and staff at the Academy of Vocational Studies – Šumadija, Aranđelovac department. 
It combines Retrieval-Augmented Generation (RAG) techniques with multi-agent orchestration to deliver highly accurate and context-aware academic support.

---

## 🚀 Overview

**Academy Assistant** is an intelligent virtual assistant built to support academic information delivery through:

* Accurate and professional Q\&A on exam schedules
* General information about academic processes and departments
* Context-aware multilingual support

The chatbot strictly adheres to communication rules, uses Serbian Latin (ekavian), and leverages a combination of LLMs and semantic search.

---

## 🧠 Features

* **Agent Orchestration**: Automatically classifies user questions into two categories — *exam-related* and *general* — and routes them to the appropriate agent.

* **Exam Agent**:

  * Specializes in answering only exam-related questions.
  * Uses a fixed, reliable data source from the database.
  * Rejects any questions not strictly related to exam schedules.
  * Always responds in professional tone and Serbian Latin script.
  * Examples it can handle:

    * "Kada je sledeći ispit iz predmeta Matematika?"
    * "Koji je datum ispita za Osnove programiranja?"

* **General Info Agent**:

  * Handles all other inquiries about the academy's organization, staff, location, enrollment, programs, and administrative matters.
  * Incorporates retrieved context using vector search to improve response accuracy.

* **Embedding & Vector Search**:

  * Converts documents into vector representations using `paraphrase-multilingual-MiniLM-L12-v2`.
  * Uses Pinecone to search relevant context for the general agent.

* **Web Scraping + Chunking Pipeline**:

  * Scrapes raw text from the official department website `https://ar.asss.edu.rs/`.
  * Converts cyrillic text to Latin.
  * Cleans HTML by removing irrelevant sections like navigation, scripts, and styles.
  * Splits content using LangChain's `RecursiveCharacterTextSplitter` to maintain semantic coherence.
  * Each chunk is vectorized and stored in Pinecone for future retrieval.

* **Short-Term Memory**:

  * Keeps last N messages for continuity and context-awareness.

* **Secure Client Login**:

  * User sessions are authenticated via username/password stored in a MySQL DB.
  * Users can view and manage their past conversations.

* **Streamlit Frontend**:

  * Clean and responsive UI for chatting.
  * Chat history, message styling, and system notifications included.

---

## 🧰 Tech Stack

* **Python**
* **LangChain + Google Gemini**
* **SentenceTransformers**
* **Pinecone** (semantic vector search)
* **Streamlit** (UI)
* **MySQL** (chat/message persistence)

---

## ✅ Usage

### 1. Scrape and embed data

```bash
python scrapeAndVectorise.py
```

This will scrape the content of the department website, chunk the text semantically, embed it, and upload to Pinecone.

### 1.1 Embed data from file

```bash
python vectorse.py
```

This will embed data from a file, and chunk it either by separator or by sentences.

### 2. Run app

```bash
streamlit run your_main_file.py
```

### 3. Login

Use predefined MySQL users to authenticate.

---

# To run use ```streamlit run streamlit_app.py```

# Needed env variables
```
GOOGLE_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
TOP_K=20
EMBEDDING_MODEL="text-embedding-3-large"
LLM_MODEL_NAME = "gemini-2.0-flash"
``` 

# Database schema setup
```sql
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE examDates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    predmet VARCHAR(255) NOT NULL,
    profesor VARCHAR(255) NOT NULL,
    datum DATE NOT NULL,
    vise_detalja TEXT
);

CREATE TABLE conversations (
    id CHAR(36) PRIMARY KEY,
    client_id INT NOT NULL,
    chatName VARCHAR(255) NOT NULL,
    messages JSON NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);
```