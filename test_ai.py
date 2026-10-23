import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY was not found in your .env file.")
    raise SystemExit(1)

try:
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are CampusAI, a helpful college study assistant."
            },
            {
                "role": "user",
                "content": "Introduce yourself as CampusAI in one sentence."
            }
        ],
        max_tokens=100
    )

    print("\nCampusAI AI connection successful!")
    print(response.choices[0].message.content)

except Exception as error:
    print("\nAI connection failed.")
    print("Error:", error)