import faiss
import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, KNOWLEDGE_BASE_PATH, EVENTS_LOG_PATH

embedder=SentenceTransformer(EMBEDDING_MODEL)
def build_knowledge_base(events):
    texts=[e['event'] for e in events]

    print(f"Embedding {len(texts)} events...")
    embeddings=embedder.encode(texts,show_progress_bar=True)
    embeddings=np.array(embeddings).astype('float32')

    dimension=embeddings.shape[1]
    index=faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    os.makedirs(os.path.dirname(KNOWLEDGE_BASE_PATH),exist_ok=True)
    faiss.write_index(index,KNOWLEDGE_BASE_PATH)

    with open(EVENTS_LOG_PATH,'w') as f:
        json.dump(events,f,indent=2)

    print(f"Knowledge base built. {index.ntotal} events indexed.")

def retrieve_context(query,k=5):
    index=faiss.read_index(KNOWLEDGE_BASE_PATH)
    with open(EVENTS_LOG_PATH) as f:
        events=json.load(f)

    query_embedding=embedder.encode([query]).astype('float32')
    distances,indices=index.search(query_embedding,k)

    results=[]
    for i in indices[0]:
        if i < len(events):
            results.append(events[i])
    return results