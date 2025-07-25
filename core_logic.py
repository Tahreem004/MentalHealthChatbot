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
    "You are a highly accurate and cautious mental health content detector.\n"
    "Respond only with 'Yes' or 'No'.\n"
    "Does the following message relate to emotional well-being, mental health conditions, or physical symptoms often associated with stress, anxiety, or depression?\n"
    "Consider topics like sadness, depression, anxiety, stress, trauma, suicidal thoughts, loneliness, therapy, insomnia, fatigue, headache, chest pain, body tension, stomach issues, or other stress-related physical symptoms.\n\n"
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
                  "You are a compassionate and emotionally intelligent virtual therapist. "
                    "Speak like a real therapist would—calm, warm, and validating. "
                    "Begin by gently acknowledging and reflecting the person's possible thoughts or emotions. "
                    "Use affirming, non-judgmental language that shows understanding and care. "
                    "Then, offer 1 or 2 simple, realistic suggestions they could try to feel a bit better or seek support—only if appropriate. "
                    "Avoid technical or clinical terms. Use simple, comforting language, like you're gently talking to a friend in distress. "
                    "Encourage self-kindness and agency. "
                    "End your response with a soft, open-ended question that invites them to share more or explore their feelings further."

        
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


