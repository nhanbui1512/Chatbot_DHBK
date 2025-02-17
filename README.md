# Chatbot BKDN

## Giới thiệu

Đây là một chatbot sử dụng mô hình AI để truy vấn cơ sở dữ liệu và xử lý câu hỏi từ người dùng. Dự án này yêu cầu sử dụng **LmStudio** với mô hình **qwen2.5-7b-instruct-1m** để chạy inference.

## Cấu trúc thư mục

- **agent.py**: Tập tin chính để chạy chương trình chatbot.
- **data.csv**: Chứa dữ liệu câu hỏi và câu trả lời.
- **embeddings.npy**: Chứa vector embedding của các câu hỏi/câu trả lời.
- **models.py**: Xử lý truy vấn cơ sở dữ liệu.
- **processor.py**: Tiền xử lý dữ liệu văn bản.
- **tools.py**: Định nghĩa các tool cho function calling.
- **phrases.txt**: Chứa danh sách các cụm từ cần gom nhóm (ví dụ: "hướng dẫn" -> "hướng_dẫn").
- **question_test.yml**: Chứa dữ liệu test.
- **data/**: Chứa dữ liệu gốc của dự án.
- **venv/**: Môi trường ảo của Python.

## Hướng dẫn cài đặt

### 1. Tạo cơ sở dữ liệu

Tạo database bằng file `.sql` có trong dự án.

### 2. Cài đặt LmStudio

- Tải và cài đặt **LmStudio**.
- Tải mô hình **qwen2.5-7b-instruct-1m**.
- Khởi động server LmStudio.

### 3. Thiết lập môi trường Python

```sh
python -m venv venv
source venv/bin/activate  # Trên macOS/Linux
venv\Scripts\activate    # Trên Windows
```

### 4. Cài đặt các thư viện cần thiết

```sh
pip install -r requirements.txt
```

### 5. Chạy chatbot

```sh
python agent.py
```

## Liên hệ

Nếu bạn có bất kỳ câu hỏi nào, vui lòng liên hệ với nhóm phát triển.
