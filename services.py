from models import *
from processor import pre_process_question, find_similarity_vectors


def search_major_information(major_name: str, year: int, admission_method: str):
    result = []
    query_string = f"SELECT * FROM data WHERE major_name LIKE '%{major_name}%' AND year = {year}"
    data = query_data(query_string=query_string)
    for row in data:
        result.append(
            {
                "major_name": row[1],
                "major_code": row[2],
                "score": row[3],
                "year": row[9],
            }

        )
    return result


def find_major_by_id(major_id: str):
    query_str = f"SELECT * FROM data WHERE major_code = {major_id}"
    data = query_data(query_str)
    print(data)


def search_for_admission_information(question: str):
    answers = []

    embedding_question = pre_process_question(question_text=question)
    vector_data = find_similarity_vectors(embedding_vector=embedding_question)

    for vector in vector_data:
        answers.append(
            {
                "answer": vector['answers']
            }
        )
    if len(answers) == 0:
        return {
            "answer": "Hiện tại chưa có thông tin để trả lời cho câu hỏi của bạn"
        }
    return answers
