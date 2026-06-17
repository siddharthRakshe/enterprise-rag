def check_context_relevance(results, threshold=0.6):
    """
    Check if retrieved documents are relevant enough.
    Returns True if similarity is above threshold.
    """

    if not results:
        return False

    # results contain (document, score)
    best_score = results[0][1]

    print(f"Guardrail Score: {best_score}")

    return best_score <= threshold