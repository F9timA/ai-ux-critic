from google import genai
from dotenv import load_dotenv
import chromadb
import os
import glob

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Chroma will persist to a local folder called chroma_db
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="ux_guidelines")


def chunk_text(text, chunk_size=500):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs


def build_knowledge_base():
    files = glob.glob("knowledge/*.txt")
    doc_id = 0

    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        for chunk in chunks:
            embedding_response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=chunk
            )
            embedding = embedding_response.embeddings[0].values

            collection.add(
                ids=[f"chunk_{doc_id}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": filepath}]
            )
            doc_id += 1
            print(f"Embedded chunk {doc_id} from {filepath}")

    print(f"\nDone. {doc_id} chunks stored in Chroma.")


if __name__ == "__main__":
    build_knowledge_base()