from fastapi import FastAPI, Request, Response, Query
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import google.generativeai as genai

API_KEY = "AIzaSyBoLSKrZTfRs6V1cEkkFS0ttlossjGvXlA"
genai.configure(api_key=API_KEY)
model_name = "models/embedding-001"
model = genai.GenerativeModel('models/gemini-2.0-flash-exp')

df = pd.read_parquet('./data/qa_with_embeddings.parquet')

app = FastAPI()


class Question(BaseModel):
    question: str


def search_similar_embeddings(query_embedding: list | np.ndarray, df: pd.DataFrame, top_k: int = 3, threshold: float = 0.6) -> pd.DataFrame:

    query_vector = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    embedding_matrix = np.array(df['embedding'].tolist(), dtype=np.float32)

    similarities = cosine_similarity(query_vector, embedding_matrix)[0]

    # Gán similarity vào DataFrame
    df_with_similarity = df.copy()
    df_with_similarity['similarity'] = similarities

    # Lọc theo ngưỡng và sắp xếp
    result = (
        df_with_similarity[df_with_similarity['similarity'] >= threshold]
        .sort_values(by='similarity', ascending=False)
        .head(top_k)
    )

    return result[['question', 'answers', 'similarity']]


@app.post("/ask")
async def receive_question(data: Question):
    question = data.question

    result = genai.embed_content(
        model=model_name,
        content=question,
        task_type="SEMANTIC_SIMILARITY"
    )
    question_embedding = result['embedding']

    retrieval_docs = search_similar_embeddings(
        query_embedding=question_embedding, df=df, top_k=5, threshold=0.85)

    document = "\n\n".join(
        f"Câu hỏi: {row['question']}\nTrả lời: {row['answers']}"
        for _, row in retrieval_docs.iterrows()
    )

    prompt = f"""
      Bạn là một trợ lý ảo giúp tư vấn tuyển sinh cho trường Đại học Bách Khoa Đà Nẵng
      Hãy dựa trên câu hỏi người dùng và tài liệu tham khảo để đưa ra câu trả lời 
      Nếu không có thông tin chính xác đúng với câu hỏi, hãy trả lời là không biết, không trả lời lan man
      <question>{question}</question>
      <document>{document}</document>
    """

    response = model.generate_content(prompt)

    return {"llm_answers": response.text}
