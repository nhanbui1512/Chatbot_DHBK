import itertools
import json
import sys
import threading
import time
from openai import OpenAI
from tools import TOOLS
from services import search_major_information, search_for_admission_information
import inspect


# Initialize LM Studio client
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
MODEL = "qwen2.5-7b-instruct-1m"


FUNCTION_MAPPING = {
    "search_major": search_major_information,
    "search_for_admission_information": search_for_admission_information
}


def call_function_with_json(func, json_data):

    sig = inspect.signature(func)
    func_params = sig.parameters

    filtered_params = {key: json_data.get(
        key, None) for key in func_params.keys()}
    return func(**filtered_params)


def process_tool_calls(response):

    tool_calls = response.tool_calls

    if tool_calls:
        tool_function_name = tool_calls[0].function.name
        tool_query_string = eval(tool_calls[0].function.arguments)
        return tool_function_name, tool_query_string
    else:
        return None, None


# Class for displaying the state of model processing
class Spinner:
    def __init__(self, message="Processing..."):
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.busy = False
        self.delay = 0.1
        self.message = message
        self.thread = None

    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def _spin(self):
        while self.busy:
            self.write(f"\r{self.message} {next(self.spinner)}")
            time.sleep(self.delay)
        self.write("\r\033[K")  # Clear the line

    def __enter__(self):
        self.busy = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.busy = False
        time.sleep(self.delay)
        if self.thread:
            self.thread.join()
        self.write("\r")  # Move cursor to beginning of line


def chat_loop():
    """
    Main chat loop that processes user input and handles tool calls.
    """

    print(
        "Assistant: "
        "Hello! I am the admissions assistant of Danang University of Technology."
    )
    print("(Type 'quit' to exit)")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            break
        messages = [
            {
                "role": "system",
                "system_language": "Vietnamese",
                "content": (
                    "Bạn là trợ lý ảo hỗ trợ hỏi đáp tuyển sinh và các vấn đề liên quan đến tuyển sinh trường đại học Bách Khoa Đà Nẵng và các vấn thông tin liên quan đến trường."
                    "Khi được yêu cầu cung cấp thông tin có liên quan, hãy tóm tắt câu hỏi và đưa ra câu trả lời."
                    "Chỉ trả lời những thông tin mà tool cung cấp và chỉ thông tin liên quan đến câu hỏi"
                    "Câu trả lời phải sử dụng tiếng Việt"
                ),
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        try:
            with Spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS,
                )

            if response.choices[0].finish_reason == 'tool_calls':

                # Handle all tool calls
                tool_calls = response.choices[0].message.tool_calls

                # Add all tool calls to messages
                messages.append(
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": tool_call.type,
                                "function": tool_call.function,
                            }
                            for tool_call in tool_calls
                        ],
                    }
                )

                # Process each tool call and add results
                for tool_call in tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    function_name = tool_call.function.name

                    function_to_do = FUNCTION_MAPPING[function_name]
                    result_function_called = call_function_with_json(
                        func=function_to_do, json_data=args)
                    print(result_function_called)

                    messages.append(
                        {
                            "role": "tool",
                            "content": json.dumps(result_function_called),
                            "tool_call_id": tool_call.id,
                        }
                    )

                # Stream the post-tool-call response
                print("\nAssistant:", end=" ", flush=True)
                stream_response = client.chat.completions.create(
                    model=MODEL, messages=messages, stream=True
                )
                collected_content = ""
                for chunk in stream_response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end="", flush=True)
                        collected_content += content
                print()  # New line after streaming completes
                messages.append(
                    {
                        "role": "assistant",
                        "content": collected_content,
                    }
                )
            else:
                answers = search_for_admission_information(question=user_input)
                print(answers)
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        messages[0],
                        messages[1],
                        {
                            "role": "tool",
                            "content": json.dumps(answers),
                            "tool_call_id": "405959860",
                            "sytem_message": "Only respond in Vietnamese"
                        }
                    ],
                )
                print("\nAssistant:", response.choices[0].message.content)

        except Exception as e:
            print(
                f"\nError chatting with the LM Studio server!\n\n"
                f"Please ensure:\n"
                f"1. LM Studio server is running at 127.0.0.1:1234 (hostname:port)\n"
                f"2. Model '{MODEL}' is downloaded\n"
                f"3. Model '{MODEL}' is loaded, or that just-in-time model loading is enabled\n\n"
                f"Error details: {str(e)}\n"
                "See https://lmstudio.ai/docs/basics/server for more information"
            )
            exit(1)


if __name__ == "__main__":
    chat_loop()
