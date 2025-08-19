import traceback
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from pydantic import SecretStr
import asyncio
from article.models import Article
from log_app.models import Log
from env_settings import EnvSettings

env_settings = EnvSettings()


def run_rag_query(question, top_k):
    try:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
        vector_store = PineconeVectorStore(
            index=Pinecone(
                api_key=env_settings.PINECONE_API_KEY
            ).Index(env_settings.PINECONE_INDEX_NAME),
            embedding=GoogleGenerativeAIEmbeddings(
                model=env_settings.GOOGLE_EMBEDDINGS_MODEL,
                google_api_key=SecretStr(env_settings.GOOGLE_API_KEY)
            )
        )
        top_k_results = vector_store.similarity_search_with_score(question, k=top_k)
    except Exception as e:
        Log.objects.create(level='ERROR', category='user-search', message=f'查詢Pinecone embeddings內容發生錯誤: {e}',
                           traceback=traceback.format_exc())
        return {"error": f"查詢Pinecone embeddings內容發生錯誤: {str(e)}"}
    try:
        match_ids = [match[0].metadata['article_id'] for match in top_k_results]
        related_articles = Article.objects.filter(id__in=match_ids)
        merge_text = "\n".join(
            [f"Title:{a.title} - Content:{a.content}" for a in related_articles])
        if len(merge_text) > 128000:
            Log.objects.create(level='ERROR', category='user-search', message='回傳文章總字數過長，請嘗試減少top_k')
            return {"error": "回傳文章總字數過長，請嘗試減少top_k"}
    except (KeyError, TypeError) as e:
        Log.objects.create(level='ERROR', category='user-search', message=f'從資料庫找出文章內容發生錯誤: {e}',
                           traceback=traceback.format_exc())
        return {"error": f"從資料庫找出文章內容發生錯誤: {str(e)}"}
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=env_settings.GOOGLE_API_KEY,
        )
        ptt_template = PromptTemplate(
            input_variables=["merge_text", "question"],
            template="""
            根據以下PTT的文章內容以純文字回答問題：
            ---
            {merge_text}
            ---
            問題：{question}
            """
        )
        chain = ptt_template | model
        answer = chain.invoke({"merge_text": merge_text, "question": question})
        return {
            "question": question,
            "answer": answer,
            "related_articles": [
                {"id": a.id, "title": a.title, "content": a.content} for a in related_articles
            ]
        }
    except Exception as e:
        Log.objects.create(level='ERROR', category='user-search', message=f'LLM生成回答發生錯誤: {e}',
                           traceback=traceback.format_exc())
        return {"error": f"LLM生成回答發生錯誤: {str(e)}"}

