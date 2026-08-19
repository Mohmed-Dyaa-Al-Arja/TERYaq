from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_chroma import Chroma


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "pdf"
CHROMA_DIR = BASE_DIR / "processed" / "chroma"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5


# ============================================================
# Load PDFs
# ============================================================

def load_documents():
    documents = []

    pdf_files = sorted(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in: {DATA_DIR}"
        )

    print("\nPDFs found:")

    for pdf_path in pdf_files:
        print(f"  - {pdf_path.name}")

        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()

        for doc in docs:
            doc.metadata["source_file"] = pdf_path.name

        documents.extend(docs)

    print(f"\nTotal pages loaded: {len(documents)}")

    return documents


# ============================================================
# Chunking
# ============================================================

def create_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(documents)

    print(f"Total chunks: {len(chunks)}")

    return chunks


# ============================================================
# Embedding + Chroma
# ============================================================

def create_vectorstore(chunks):

    print("\nLoading embedding model:")
    print(f"  {EMBEDDING_MODEL}")

    embedding_model = FastEmbedEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    print("Embedding model loaded.")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name="teryaq_breast_cancer_test",
        collection_metadata={
            "hnsw:space": "cosine"
        },
        persist_directory=str(CHROMA_DIR),
    )

    print("Chroma vectorstore created.")

    return vectorstore


# ============================================================
# Retrieval Test
# ============================================================

def test_retrieval(vectorstore, question):

    print("\n" + "=" * 80)
    print(f"QUESTION: {question}")
    print("=" * 80)

    results = vectorstore.similarity_search_with_score(
        question,
        k=TOP_K,
    )

    for i, (doc, score) in enumerate(results, start=1):

        print("\n" + "-" * 80)
        print(f"RESULT #{i}")
        print(f"Score: {score}")
        print(f"Source: {doc.metadata.get('source_file')}")
        print(f"Page: {doc.metadata.get('page')}")

        content = doc.page_content.strip()

        print("\nContent:")
        print(content[:1000])


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 80)
    print("TERYaq - EMBEDDING + RETRIEVAL TEST")
    print("=" * 80)

    documents = load_documents()

    chunks = create_chunks(documents)

    vectorstore = create_vectorstore(chunks)

    test_questions = [
        "What are the recommendations for breast cancer screening?",
        "What is early diagnosis of breast cancer?",
        "What are the treatment options for breast cancer?",
    ]

    for question in test_questions:
        test_retrieval(vectorstore, question)

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()