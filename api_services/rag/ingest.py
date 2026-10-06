import hashlib
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.retriever import COLLECTION_NAME, vector_store


DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_and_split_pdf(file_path, category):
    # Load the PDF
    loader = PyPDFLoader(str(file_path))
    documents = loader.load()

    # Split the PDF text into smaller chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)

    # Add metadata to every chunk
    for chunk in chunks:
        chunk.metadata["category"] = category
        chunk.metadata["source"] = Path(file_path).name
        chunk.metadata["page"] = int(chunk.metadata.get("page", 0))

    return chunks

def ingest_knowledge():
    # Process both knowledge PDFs
    for category in ("diet", "workout"):

        pdf_path = DATA_DIR / f"{category}.pdf"

        # Load and split PDF
        chunks = load_and_split_pdf(pdf_path, category)

        # Create a unique ID for every chunk
        ids = [
            hashlib.sha256(
                (
                    f"{category}:"
                    f"{chunk.metadata['source']}:"
                    f"{chunk.metadata['page']}:"
                    f"{chunk.page_content}"
                ).encode("utf-8")
            ).hexdigest()
            for chunk in chunks
        ]

        # Store chunks and their embeddings in the vector store
        vector_store.add_documents(
            chunks,
            ids=ids,
        )

        print(
            f"Indexed {len(chunks)} chunks "
            f"from {pdf_path.name} "
            f"in {COLLECTION_NAME}."
        )


# if __name__ == "__main__":
#     ingest_knowledge()