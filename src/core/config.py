import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL")

def llm(temperature: float = 0):
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=BASE_URL,
        model=MODEL,
        temperature=temperature,
        timeout=60,
        max_retries=3,
    )
