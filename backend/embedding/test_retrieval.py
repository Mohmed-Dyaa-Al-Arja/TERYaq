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
            "distances"
        ]
    )

    print("=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i, (
        document,
        metadata,
        distance
    ) in enumerate(
        zip(
            documents,
            metadatas,
            distances
        ),
        start=1
    ):

        print()
        print(f"RESULT #{i}")
        print("-" * 70)

        print(
            f"Distance: {distance:.4f}"
        )

        print(
            f"Page: {metadata.get('page')}"
        )

        print(
            f"Type: {metadata.get('visual_type')}"
        )

        print(
            f"Title: "
            f"{metadata.get('semantic_title')}"
        )

        print()

        print(
            document[:1000]
        )


if __name__ == "__main__":

    queries = [
        "What does Figure 23 show?",
        "What are the causes of targets not being met?",
        "What does the breast cancer incidence map show?",
        "What does Figure 22 show about three-year survival?"
    ]

    for query in queries:

        search(
            query,
            top_k=3
        )