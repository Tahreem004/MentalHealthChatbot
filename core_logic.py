# ffvuip]
# -*- coding: utf-8 -*-
"""
Created on Fri May 16 00:44:10 2025

@author: tehre
"""

import os
import uuid
import requests
import azure.cognitiveservices.speech as speechsdk
from deep_translator import GoogleTranslator

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_TTS_KEY_1 = os.getenv("AZURE_TTS_KEY_1")
AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")
AZURE_TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

def translate_urdu_to_english(text):
    try:
        return GoogleTranslator(source="ur", target="en").translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return ""

def translate_english_to_urdu(text):
    url = f"{translator_endpoint}/translate?api-version=3.0&from=en&to=ur"
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_TRANSLATOR_REGION,
        'Content-type': 'application/json'
    }
    body = [{'text': text}]
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    result = response.json()
    return result[0]['translations'][0]['text']


def is_query_mental_health_related(text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        "You are a highly accurate mental health content detector. "
        "Respond only with 'Yes' or 'No'.\n"
        "Does the following message talk about emotional well-being, physical health sadness, depression, anxiety, stress, trauma, suicidal thoughts, loneliness, or therapy?\n\n"
        f"Message: \"{text}\"\nAnswer:"
    )
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip().lower()
        return "yes" in answer
    except Exception as e:
        print(f"Classifier Exception: {e}")
        return True  # Assume yes to be safe


def generate_response(english_text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "MentalHealthBot"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a warm, kind, and emotionally intelligent virtual therapist. "
                    "Always respond with empathy. First, gently reflect the person’s possible feelings. "
                    "Then offer 2 clear suggestions for how they might cope or get support. "
                    "Avoid technical or medical terms. Use simple, friendly language like you’re talking to someone you care about deeply. "
                    "Always end with a compassionate question to continue the conversation."
        
                )
                   
            },
            {
                "role": "user",
                "content": f"A person says: \"{english_text}\". Reply simply, helpfully, and briefly."
            }
        ]
    }

    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Response generation failed: {e}")
        return "Error generating response."



def azure_tts_urdu(text):
    try:
        urdu_text = translate_english_to_urdu(text)
        ssml = f"""
        <speak version='1.0' xml:lang='ur-PK'>
            <voice xml:lang='ur-PK' xml:gender='Male' name='ur-PK-AsadNeural'>
                {urdu_text}
            </voice>
        </speak>
        """
        tts_url = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY_1,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
            "User-Agent": "UrduMentalHealthBot"
        }
        response = requests.post(tts_url, headers=headers, data=ssml.encode("utf-8"))

        if response.status_code == 200:
            filename = f"response_{uuid.uuid4().hex}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print("Azure TTS Error:", response.status_code, response.text)
            return None
    except Exception as e:
        print(f"TTS Exception: {e}")
        return None


