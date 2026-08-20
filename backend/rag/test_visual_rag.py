from backend.rag.retriever import retrieve
from backend.rag.reranker import rerank_results
from backend.rag.evidence_gate import validate_evidence


def test_query(query: str):

    print()
    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    # --------------------------------------------------------
    # Retrieval
    # --------------------------------------------------------

    results = retrieve(
        query,
        top_k=5,
    )

    # --------------------------------------------------------
    # Reranking
    # --------------------------------------------------------

    ranked = rerank_results(
        query,
        results,
    )

    # --------------------------------------------------------
    # Evidence Gate
    # --------------------------------------------------------

    gate = validate_evidence(
        ranked,
        min_score=0.55,
    )

    print()
    print(
        f"Evidence sufficient: "
        f"{gate['sufficient']}"
    )

    print(
        f"Reason: "
        f"{gate['reason']}"
    )

    print()
    print("RERANKED RESULTS")
    print("-" * 80)

    for index, result in enumerate(
        ranked[:5],
        start=1,
    ):

        metadata = result["metadata"]

        print()
        print(f"#{index}")

        print(
            f"Score: "
            f"{result['rerank_score']:.4f}"
        )

        print(
            f"Distance: "
            f"{result['distance']:.4f}"
        )

        print(
            f"Page: "
            f"{metadata.get('page')}"
        )

        print(
            f"Type: "
            f"{metadata.get('visual_type')}"
        )

        print(
            f"Title: "
            f"{metadata.get('semantic_title')}"
        )


if __name__ == "__main__":

    queries = [
    "What does Figure 23 show?",
    "What are the causes of targets not being met?",
    "What does Figure 22 show about three-year survival?",
    "What does the breast cancer incidence map show?",
    "What are the three GBCI pillars?",
    "What is the purpose of the fishbone diagram?",
    ]

    for query in queries:
        test_query(query)