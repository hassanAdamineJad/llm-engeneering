import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')
openai= OpenAI(api_key=api_key)

system_prompt = """
You are a helpful assistant.
"""

user_prompt = "What is the capital of France?"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
]

response = openai.chat.completions.create(model="gpt-6-luna", reasoning_effort="none", messages=messages)
print(response.choices[0].message.content)