📘 Project Name: Academy Assistant

A multilingual virtual assistant designed for the needs of students and staff at a higher education institution.
It combines Retrieval-Augmented Generation (RAG) with multi-agent orchestration to provide accurate, structured, and context-aware academic support.

⸻

🚀 Overview

Academy Assistant delivers:

 •	Structured Q&A for exam schedules, academic deadlines and information about exams
	
 •	Informational responses about general information about the institution
	
 •	Multilingual support with formal tone and Serbian Latin (Ekavian) script

It blends LLM reasoning with semantic vector search to ensure grounded answers based strictly on available data.

⸻

🧠 Features

•	Example prompts:
	“When is the Programming 101 exam?”
	“What date is the Math final?”

•	Uses semantic search + LLM synthesis for factual answers.

•	Embedding & Vector Search

•	Text embedded with paraphrase-multilingual-MiniLM-L12-v2.

•	Stored in Pinecone with metadata for fast, semantic retrieval.

•	Web Scraping + Chunking

•	Transliterates Cyrillic to Latin.

•	Cleans HTML and removes irrelevant sections.

•	Chunks content using RecursiveCharacterTextSplitter.

•	Short-Term Memory

•	User sessions and chat history stored securely in MySQL.

•	Streamlit Frontend

⸻

🛠️ Setup Instructions

### Prerequisites

Before setting up the Academy Assistant, ensure you have the following installed:
- Python 3.8+ with pip
- MySQL Server
- Git

### Step-by-Step Installation

#### 0. Clone the Repository

```bash
git clone <repository-url>
cd student-chatbot
```

#### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Setup MySQL Database

**Install MySQL** (if not already installed):
- Ubuntu/Debian: `sudo apt install mysql-server`
- macOS: `brew install mysql`
- Windows: Download from [MySQL official website](https://dev.mysql.com/downloads/installer/)

**Configure MySQL:**
1. Start MySQL service:
   ```bash
   sudo systemctl start mysql
   ```

2. Create a database and user:
   ```sql
   mysql -u root -p
   CREATE DATABASE asssar_db;
   CREATE USER 'admin'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON asssar_db.* TO 'admin'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

3. Create the required tables using the schema provided below.

#### 3. Configure Database Connection

Create/update `.streamlit/secrets.toml` with your MySQL credentials:

```toml
[mysql]
host = "localhost"
port = 3306
database = "asssar_db"
user = "admin"
password = "password"
```

**Important:** Replace the credentials with your actual MySQL setup.

#### 4. Create Database Tables

Execute the following SQL commands in your MySQL database:

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

#### 5. Setup Pinecone Vector Database

1. **Create Pinecone Account:**
   - Visit [Pinecone.io](https://www.pinecone.io/)
   - Sign up for a free account

2. **Create Pinecone Index:**
   - Log into Pinecone console
   - Create a new index with the following specifications:
     - Dimensions: 384 (for paraphrase-multilingual-MiniLM-L12-v2)
     - Metric: cosine
     - Cloud & Region: us-east-1

3. **Get API Key:**
   - Navigate to API Keys section in Pinecone console
   - Generate a new API key

#### 6. Setup Google AI Studio API

1. **Get Google AI API Key:**
   - Visit [AI Studio](https://aistudio.google.com/)
   - Sign in with your Google account
   - Generate a new API key

#### 7. Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_ai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=your_pinecone_index_name_here
TOP_K=25
LLM_MODEL_NAME="gemini-2.5-flash-preview-05-20" # This is currently latest gemini 2.5 flash model code
```

#### 8. Prepare Your Data

1. **Add your content to data files:**
   - `dataToVectorise/data.txt` - Add your general content (separated by sentences)
   - `dataToVectorise/pData.txt` - Add structured content using `----------------` as separator

2. **Example data format:**
   - **data.txt:** Regular text content with natural sentence breaks
   - **pData.txt:** Structured content with `----------------` separating different sections

#### 9. Vectorise Your Data

Run the vectorization script twice to process both data files:

```bash
# First run - process data.txt with sentence-based chunking
python vectorise.py
# Select option 1 (sentence-based chunking)
# Enter file path: dataToVectorise/data.txt

# Second run - process pData.txt with delimiter-based chunking  
python vectorise.py
# Select option 2 (delimiter-based chunking)
# Enter file path: dataToVectorise/pData.txt
```

#### 10. Scrape and Embed Web Content

If you want to include web-scraped content:

```bash
python scrapeAndVectorise.py
```

This will scrape content from configured websites, process it, and upload to Pinecone.

#### 11. Configure Application Port 

Modify `.streamlit/config.toml` to change the default port (currently set to 5000):

```toml
[server]
port = 5000  # Change to your desired port
```

#### 12. Launch the Application

```bash
streamlit run streamlit_app.py
```

#### 13. Access the Application

1. Open your web browser
2. Navigate to `http://localhost:5000` (or your configured url)
3. Wait for the application to initialize on first run
4. Log in using the MySQL credentials you configured

### Usage

Once setup is complete:

1. **Authentication:** Log in using your MySQL database credentials
2. **Chat Interface:** Start asking questions about exam schedules, academic information, etc.

⸻

⚙️ Environment Variables

GOOGLE_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
TOP_K=25
LLM_MODEL_NAME="gemini-2.5-flash-preview-05-20"

⸻

🗄️ Database Schema

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