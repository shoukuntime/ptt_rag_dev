from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from env_settings import EnvSettings
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pydantic import SecretStr
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ptt_rag_dev.celery import app
from article.models import Article

env_settings = EnvSettings()


@app.task()
def store_data_in_pinecone(article_id_list: list):
    vector_store = PineconeVectorStore(
        index=Pinecone(
            api_key=env_settings.PINECONE_API_KEY
        ).Index(env_settings.PINECONE_INDEX_NAME),
        embedding=GoogleGenerativeAIEmbeddings(model=env_settings.GOOGLE_EMBEDDINGS_MODEL,
                                               google_api_key=SecretStr(env_settings.GOOGLE_API_KEY)),
    )
    documents = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n---\n", "\n--\n", "\n", "。", "！", "？", "，", " ", ""]
    )
    for article in Article.objects.filter(id__in=article_id_list).all():
        chunks = text_splitter.split_text(article.content)
        for i, chunk in enumerate(chunks):
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "article_id": article.id,
                    "board": article.board,
                    "title": article.title,
                    "author": article.author,
                    "post_time": str(article.post_time),
                    "url": article.url,
                    "chunk_index": i
                }
            ))
    vector_store.add_documents(documents=documents)
