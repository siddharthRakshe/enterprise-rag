def check_context_relevance(results, threshold=2.0):
    """
    Check if retrieved documents are relevant enough.
    Lower score = more relevant in Chroma distance search.
    """

    if not results:
        return False

    best_score = results[0][1]

    print(f"Guardrail Score: {best_score}")

    return best_score <= threshold