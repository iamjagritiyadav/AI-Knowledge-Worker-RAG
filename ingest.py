import warnings
warnings.filterwarnings("ignore") 

from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from chromadb import PersistentClient
from tqdm import tqdm
import litellm
from litellm import completion, embedding
from multiprocessing import Pool
from tenacity import retry, wait_exponential, stop_after_attempt
import os

load_dotenv(override=True)

# --- CONFIGURATION (TIER 1 TUNED) ---
MODEL = "gemini/gemini-2.0-flash" 
EMBEDDING_MODEL = "gemini/text-embedding-004" 

# Path Setup
DB_NAME = str(Path(__file__).parent / "preprocessed_db")
KNOWLEDGE_BASE_PATH = Path(__file__).parent / "knowledge-base"
collection_name = "docs"

# Tuning for Paid Tier (2,000 RPM / 4M TPM)
AVERAGE_CHUNK_SIZE = 400  # Increased chunk size for better context
WORKERS = 8               # Parallel processing power
EMBEDDING_BATCH_SIZE = 50 # Number of chunks to embed per API call

# Faster retries because we don't need to wait for free tier cooldowns
wait_policy = wait_exponential(multiplier=0.5, min=1, max=10)

class Result(BaseModel):
    page_content: str
    metadata: dict

class Chunk(BaseModel):
    headline: str = Field(description="A brief heading for this chunk")
    summary: str = Field(description="A few sentences summarizing the content")
    original_text: str = Field(description="The original text of this chunk exactly as is")

    def as_result(self, document):
        metadata = {"source": document["source"], "type": document["type"]}
        return Result(
            page_content=f"{self.headline}\n\n{self.summary}\n\n{self.original_text}",
            metadata=metadata,
        )

class Chunks(BaseModel):
    chunks: list[Chunk]

def fetch_documents():
    documents = []
    if not KNOWLEDGE_BASE_PATH.exists():
        print(f"❌ Error: {KNOWLEDGE_BASE_PATH} not found.")
        return []
    
    # Updated to look for .md files in the folder structure shown in your screenshot
    # Recurse through all subfolders
    for file in KNOWLEDGE_BASE_PATH.rglob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            # Use parent folder name as 'type' (e.g. 'policies', 'claims')
            documents.append({"type": file.parent.name, "source": file.name, "text": f.read()})

    print(f"✅ Loaded {len(documents)} documents")
    return documents

def make_prompt(document):
    # Dynamic chunk estimation
    how_many = (len(document["text"]) // AVERAGE_CHUNK_SIZE) + 1
    return f"""
    Split the following document into {how_many} overlapping chunks for a KnowledgeBase.
    Company: Insurellm
    Type: {document["type"]}
    Source: {document["source"]}

    Document Content:
    {document["text"][:30000]} 
    """ # Cap text at 30k chars to prevent context window overflow

@retry(wait=wait_policy, stop=stop_after_attempt(5))
def process_document(document):
    messages = [{"role": "user", "content": make_prompt(document)}]
    
    response = completion(
        model=MODEL, 
        messages=messages, 
        response_format=Chunks
    )
    
    reply = response.choices[0].message.content
    doc_as_chunks = Chunks.model_validate_json(reply).chunks
    return [chunk.as_result(document) for chunk in doc_as_chunks]

def create_chunks(documents):
    chunks = []
    print(f"🚀 Processing {len(documents)} docs with {WORKERS} parallel workers...")
    
    # Parallel processing loop
    with Pool(processes=WORKERS) as pool:
        for result in tqdm(pool.imap_unordered(process_document, documents), total=len(documents)):
            chunks.extend(result)
    return chunks

def create_embeddings(chunks):
    chroma = PersistentClient(path=DB_NAME)
    try:
        chroma.delete_collection(collection_name)
        print("🗑️  Deleted old collection.")
    except:
        pass

    collection = chroma.get_or_create_collection(collection_name)
    texts = [chunk.page_content for chunk in chunks]
    metas = [chunk.metadata for chunk in chunks]
    ids = [str(i) for i in range(len(chunks))]
    
    print(f"🧠 Generating embeddings for {len(texts)} chunks (Batch size: {EMBEDDING_BATCH_SIZE})...")
    
    # BATCHING LOOP (Critical for high volume)
    for i in tqdm(range(0, len(texts), EMBEDDING_BATCH_SIZE)):
        batch_texts = texts[i : i + EMBEDDING_BATCH_SIZE]
        batch_metas = metas[i : i + EMBEDDING_BATCH_SIZE]
        batch_ids = ids[i : i + EMBEDDING_BATCH_SIZE]
        
        try:
            response = embedding(
                model=EMBEDDING_MODEL,
                input=batch_texts
            )
            
            vectors = [item['embedding'] for item in response['data']]
            collection.add(ids=batch_ids, embeddings=vectors, documents=batch_texts, metadatas=batch_metas)
        except Exception as e:
            print(f"⚠️ Batch failed: {e}")

    print(f"✅ Vectorstore created with {collection.count()} items.")

if __name__ == "__main__":
    docs = fetch_documents()
    if docs:
        chunks = create_chunks(docs)
        if chunks:
            create_embeddings(chunks)
            print("🎉 Ingestion complete! Run 'python test_rag_terminal.py' to test.")
        else:
            print("⚠️ No chunks were generated. Check your input documents.")