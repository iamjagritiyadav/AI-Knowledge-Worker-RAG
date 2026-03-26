
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import warnings
warnings.filterwarnings("ignore") 

from pathlib import Path
from dotenv import load_dotenv
from chromadb import PersistentClient
import litellm
from litellm import completion, embedding
from pydantic import BaseModel, Field
from tenacity import retry, wait_exponential

load_dotenv(override=True)

# --- CONFIGURATION ---
MODEL = "gemini/gemini-2.0-flash" 
EMBEDDING_MODEL = "gemini/text-embedding-004"

# FIX: Ensure this matches ingest.py exactly (Current folder, not parent)
DB_NAME = str(Path(__file__).parent / "preprocessed_db")
collection_name = "docs"
wait = wait_exponential(multiplier=1, min=10, max=240)

# Initialize Chroma
chroma = PersistentClient(path=DB_NAME)
collection = chroma.get_or_create_collection(collection_name)

RETRIEVAL_K = 20
FINAL_K = 10

SYSTEM_PROMPT = """
You are a knowledgeable, friendly assistant representing the company Insurellm.
Use the following context to answer the user's question accurately.
If you don't know the answer based on the context, say so.

Context:
{context}
"""

class Result(BaseModel):
    page_content: str
    metadata: dict

class RankOrder(BaseModel):
    order: list[int] = Field(
        description="The order of relevance of chunks, from most relevant to least relevant, by chunk id number"
    )

@retry(wait=wait)
def rerank(question, chunks):
    system_prompt = "You are a document re-ranker. Rank chunks by relevance to the question. Reply with ranked IDs only."
    
    user_prompt = f"Question: {question}\n\nChunks to rank:\n"
    for index, chunk in enumerate(chunks):
        user_prompt += f"# CHUNK ID {index + 1}: {chunk.page_content[:200]}...\n\n"
    
    try:
        response = completion(
            model=MODEL, 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=RankOrder
        )
        order = RankOrder.model_validate_json(response.choices[0].message.content).order
        return [chunks[i - 1] for i in order if i <= len(chunks)]
    except Exception as e:
        # If reranking fails, just return the top chunks as-is
        return chunks[:5]

@retry(wait=wait)
def rewrite_query(question, history=[]):
    message = f"Conversation History: {history}\nUser Question: {question}\n\nRewrite this into a single, optimized search query for a technical knowledge base. Output ONLY the query."
    
    try:
        response = completion(
            model=MODEL, 
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    except:
        return question

def fetch_context_unranked(question):
    # Use LiteLLM to get embeddings for the search query
    resp = embedding(model=EMBEDDING_MODEL, input=[question])
    query_vector = resp['data'][0]['embedding']
    
    results = collection.query(query_embeddings=[query_vector], n_results=RETRIEVAL_K)
    
    chunks = []
    if results["documents"]:
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            chunks.append(Result(page_content=doc, metadata=meta))
    return chunks

def fetch_context(original_question):
    # 1. Fetch chunks for the raw question
    chunks1 = fetch_context_unranked(original_question)
    
    # 2. Rerank them
    if not chunks1:
        return []
        
    reranked = rerank(original_question, chunks1)
    return reranked[:FINAL_K]

def answer_question(question: str, history: list[dict] = []):
    # --- 1. THE CHIT-CHAT ROUTER (NEW) ---
    # Detects if input is just a greeting to skip the database search
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "thanks", "thank you", "sup"]
    
    # Simple check: if the user's input is just a greeting word
    if question.strip().lower() in greetings:
        messages = [
            {"role": "system", "content": "You are a helpful, friendly assistant for Insurellm. Reply to the user's greeting warmly and ask how you can help with insurance policies."},
            *history,
            {"role": "user", "content": question}
        ]
        response = completion(model=MODEL, messages=messages)
        # Return empty list [] for sources because we didn't search the DB
        return response.choices[0].message.content, [] 

    # --- 2. THE REAL RAG LOGIC (EXISTING) ---
    chunks = fetch_context(question)
    
    if not chunks:
        # Fallback if DB search fails
        return "I'm sorry, I couldn't find specific details in the knowledge base. Could you rephrase your question about Insurellm?", []

    context_text = "\n\n".join(
        f"Source: {c.metadata['source']}\nContent: {c.page_content}" for c in chunks
    )
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context_text)},
        *history,
        {"role": "user", "content": question}
    ]
    
    response = completion(model=MODEL, messages=messages)
    return response.choices[0].message.content, chunks