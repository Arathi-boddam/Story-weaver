import requests

def call_llm(prompt, temperature=0.7):
    url = "http://localhost:11434/api/generate"

    data = {
        "model": "gemma:7b",   # change to gemma model
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    try:
        response = requests.post(url, json=data)
        result = response.json()

        # Ollama returns text in "response"
        return result.get("response", "No response from model")

    except Exception as e:
        return f"Error: {str(e)}"