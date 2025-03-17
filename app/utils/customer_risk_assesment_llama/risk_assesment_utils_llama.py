import os
from groq import Groq

def get_groq_client():
    api_key = "sk_1mgo3NgcsgSUaUDebbDsWGdyb3FYJpl6bjuUzbkciQ0RMRaCAgAo"
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    return Groq()

from dotenv import load_dotenv
load_dotenv()
