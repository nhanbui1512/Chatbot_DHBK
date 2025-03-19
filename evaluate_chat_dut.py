import pandas as pd
from tqdm.auto import tqdm
import json
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain.schema import SystemMessage
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
EVALUATION_PROMPT = """###Task Description:
An instruction (might include an Input inside it), a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given.
1. Write a detailed feedback that assess the quality of the response strictly based on the given score rubric, not evaluating in general.
2. After writing a feedback, write a score that is an integer between 1 and 5. You should refer to the score rubric.
3. The output format should look as follows: \"Feedback: {{write a feedback for criteria}} [RESULT] {{an integer number between 1 and 5}}\"
4. Please do not generate any other opening, closing, and explanations. Be sure to include [RESULT] in your output.

###The instruction to evaluate:
{instruction}

###Response to evaluate:
{response}

###Reference Answer (Score 5):
{reference_answer}

###Score Rubrics:
[Is the response correct, accurate, and factual based on the reference answer?]
Score 1: The response is completely incorrect, inaccurate, and/or not factual.
Score 2: The response is mostly incorrect, inaccurate, and/or not factual.
Score 3: The response is somewhat correct, accurate, and/or factual.
Score 4: The response is mostly correct, accurate, and factual.
Score 5: The response is completely correct, accurate, and factual.

###Feedback:"""


evaluation_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content="You are a fair evaluator language model."),
        HumanMessagePromptTemplate.from_template(EVALUATION_PROMPT),
    ]
)


load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = API_KEY
print(OPENAI_API_KEY)


BASE_URL = "http://localhost:1234/v1"
MODEL_GPT_REVIEW = "gpt-4-1106-preview"
MODEL_NAME = "qwen2.5-7b-instruct-1m"
eval_chat_model = ChatOpenAI(
    model=MODEL_GPT_REVIEW, temperature=0, openai_api_key=OPENAI_API_KEY)
evaluator_name = "GPT4"


def evaluate_answers(
    answer_path: str,
    eval_chat_model,
    evaluator_name: str,
    evaluation_prompt_template: ChatPromptTemplate,
) -> None:
    """Evaluates generated answers and saves results back to an Excel file."""

    if os.path.isfile(answer_path):
        df = pd.read_excel(answer_path)  # Đọc file Excel
    else:
        raise FileNotFoundError(f"File {answer_path} không tồn tại.")

    # Đảm bảo cột tồn tại trước khi sử dụng
    eval_score_col = f"eval_score_{evaluator_name}"
    eval_feedback_col = f"eval_feedback_{evaluator_name}"

    if eval_score_col not in df.columns:
        df[eval_score_col] = None
    if eval_feedback_col not in df.columns:
        df[eval_feedback_col] = None

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        if not pd.isna(row[eval_score_col]):
            continue  # Bỏ qua nếu đã đánh giá rồi

        eval_prompt = evaluation_prompt_template.format_messages(
            instruction=row["question"],
            response=row["LLM answers"],
            reference_answer=row["true_answer"],
        )
        eval_result = eval_chat_model.invoke(eval_prompt)

        # Tách feedback và score
        result_parts = eval_result.content.rsplit("[RESULT]", 1)
        feedback = result_parts[0].strip()
        score = result_parts[1].strip() if len(result_parts) > 1 else "N/A"

        df.at[idx, eval_score_col] = score
        df.at[idx, eval_feedback_col] = feedback

    df.to_excel(answer_path, index=False)  # Lưu lại file Excel


evaluate_answers(answer_path='./evaluate_question_with_answers.xlsx', eval_chat_model=eval_chat_model,
                 evaluator_name=evaluator_name, evaluation_prompt_template=evaluation_prompt_template)
