from datetime import UTC, datetime

from langchain_classic.document_loaders import WebBaseLoader
from langchain_classic.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def ingest_wikipedia_links(urls: list[str]) -> list[Document]:
        """Letölti a HTML oldalakat, letisztítja a szöveget és beindexeli a Qdrantba."""
        print(f"[Ingestion] {len(urls)} Wikipédia link beolvasása...")
        
        # HTML Loader (BeautifulSoup)
        loader = WebBaseLoader(
            web_paths=urls,
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(id="mw-content-text") # Csak a Wikipédia érdemi szövegtörzse kell
            )
        )
        docs = loader.load()
        downloaded_at = datetime.now(UTC).isoformat()
        
        # Chunking
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)

        chunk_indices: dict[str, int] = {}
        for chunk in chunks:
            source_id = chunk.metadata.get("source", "unknown")
            chunk_idx = chunk_indices.get(source_id, 0)
            chunk.metadata.update(
                {
                    "downloaded_at": downloaded_at,
                    "source_id": source_id,
                    "chunk_idx": chunk_idx,
                }
            )
            chunk_indices[source_id] = chunk_idx + 1
        
        print(f"[Ingestion] A szövegek {len(chunks)} darabra (chunk) lettek felvágva.")
        
        return chunks
