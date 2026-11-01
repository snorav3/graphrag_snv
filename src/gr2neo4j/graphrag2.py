import os

from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

from gr2neo4j.populate_graph_db import upsert_domain_graph, upsert_graph_from_wiki_pages
from gr2neo4j.query_graph_db import run_diagnostic_report, setup_graph_rag
from gr2neo4j.questions import QUESTIONS
from gr2neo4j.wikis import WIKI_PAGES

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "my_passwd")

CHAT_MODEL = "qwen2.5:0.5b"


def neo4j():
    graph = Neo4jGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, refresh_schema=False)
    
    # 1. Gráf feltöltése saját seed adatokkal:
    #upsert_domain_graph(graph)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    
    # 2. Gráf feltöltése a valódi dokumentumokkal (Wikipédia-oldalakból kivonatolva):
    #upsert_graph_from_wiki_pages(graph, WIKI_PAGES)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
        
    # 3. Lekérdezések:    
    #gr_chain = setup_graph_rag(graph, CHAT_MODEL)
    #
    #for q in QUESTIONS:
    #    print(f"\nKérdés: {q}\n")
    #    print("Válasz: \n")
    #    print(gr_chain.invoke(input={"query": q})["result"])
    #-------------------------------------------------------
    run_diagnostic_report(graph)
    
    