from operator import itemgetter

#from langchain_classic.chains import create_retrieval_chain
#from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "wikipedia_rag"
EMBEDDING_MODEL = "granite-embedding:278m"
LLM_MODEL = "qwen2.5:0.5b"
#OLLAMA_URL = "http://localhost:11434"


class LocalRagWithQdrant:
    def __init__(self):
        print("[RAG] Lokális modellek és kliensek inicializálása...")
        
        # 1. Ollama embedding & chat model
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        self.llm = ChatOllama(model=LLM_MODEL, temperature=0.2)
        
        # 2. Qdrant client & Vector Store
        self.qdrant_client = QdrantClient(url=QDRANT_URL)
        self.__init_qdrant_collection()
        
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=COLLECTION_NAME,
            embedding=self.embeddings
        )

    def __init_qdrant_collection(self):
        if not self.qdrant_client.collection_exists(COLLECTION_NAME):
            self.qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=768, # A granite-embedding:278m modell 768 dimenziós vektorokat gyárt
                    distance=Distance.COSINE
                )
            )
            print(f"[Qdrant] '{COLLECTION_NAME}' kollekció sikeresen létrehozva.")

    # store chunks
    def ingest_into_qdrant(self, chunks: list[Document]) -> None:
        # Embedding & save vectors into Qdrant
        print("[Qdrant] Vektorok generálása és mentése az adatbázisba...")
        self.vector_store.add_documents(chunks)
        print("[Rendszer] Sikeres indexelés!")

############################################################## ASK QUESTIONS: ##############################################################

    def ask_question(self, question: str):
        """Létrehozza a RAG láncot és megválaszolja a kérdést a kontextus alapján."""
        print(f"\n[Keresés] Releváns dokumentumok kigyűjtése a kérdéshez: '{question}'")
        
        # Vector Store -> Retriever
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5}) # A top 5 legközelebbi darabot kéri le
        
        # Prompt tamplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "A következő kikeresett kontextus alapján válaszolj a kérdésre magyarul. "
                "Ha nem találod a választ a kontextusban, mondd azt, hogy nem tudod, ne találj ki semmit.\n\nKontextus:\n{context}"
            )),
            ("user", "{input}")
        ])
        
        # LangChain
        #question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        #rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        # or with pipes:
        document_chain = (
            {
                "context": itemgetter("context")
                | RunnableLambda(
                    lambda documents: "\n\n".join(
                        document.page_content for document in documents
                    )
                ),
                "input": itemgetter("input"),
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        rag_chain = (
            RunnablePassthrough.assign(context=itemgetter("input") | retriever)
            | RunnablePassthrough.assign(answer=document_chain)
        )

        print("\n============================ LOKÁLIS AI VÁLASZ =============================")
        # direct answer:
        #response = rag_chain.invoke({"input": question})
        #print(response["answer"])
        
        # tokenized (streaming) answer:
        answer_parts: list[str] = []
        context = []

        for chunk in rag_chain.stream({"input": question}):
            if "context" in chunk:
                context = chunk["context"]
            answer_chunk = chunk.get("answer")
            if answer_chunk:
                print(answer_chunk, end="", flush=True)
                answer_parts.append(answer_chunk)
        print()

        # Források
        print("================================ FORRÁSOK ==================================")
        for i, doc in enumerate(context, 1):
            src_loc = doc.metadata.get("source", "Ismeretlen forrás")
            page_num = doc.metadata.get("page", "-")
            print(f"[{i}] {src_loc} (Oldal: {page_num})")
            #print(f"    Idézet: {doc.page_content[:100]}...")
        
        print("----------------------------------------------------------------------------\n")

        return "".join(answer_parts)
