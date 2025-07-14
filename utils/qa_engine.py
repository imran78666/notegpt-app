import os
import time
from dotenv import load_dotenv
from groq import Groq, RateLimitError
from langchain.text_splitter import CharacterTextSplitter

# ✅ Load .env file
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# ✅ Create Groq client using the hidden key
client = Groq(api_key=groq_api_key)


def load_chunks(text, chunk_size=1500, chunk_overlap=100):
    splitter = CharacterTextSplitter(separator="\n", chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(text)
    return chunks


def answer_question(question, chunks):
    # Using more chunks for detailed answers
    limited_chunks = "\n\n".join(chunks[:3])

    prompt = f"""
You are a helpful teacher. Provide a **detailed, easy-to-understand explanation suitable for students**.
Explain the topic clearly step-by-step, with examples, comparisons, and all important points. 
Avoid very short answers. Write as if explaining to a beginner.

Topic: {question}

Content to refer:
{limited_chunks}
"""

    while True:
        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1800,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            time.sleep(8)
