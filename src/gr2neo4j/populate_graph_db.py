#import time
#from datetime import datetime

#import wikipedia
#from langchain_community.document_loaders import WikipediaLoader
from langchain_community.graphs import Neo4jGraph

#from langchain_text_splitters import RecursiveCharacterTextSplitter
from gr1naivrag.ingester import ingest_wikipedia_links
from gr2neo4j.cyphers import CONSTRAINT_CYPHERS, SEED_CYPHERS


def set_constraints(graph: Neo4jGraph):
    print(f"{len(CONSTRAINT_CYPHERS)} db CONSTRAINT-CYPHER-parancsok kötegelt végrehajtása...")
    
    batch_query = """
    CALL apoc.cypher.runMany($queries, {})
    """
    
    try:
        combined_queries = ";\n".join(CONSTRAINT_CYPHERS)
        graph.query(batch_query, {"queries": combined_queries})
        print("Minden CONSTRAINT-CYPHER-parancs sikeresen végrehajtva!")
    except Exception as e:
        print(f"Hiba történt a batch végrehajtása közben (constraints): {e}")

def upsert_domain_graph(graph: Neo4jGraph):
    ##with graph:
    #for idx, cypher in enumerate(SEED_CYPHERS, 1):
    #    graph.query(cypher)
    #    print(f"[{idx}/{len(SEED_CYPHERS)}] sikeresen végrehajtva")
    print(f"{len(SEED_CYPHERS)} db SEED-CYPHER-parancsok kötegelt végrehajtása...")
    
    batch_query = """
    CALL apoc.cypher.runMany($queries, {})
    """
    
    try:
        #graph.query(batch_query, {"queries": SEED_CYPHERS})
        combined_queries = ";\n".join(SEED_CYPHERS)
        graph.query(batch_query, {"queries": combined_queries})
        print("Minden SEED-CYPHER-parancs sikeresen végrehajtva!")
    except Exception as e:
        print(f"Hiba történt a batch végrehajtása közben (seed): {e}")

####################################################################################################
# #unused!
# #wikipedia.set_user_agent("GepjarmuGrafExtrakcio/1.0 (kapcsolat: snorav3@gmail.com)")
#
# #unused!
# def upsert_graph_from_wiki_pages(graph: Neo4jGraph, pages):
#     wiki_chunks_data = load_and_chunk_wikipedia(pages)
#    
#     if wiki_chunks_data:
#         upsert_document_graph(graph, wiki_chunks_data)
#         print("A dokumentum-gráf sikeresen elkészült!")
#     else:
#         print("Nem sikerült adatot letölteni a Wikipédiáról.")
#    
# #unused!
# def load_and_chunk_wikipedia(pages):
#     all_chunks = {}
#    
#     # 1000 karakteres chunkok
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200
#     )
#    
#     for page in pages:
#         print(f"'{page}' Wikipédia-oldal letöltése...")
#         try:
#             loader = WikipediaLoader(query=page, load_max_docs=1, lang="hu")
#             docs = loader.load()
#            
#             if not docs:
#                 loader = WikipediaLoader(query=page, load_max_docs=1, lang="en")
#                 docs = loader.load()
#                
#             if docs:
#                 doc = docs[0]
#                 chunks = text_splitter.split_documents([doc])
#                 for chunk_idx, chunk in enumerate(chunks):
#                     chunk.metadata["chunk_idx"] = chunk_idx
#
#                 all_chunks[page] = {
#                     "title": page,
#                     "source_url": doc.metadata.get("source", f"https://wikipedia.org{page}"),
#                     "source_id": f"wiki_{page.lower().replace(' ', '_')}", # pl: wiki_volvo_trucks
#                     "downloaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     "chunks": chunks
#                 }
#                 print(f"Létrejött {len(chunks)} db chunk a(z) '{page}' oldalhoz.")
#             else:
#                 print(f"Nem található tartalom a(z) '{page}' oldalhoz.")
#         except Exception as e:
#             print(f"Hiba a(z) '{page}' oldal letöltésekor: {e}")
#            
#         time.sleep(1.5)
#        
#     return all_chunks
####################################################################################################

def upsert_graph_from_wiki_urls(graph: Neo4jGraph, urls: list[str]):
    wiki_chunks_data = ingest_wikipedia_links(urls)
    
    if wiki_chunks_data:
        upsert_document_graph(graph, wiki_chunks_data)
        print("A dokumentum-gráf sikeresen elkészült!")
    else:
        print("Nem sikerült adatot letölteni a Wikipédiáról.")


def upsert_document_graph(graph: Neo4jGraph, graph_data):    
    print("\nAdatok feltöltése a Neo4j-be...")
    
    #for data in graph_data.items(): ==> for page_key, data in graph_data.items(): ==>
    for data in graph_data.values():
        doc_title = data["title"]
        source_url = data["source_url"]
        chunks = data["chunks"]
        
        doc_query = """
        MERGE (d:Document {id: $doc_id})
        SET d.title = $title, d.source = $source, d.downloaded_at = $downloaded_at
        """
        graph.query(doc_query, {"doc_id": doc_title, "title": doc_title, "source": source_url})
        
        prev_chunk_id = None
        
        for idx, chunk in enumerate(chunks, 1):
            chunk_id = f"{doc_title}_chunk_{idx}"
            chunk_text = chunk.page_content
            
            chunk_query = """
            MATCH (d:Document {id: $doc_id})
            MERGE (c:Chunk {id: $chunk_id})
            SET c.text = $text, c.sequence = $sequence, c.chunk_idx = $chunk_idx
            MERGE (d)-[:CONTAINS]->(c)
            """
            graph.query(chunk_query, {
                "doc_id": doc_title,
                "chunk_id": chunk_id,
                "text": chunk_text,
                "sequence": idx,
                "chunk_idx": chunk.metadata["chunk_idx"]
            })
            
            if prev_chunk_id:
                next_chunk_query = """
                MATCH (prev:Chunk {id: $prev_id}), (curr:Chunk {id: $curr_id})
                MERGE (prev)-[:NEXT_CHUNK]->(curr)
                """
                graph.query(next_chunk_query, {
                    "prev_id": prev_chunk_id,
                    "curr_id": chunk_id
                })
                
            prev_chunk_id = chunk_id
            
        print(f"'{doc_title}' sikeresen elmentve a gráf-db-be.")
