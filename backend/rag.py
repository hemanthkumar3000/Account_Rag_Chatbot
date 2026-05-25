from typing import List


def build_rag_prompt(
    context_chunks: List[str],
    history: List[str],
    question: str,
) -> str:
    """
    Build a prompt that tells the LLM to answer only from the given context.
    """
    if not context_chunks:
        context_text = "No relevant context available."
    else:
        context_text = "\n\n".join(context_chunks)

    history_text = "\n".join(history)

    prompt = f"""You are a helpful assistant.

Use only the provided context to answer.

Context:
{context_text}

History:
{history_text}

Question:
{question}

Answer:"""
    return prompt