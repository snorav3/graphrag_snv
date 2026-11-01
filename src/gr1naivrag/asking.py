
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from gr1naivrag.my_qdrant import LocalRagWithQdrant


def ask_question(rag: LocalRagWithQdrant, question: str):
        """Létrehozza a RAG láncot és megválaszolja a kérdést a kontextus alapján."""
        print(f"\n[Keresés] Releváns dokumentumok kigyűjtése a kérdéshez: '{question}'")
        
        # Vector Store -> Retriever
        retriever = rag.vector_store.as_retriever(search_kwargs={"k": 5}) # A top 5 legközelebbi darabot kéri le
        
        # Prompt tamplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", "A következő kikeresett kontextus alapján válaszolj a kérdésre magyarul. "
                       "Ha nem találod a választ a kontextusban, mondd azt, hogy nem tudod, ne találj ki semmit.\n\nKontextus:\n{context}"),
            ("user", "{input}")
        ])
        
        # LangChain
        question_answer_chain = create_stuff_documents_chain(rag.llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        response = rag_chain.invoke({"input": question})
        
        print("\n============================ LOKÁLIS AI VÁLASZ =============================")
        print(response["answer"])

        # Források
        print("================================ FORRÁSOK ==================================")
        for i, doc in enumerate(response["context"], 1):
            src_loc = doc.metadata.get("source", "Ismeretlen forrás")
            page_num = doc.metadata.get("page", "-")
            print(f"[{i}] {src_loc} (Oldal: {page_num})")
            #print(f"    Idézet: {doc.page_content[:100]}...")
        
        print("----------------------------------------------------------------------------\n")

        return response["answer"]
