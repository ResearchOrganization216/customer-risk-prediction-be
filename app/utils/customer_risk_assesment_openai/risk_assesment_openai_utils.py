import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(prompt):
    try:
        client = openai.OpenAI()  # Use the new API client

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Specialist in the Vehicle Insurance industry"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content  # Correct way to extract response
    
    except openai.OpenAIError as e:  # Correct exception handling
        print(f"OpenAI API Error: {str(e)}")
        return f"OpenAI API Error: {str(e)}"

    except Exception as e:
        print(f"General Error: {str(e)}")
        return f"General Error: {str(e)}"
