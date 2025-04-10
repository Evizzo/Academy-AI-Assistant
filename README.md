To run use ```streamlit run streamlit_app.py```

Needed env variables
```
GOOGLE_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
TOP_K=15
EMBEDDING_MODEL="text-embedding-3-large"
LLM_MODEL_NAME = "gemini-2.0-flash"
``` 


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
