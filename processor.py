import numpy as np
import torch
from pyvi import ViTokenizer
import re
from torch.nn.functional import cosine_similarity
from transformers import AutoModel, AutoTokenizer
import pandas as pd

PhobertTokenizer = AutoTokenizer.from_pretrained(
    "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")
model = AutoModel.from_pretrained(
    "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")


numpy_embeddings = np.load("embeddings.npy")
torch_embeddings = torch.from_numpy(numpy_embeddings)


df = pd.read_csv('data.csv', usecols=['questions', 'answers'])


#! Đọc các cụm từ cần gộp từ file
def load_phrases(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        phrases = [line.strip() for line in file.readlines()]
    return phrases


file_path = 'phrases.txt'
custom_phrases = load_phrases(file_path)


def custom_tokenize(text):
    for phrase in custom_phrases:
        #! Gom nhóm các cụm từ có nghĩa
        text = text.replace(phrase, phrase.replace(" ", "_"))
    return ViTokenizer.tokenize(text)


def tokenize_sentences(sentences):
    result = []
    for sentence in sentences:
        result.append(custom_tokenize(sentence))
    return result


def clean_text(text):
    # Loại bỏ khoảng trống dư thừa giữa các từ
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(':\)|;\)|:-\)|\(-:|:-D|=D|:P|xD|X-p|\^\^|:-*|\^\.\^|\^\-\^|\^\_\^|\,-\)|\)-:|:\'\(|:\(|:-\(|:\S|T\.T|\.\_\.|:<|:-\S|:-<|\*\-\*|:O|=O|=\-O|O\.o|XO|O\_O|:-\@|=/|:/|X\-\(|>\.<|>=\(|D:', '', text)
    text = re.sub(r'\!', '', text)  # xoa dau cham than
    text = re.sub(r'\?', '', text)  # xoa dau hoi cham
    text = re.sub(r'\.', '', text)  # xoa dau cham cau
    text = re.sub(r'#([^\s]+)', r'\1', text)  # xóa các hastag #
    # xoa cac dau ngoac kep vs ngoac don
    text = re.sub(r'["\'()[]{}]', '', text)
    text = text.lower()
    return text.strip()


def pre_process_question(question_text):
    input_text = [question_text]
    input_text = list(map(clean_text, input_text))
    input_text = tokenize_sentences(input_text)
    input_questions = PhobertTokenizer(
        input_text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        embeddings_question = model(
            **input_questions, output_hidden_states=True, return_dict=True).pooler_output
        return embeddings_question


def find_similarity_vectors(embedding_vector):
    result = []
    cosine_sim = cosine_similarity(embedding_vector, torch_embeddings, dim=1)

    similar_indices = torch.where(cosine_sim >= 0.81)[0]
    sorted_indices = similar_indices[torch.argsort(
        cosine_sim[similar_indices], descending=True)]

    top_3_indices = sorted_indices[:3]
    for idx in top_3_indices:
        result.append(df.iloc[idx.item()])
    return result
