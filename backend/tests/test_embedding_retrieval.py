from __future__ import annotations

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

COLLECTION_NAME = "teryaq_breast_cancer_test"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

TOP_K = 5


# ============================================================
# Load PDFs
# ============================================================

def load_documents():
    documents = []

    pdf_files = sorted(
        DATA_DIR.glob("*.pdf")
    )

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in: {DATA_DIR}"
        )

    print()
    print("=" * 80)
    print("PDF FILES")
    print("=" * 80)

    for pdf_path in pdf_files:

        print(
            f"Loading: {pdf_path.name}"
        )

        loader = PyPDFLoader(
            str(pdf_path)
        )

        docs = loader.load()

        for doc in docs:

            doc.metadata[
                "source_file"
            ] = pdf_path.name

        documents.extend(docs)

    print()
    print(
        f"Total pages loaded: "
        f"{len(documents)}"
    )

    return documents


# ============================================================
# Chunking
# ============================================================

def create_chunks(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(
        documents
    )

    print(
        f"Total chunks created: "
        f"{len(chunks)}"
    )

    return chunks


# ============================================================
# Embedding
# ============================================================

def create_embedding_model():

    print()
    print("=" * 80)
    print("EMBEDDING MODEL")
    print("=" * 80)

    print(
        f"Loading embedding model: "
        f"{EMBEDDING_MODEL}"
    )

    embedding_model = FastEmbedEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    print("Embedding model loaded.")

    return embedding_model


# ============================================================
# Create Chroma
# ============================================================

def create_vectorstore(chunks):

    embedding_model = (
        create_embedding_model()
    )

    print()
    print("=" * 80)
    print("CHROMA")
    print("=" * 80)

    print(
        f"Collection: "
        f"{COLLECTION_NAME}"
    )

    print(
        f"Directory: "
        f"{CHROMA_DIR}"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        collection_metadata={
            "hnsw:space": "cosine"
        },
        persist_directory=str(
            CHROMA_DIR
        ),
    )

    print(
        "Chroma vectorstore created."
    )

    return vectorstore


# ============================================================
# Print Metadata
# ============================================================

def print_result_metadata(
    doc,
    score,
):

    metadata = (
        doc.metadata
        or {}
    )

    print()
    print("-" * 80)

    print(
        f"Distance : "
        f"{float(score):.4f}"
    )

    print(
        f"Source   : "
        f"{metadata.get('source_file', 'N/A')}"
    )

    print(
        f"Page     : "
        f"{metadata.get('page', 'N/A')}"
    )

    print(
        f"Type     : "
        f"{metadata.get('content_type', 'N/A')}"
    )

    print(
        f"Title    : "
        f"{metadata.get('semantic_title', 'N/A')}"
    )

    print(
        f"Caption  : "
        f"{metadata.get('source_caption', 'N/A')}"
    )

    print(
        f"Section  : "
        f"{metadata.get('section', 'N/A')}"
    )

    print(
        f"Chunk ID : "
        f"{metadata.get('chunk_id', 'N/A')}"
    )

    print()
    print("CONTENT:")

    content = (
        doc.page_content
        or ""
    ).strip()

    print(
        content[:2500]
    )


# ============================================================
# Retrieval Test
# ============================================================

def test_retrieval(
    vectorstore,
    question: str,
):

    print()
    print("=" * 80)
    print("QUERY")
    print("=" * 80)

    print(question)

    results = (
        vectorstore
        .similarity_search_with_score(
            question,
            k=TOP_K,
        )
    )

    if not results:

        print()
        print(
            "NO RESULTS FOUND."
        )

        return

    print()
    print(
        f"Retrieved {len(results)} "
        f"results."
    )

    for index, (
        doc,
        score,
    ) in enumerate(
        results,
        start=1,
    ):

        print()
        print(
            "=" * 80
        )

        print(
            f"RESULT #{index}"
        )

        print(
            "=" * 80
        )

        print_result_metadata(
            doc,
            score,
        )


# ============================================================
# Test Questions
# ============================================================

TEST_QUESTIONS = [

    # --------------------------------------------------------
    # General
    # --------------------------------------------------------

    (
        "What are the recommendations "
        "for breast cancer screening?"
    ),

    (
        "What is early diagnosis "
        "of breast cancer?"
    ),

    (
        "What are the treatment options "
        "for breast cancer?"
    ),

    # --------------------------------------------------------
    # USPSTF
    # --------------------------------------------------------

    (
        "According to the USPSTF recommendation, "
        "which age group should be screened "
        "with mammography every 2 years?"
    ),

    # --------------------------------------------------------
    # Early detection
    # --------------------------------------------------------

    (
        "What is the goal of breast-cancer "
        "early detection programmes regarding "
        "the proportion of women diagnosed "
        "at stages I or II?"
    ),

    # --------------------------------------------------------
    # Diagnostic interval
    # --------------------------------------------------------

    (
        "What is the diagnostic interval, "
        "and what is the KPI for Pillar 2?"
    ),

    (
        "What services are included in the "
        "diagnostic interval?"
    ),

    # --------------------------------------------------------
    # Staging
    # --------------------------------------------------------

    (
        "What is the role of staging after "
        "a breast cancer diagnosis?"
    ),

    # --------------------------------------------------------
    # Treatment
    # --------------------------------------------------------

    (
        "What does the GBCI Framework state "
        "about multidisciplinary treatment?"
    ),

    # --------------------------------------------------------
    # Visual
    # --------------------------------------------------------

    (
        "What does Figure 23 show?"
    ),
]


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 80)
    print(
        "TERYaq - EMBEDDING + "
        "RETRIEVAL TEST"
    )
    print("=" * 80)

    # --------------------------------------------------------
    # 1. Load PDFs
    # --------------------------------------------------------

    documents = (
        load_documents()
    )

    # --------------------------------------------------------
    # 2. Create chunks
    # --------------------------------------------------------

    chunks = (
        create_chunks(
            documents
        )
    )

    # --------------------------------------------------------
    # 3. Create vectorstore
    # --------------------------------------------------------

    vectorstore = (
        create_vectorstore(
            chunks
        )
    )

    # --------------------------------------------------------
    # 4. Run retrieval tests
    # --------------------------------------------------------

    for question in TEST_QUESTIONS:

        test_retrieval(
            vectorstore=vectorstore,
            question=question,
        )

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print(
        "RETRIEVAL TEST FINISHED"
    )
    print("=" * 80)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()