"""Load all medical PDFs from data/pdf."""

from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


DEFAULT_PDF_DIR = Path("data/pdf")


def discover_pdfs(pdf_dir: str | Path = DEFAULT_PDF_DIR) -> list[Path]:
    """Return all PDFs in the knowledge-base directory."""
    directory = Path(pdf_dir)

    if not directory.exists():
        raise FileNotFoundError(
            f"PDF directory does not exist: {directory}"
        )

    return sorted(
        path for path in directory.glob("*.pdf")
        if path.is_file()
    )


def load_pdf(
    pdf_path: str | Path,
) -> list[Document]:
    """Load one PDF into LangChain documents."""
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(path)

    loader = PyPDFLoader(str(path))
    pages = loader.load()

    for page in pages:
        page.metadata["source_file"] = path.name
        page.metadata["source_path"] = str(path)

    return pages


def load_all_pdfs(
    pdf_dir: str | Path = DEFAULT_PDF_DIR,
) -> list[Document]:
    """Load every PDF currently present in data/pdf."""
    documents: list[Document] = []

    for pdf_path in discover_pdfs(pdf_dir):
        documents.extend(load_pdf(pdf_path))

    if not documents:
        raise RuntimeError(
            f"No PDF documents found in {pdf_dir}."
        )

    return documents
