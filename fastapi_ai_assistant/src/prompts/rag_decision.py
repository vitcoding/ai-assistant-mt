def get_prompt_decision(user_input: str) -> str:
    """Gets RAG decision prompt."""

    prompt_decision = f"""
You are an assistant that can either search for information (RAG) or respond independently.
Decide whether document retrieval is needed to answer the user's latest query.

Examples where RAG is NOT needed:
- Questions about today's weather.
- Simple calculations (2+2=?).
- General knowledge (capital of France).

Examples where RAG is needed:
- Questions about retrieved context.
- Questions about films.
- Questions about specific data (documents, articles, personal data).
- Requests like "Find me information about X".

User query:
{user_input}

Your response must be in JSON format:
{{"rag_decision": true/false}}
"""
    return prompt_decision
