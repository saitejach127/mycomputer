import requests
import os

def get_gemini_response(text, api_key):
    """
    Sends a request to the Gemini API and returns the response.
    """
    if not api_key:
        return "GEMINI_API_KEY not set."

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    data = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}},
    }
    
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {e}"
