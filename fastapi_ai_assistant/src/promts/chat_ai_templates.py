from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Your name is 'ИИ Ассистент'. "
            "You are an assistant for question-answering tasks. "
            "\nTry to use a maximum of three sentences to keep "
            "the answer concise if possible. If you don't know "
            "the answer, say that you don't know. \n"
            "You must speak only {language}. "
            "{docs_content}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

prompt_template_1 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Your name is 'ИИ Ассистент'. "
            "You are an assistant for question-answering tasks. \n"
            "Use the retrieved documents of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise. "
            "You must speak only {language}."
            "\n\n\n"
            "Retrieved context:\n\n{docs_content}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

prompt_template_0 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant named 'AI Chat'. Answer all questions "
            "to the best of your ability in {language}."
            "{docs_content}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
