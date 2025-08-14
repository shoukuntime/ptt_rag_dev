from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from env_settings import EnvSettings
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pydantic import SecretStr
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ptt_rag_dev.celery import app
from article.models import Article
import time
import random
from math import ceil

env_settings = EnvSettings()


BATCH_SIZE = 50  # 每批處理 50 筆，避免一次塞爆 API
MAX_RETRIES = 5
BASE_DELAY = 2  # 秒

def retry_with_backoff(func, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "ResourceExhausted" in str(e) or "429" in str(e):
                delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
                print(f"[Quota hit] Retry {attempt+1}/{MAX_RETRIES} after {delay:.2f}s...")
                time.sleep(delay)
            else:
                raise
    raise RuntimeError("Max retries reached for embedding request")

@app.task()
def store_data_in_pinecone(article_id_list: list):
    vector_store = PineconeVectorStore(
        index=Pinecone(api_key=env_settings.PINECONE_API_KEY)
        .Index(env_settings.PINECONE_INDEX_NAME),
        embedding=GoogleGenerativeAIEmbeddings(
            model=env_settings.GOOGLE_EMBEDDINGS_MODEL,
            google_api_key=SecretStr(env_settings.GOOGLE_API_KEY),
        ),
    )

    documents = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
    )

    for article in Article.objects.filter(id__in=article_id_list).all():
        chunks = text_splitter.split_text(article.content)
        for i, chunk in enumerate(chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "article_id": article.id,
                        "board": article.board,
                        "title": article.title,
                        "author": article.author,
                        "post_time": str(article.post_time),
                        "url": article.url,
                        "chunk_index": i,
                    },
                )
            )

    # 分批送入，避免一次塞太多
    total_batches = ceil(len(documents) / BATCH_SIZE)
    for i in range(total_batches):
        batch_docs = documents[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        retry_with_backoff(vector_store.add_documents, documents=batch_docs)
        print(f"[Batch {i+1}/{total_batches}] Uploaded {len(batch_docs)} docs")
