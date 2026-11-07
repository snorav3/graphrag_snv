import uvicorn
from fastapi import FastAPI

#from langchain.chains.retrieval import create_retrieval_chain
from pydantic import BaseModel

from gr1naivrag.collectors import collect_questions
from gr1naivrag.ingester import ingest_wikipedia_links_flat
from gr1naivrag.my_qdrant import LocalRagWithQdrant

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "wikipedia_rag"
EMBEDDING_MODEL = "granite-embedding:278m"
LLM_MODEL = "qwen2.5:0.5b"
#OLLAMA_URL = "http://localhost:11434"
SOURCES_FILE_PATH = "README.md"
QUESTIONS_FILE_PATH = "questions.md"


class ChatRequest(BaseModel):
    question: str


def naivrag():
    rag = LocalRagWithQdrant()
        
    # 1. Adatok betöltése
    #chunks = ingest_wikipedia_links_flat()
    #rag.ingest_into_qdrant(chunks)
    
    # 2/a. Kérdések kigyűjtése a fájlból
    questions = collect_questions(QUESTIONS_FILE_PATH)
    
    for ord, q in enumerate(questions, 1):
        print(f"\n\n================================ {ord}. KÉRDÉS ================================")
        rag.ask_question(q)

    # 2/b. Kérdés CLI-ből
    #while True:
    #    question = input("Írd be a kérdésed (kilépés: x): ")
    #    if question == "x":
    #        break
    #    rag.ask_question(question)

    # 2/c. FastAPI /api/chat endpointtal
    #app = FastAPI()
    #
    #@app.post("/api/chat")
    #def chat(request: ChatRequest):
    #    answer = rag.ask_question(request.question)
    #    return {"answer": answer}
    #
    #uvicorn.run(app, host="127.0.0.1", port=8000)

