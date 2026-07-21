import ollama

def generate_response(user_input, result, history = None, model_name="llama3.2"):

    docs = result.get('documents', []) if isinstance(result, dict) else []
    metas = result.get('metadatas', []) if isinstance(result, dict) else []

    system_prompt = (
        "You are a helpful assistant. Use the provided context to answer the user's question."
        " If the context does not contain enough information, say you don't know.\n\n"
        "Context documents:\n" + str(docs) + "\n\nMetadata:\n" + str(metas)
    )

    messages = [
        {"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_input})

    response = ollama.chat(
        model=model_name,
        messages=messages
    )

    try:
        return response['message']['content']
    except Exception:
        return str(response)