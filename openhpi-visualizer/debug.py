import langfun as lf
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the generative AI model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# This is a minimal, reproducible example that demonstrates the issue.
summary = lf.query(
    "Summarize the following text in one sentence: {{text}}",
    lm=lf.llms.GeminiPro(),
    text="Langfun is a Python library for natural language processing."
)

print(summary)
