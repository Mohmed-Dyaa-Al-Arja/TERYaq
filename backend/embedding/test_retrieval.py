from backend.embedding.vector_store import get_client
from backend.embedding.model import embed_texts
from backend.embedding.config import COLLECTION_NAME


def search(query: str, top_k: int = 5):

    client = get_client()

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    query_embedding = embed_texts(
        [query]
    )[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i, (
        document,
        metadata,
        distance,
    ) in enumerate(
        zip(
            documents,
            metadatas,
            distances,
        ),
        start=1,
    ):

        metadata = metadata or {}

        print()
        print(f"RESULT #{i}")
        print("-" * 80)

        print(
            f"Distance: {distance:.4f}"
        )

        print(
            f"Page: {metadata.get('page')}"
        )

        print(
            f"Type: "
            f"{metadata.get('visual_type')}"
        )

        print(
            f"Title: "
            f"{metadata.get('semantic_title')}"
        )

        print(
            f"Caption: "
            f"{metadata.get('source_caption')}"
        )

        print()
        print("TEXT:")
        print("-" * 80)
        print(document[:2000])

        print()
        print("=" * 80)


if __name__ == "__main__":

    queries = [

        # ====================================================
        # Visual reference
        # ====================================================

        "What does Figure 23 show?",

        # ====================================================
        # Visual semantic question
        # ====================================================

        "What are the causes of targets not being met?",

        "What does the breast cancer incidence map show?",

        "What does Figure 22 show about three-year survival?",

        # ====================================================
        # GBCI
        # ====================================================

        "What are the three pillars of the Global Breast Cancer Initiative (GBCI) Implementation Framework?",

        "What is the diagnostic interval, and what is the KPI for Pillar 2?",

        # ====================================================
        # Early detection
        # ====================================================

        "What is the goal of breast-cancer early detection programmes regarding the proportion of women diagnosed with invasive breast cancer at stages I or II?",

        # ====================================================
        # USPSTF
        # ====================================================

        "According to the USPSTF recommendation, which age group should be screened with mammography every 2 years?",

        # ====================================================
        # Diagnostic work-up
        # ====================================================

        "What services are included in the diagnostic interval, and how do clinical evaluation, imaging, tissue sampling, and pathology contribute to reaching a definitive diagnosis?",
    ]

    for query in queries:

        search(
            query,
            top_k=5,
        )