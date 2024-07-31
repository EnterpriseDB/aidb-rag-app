from db import get_connection

template = """<s>[INST]
You are a friendly documentation search bot.
Use following piece of context to answer the question.
If the context is empty, try your best to answer without it.
Never mention the context.
Try to keep your answers concise unless asked to provide details.

Context: {context}
Question: {question}
[/INST]</s>
Answer:
"""

def get_retrieval_condition(query_embedding, topk):
    # Convert query embedding to a string format for SQL query
    query_embedding_str = ",".join(map(str, query_embedding))

    # # SQL condition for cosine similarity
    # condition = f"(embeddings <=> '{query_embedding_str}') < {threshold} ORDER BY embeddings <=> '{query_embedding_str}'"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
            f"""SELECT data from aidb.retrieve('{query_embedding_str}', {topk}, 'documents_embeddings');"""
        )
    results = cursor.fetchall()
    rag_query = ' '.join([row[0] for row in results])
    return rag_query


def rag_query(tokenizer, model, device, query, topk):
    # Retrieve relevant embeddings from the database
    rag_query = get_retrieval_condition(query, topk)
    query_template = template.format(context=rag_query, question=query)

    input_ids = tokenizer.encode(query_template, return_tensors="pt")

    # Generate the response
    model.generation_config.pad_token_id = tokenizer.pad_token_id
    generated_response = model.generate(input_ids.to(device), max_new_tokens=100)
    return tokenizer.decode(generated_response[0][input_ids.shape[-1]:], skip_special_tokens=True)
