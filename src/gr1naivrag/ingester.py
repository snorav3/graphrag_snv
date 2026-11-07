from datetime import UTC, datetime

import bs4

#from langchain_classic.document_loaders import WebBaseLoader
#from langchain_classic.schema import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.runnables import chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.base import TextSplitter

from gr1naivrag.collectors import collect_wikipedia_links

SOURCES_FILE_PATH = "README.md"


#@chain
def ingest_wikipedia_links_flat() -> list[Document]:    
    ingestion_chain = load_wiki_docs_4_vectors | split_wiki_docs | add_metadata_2_chunks
    chunks = ingestion_chain.invoke(None)

    print(f"[Ingestion] A szövegek {len(chunks)} darabra (chunk) lettek felvágva.")
    return chunks

#@chain
def ingest_wikipedia_links(urls: list[str]) -> list[Document]:
    # sima verzió:
    #docs = []
    #for gidx, url in enumerate(urls):
    #    doc = load_wiki_docs_4_graphs.invoke(url)
    #    doc = add_metadata_2_doc.invoke(gidx, doc)
    #    docs.extend(doc)
    # pipeline-verzió:
    ingestion_pipe = load_wiki_docs_4_graphs | add_metadata_2_doc
    docs = ingestion_pipe.map([ (idx, url) for idx, url in enumerate(urls) ])

    print(f"[Ingestion] {len(docs)} darab Wikipédia-szöveg lett feldolgozva.")
    return docs


@chain
def load_wiki_docs_4_vectors(_) -> list[Document]:
    # Wikipédia források (Magyar Wikipédia oldalak)
    wiki_urls = collect_wikipedia_links(SOURCES_FILE_PATH)
    loader = load_wiki_docs_4_vectors_from(wiki_urls)
    
    return loader.load()

def load_wiki_docs_4_vectors_from(urls: list[str]) -> WebBaseLoader:
    """"Letölti a HTML oldalakat (load)..."""
    print(f"[Ingestion] {len(urls)} Wikipédia link beolvasása...")
    
    # HTML Loader (BeautifulSoup)
    loader = WebBaseLoader(
        web_paths=urls,
        bs_kwargs={
            "parse_only": bs4.SoupStrainer(id="mw-content-text"), # Csak a Wikipédia érdemi szövegtörzse kell
        },
    )
    
    return loader

@chain
def load_wiki_docs_4_graphs(url: str) -> Document:
    loader = load_wikipedia_4_graphs_from(url)
    docs = loader.load()
    return docs[0]

def load_wikipedia_4_graphs_from(url: str) -> WebBaseLoader:
    """"Letölti a HTML oldalakat (load)..."""
    print(f"[Ingestion] {url} Wikipédia link beolvasása...")
    
    # HTML Loader (BeautifulSoup)
    loader = WebBaseLoader(
        web_paths=url,
        bs_kwargs={
            "parse_only": bs4.SoupStrainer(id="mw-content-text"), # Csak a Wikipédia érdemi szövegtörzse kell
        },
    )
    
    return loader
    
    
@chain
def split_wiki_docs(docs: list[Document]) -> list[Document]:
    splitter = get_splitter()    
    # Chunking
    return splitter.split_documents(docs)

def get_splitter() -> TextSplitter:
    """"..., letisztítja a szöveget (split & annotate) LCEL pipeline segítségével..."""
    print("[Ingestion] beolvasott dokumentumok darabolása...")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    #text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    return text_splitter
   
    
@chain
def add_metadata_2_chunks(chunks: list[Document]) -> list[Document]:
    """"..., és beindexeli vektoradatbázisba (Qdrantba)."""
    
    downloaded_at = datetime.now(UTC).isoformat()
    #downloaded_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    
    chunk_indices: dict[str, int] = {}
    for chunk in chunks:
        source_id = chunk.metadata.get("source", "ismeretlen")
        chunk_idx = chunk_indices.get(source_id, 0)
        chunk.metadata.update(
            {
                "downloaded_at": downloaded_at,
                "source_id": source_id,
                "chunk_idx": chunk_idx,
            }
        )
        chunk_indices[source_id] = chunk_idx + 1
    return chunks

@chain
def add_metadata_2_doc(idx_doc_pair: tuple[int, Document]) -> Document:
    """"..., és beindexeli gráfadatbázisba (Neo4j-be)."""
    
    doc_idx, doc = idx_doc_pair
    
    chunks = split_wiki_docs.invoke([doc])
    print(f"Létrejött {len(chunks)} db chunk a(z) '{doc.metadata.get('title', 'ismeretlen')}' oldalhoz.")
    
    for chunk_idx, chunk in enumerate(chunks):
        #chunk.metadata["source_id"] = chunk.metadata.get("source", "ismeretlen")
        #chunk.metadata["downloaded_at"] = datetime.now(UTC).isoformat()
        chunk.metadata["chunk_idx"] = chunk_idx
        chunk.metadata["doc_idx"] = doc_idx        
    
    doc.metadata.update(
        {
            # title és source(url) már benne van a metadatában!
            "source_id": doc.metadata.get("source", "ismeretlen"),
            "downloaded_at": datetime.now(UTC).isoformat(),
            #"downloaded_at" = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            "doc_idx": doc_idx,
            "chunks": chunks
        }
    )
    
    return doc
