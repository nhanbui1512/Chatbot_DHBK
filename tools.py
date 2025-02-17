TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_major",
            "description": "Truy vấn cơ sở dữ liệu để tìm thông tin điểm trúng tuyển theo các phương thức xét tuyển của trường đại học.",
            "parameters": {
                "type": "object",
                "properties": {
                    "major_name": {
                        "type": "string",
                        "description": "Tên ngành đào tạo mà người dùng muốn tra cứu điểm trúng tuyển. Ví dụ: 'Công nghệ thông tin', 'Kinh tế', 'Y khoa'."
                    },
                    "year": {
                        "type": "integer",
                        "description": "Năm xét tuyển mà người dùng muốn tra cứu. Chỉ nhận giá trị là năm dương lịch, ví dụ: 2023, 2024."
                    },
                    "admission_method": {
                        "type": "string",
                        "enum": ["thi_THPT", "hoc_ba", "ky_thi_truong"],
                        "description": "Phương thức xét tuyển mà người dùng muốn tra cứu điểm trúng tuyển. Các giá trị có thể là: \n- 'thi_THPT': Điểm xét tuyển dựa trên kỳ thi tốt nghiệp THPT. \n- 'hoc_ba': Điểm xét tuyển dựa trên học bạ cấp 3.\n- 'ky_thi_truong': Điểm xét tuyển dựa trên kỳ thi riêng do trường tổ chức."
                    },
                    "subject_group": {
                        "type": "string",
                        "description": "Tổ hợp môn xét tuyển mà người dùng quan tâm, ví dụ: 'A00' (Toán, Lý, Hóa), 'D01' (Toán, Văn, Anh)."
                    }
                },
                "required": ["major_name", "year"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_for_admission_information",
            "description": "Truy vấn vector database để tìm kiếm câu trả lời cho các câu hỏi liên quan đến tuyển sinh và thông tin trường đại học.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Câu hỏi mà người dùng muốn tìm kiếm thông tin về tuyển sinh hoặc về trường đại học. Ví dụ: \n- 'Trường có những ngành đào tạo nào?'\n- 'Điều kiện tuyển sinh ngành Khoa học Máy tính là gì?'\n- 'Số điện thoại liên hệ của trường là gì?'\n- 'Trường có ký túc xá không?'"
                    }
                },
                "required": ["question"]
            }
        }
    }
]
