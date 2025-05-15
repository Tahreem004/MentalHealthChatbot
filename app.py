# -*- coding: utf-8 -*-
"""
Created on Fri May 16 00:43:56 2025

@author: tehreem
"""

from flask import Flask, request, jsonify, send_file
from core_logic import (
    translate_urdu_to_english,
    is_query_mental_health_related,
    generate_response,
    azure_tts_urdu
)
import os
from werkzeug.utils import secure_filename
import speech_recognition as sr
from pydub import AudioSegment
from googletrans import Translator

app = Flask(__name__)

# ---------------------- ROUTES ---------------------- #

@app.route("/")
def index():
    return "Mental Health API is live!"

@app.route("/classify", methods=["POST"])
def classify():
    data = request.json
    text = data.get("text", "")
    english = translate_urdu_to_english(text)
    result = is_query_mental_health_related(english)
    return jsonify({"mental_health_related": result})

@app.route("/respond", methods=["POST"])
def respond():
    data = request.json
    urdu_text = data.get("text", "")
    english_text = translate_urdu_to_english(urdu_text)

    if is_query_mental_health_related(english_text):
        response = generate_response(english_text)
    else:
        response = "میں معذرت کرتا ہوں! میں صرف آپ کی ذہنی صحت سے متعلق مشورے دے سکتا ہوں۔"

    audio_file = azure_tts_urdu(response)

    if audio_file and os.path.exists(audio_file):
        from flask import after_this_request

        @after_this_request
        def cleanup(response_obj):
            try:
                os.remove(audio_file)
            except Exception as e:
                print(f"Cleanup error: {e}")
            return response_obj

        return send_file(audio_file, mimetype="audio/mpeg", as_attachment=True, download_name="response.mp3")
    else:
        return jsonify({"error": "Failed to generate or locate audio file"}), 500



@app.route("/transcribe_translate", methods=["POST"])
def transcribe_and_translate():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    filename = secure_filename(audio_file.filename)
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, filename)
    audio_file.save(file_path)

    try:
        # Convert to WAV if needed
        if not filename.endswith(".wav"):
            sound = AudioSegment.from_file(file_path)
            file_path = file_path.rsplit(".", 1)[0] + ".wav"
            sound.export(file_path, format="wav")

        # Transcribe using Google Web Speech API
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            urdu_text = recognizer.recognize_google(audio_data, language="ur-PK")

        # Translate to English
        translator = Translator()
        translation = translator.translate(urdu_text, src="ur", dest="en")

        os.remove(file_path)

        return jsonify({
            "urdu_text": urdu_text,
            "english_translation": translation.text
        })

    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/voice_assist", methods=["POST"])
def voice_assist():
    # ... (initial code)
    try:
        # Transcription and TTS code

        audio_response_path = azure_tts_urdu(response_text)
        print(f"TTS audio path: {audio_response_path}")
        if audio_response_path is None or not os.path.exists(audio_response_path):
            return jsonify({"error": "Failed to generate or locate audio response"}), 500

        from flask import after_this_request

        @after_this_request
        def cleanup(response_obj):
            try:
                os.remove(audio_response_path)
            except Exception as e:
                print(f"Cleanup error: {e}")
            return response_obj

        return send_file(audio_response_path, mimetype="audio/mpeg", as_attachment=True, download_name="response.mp3")

    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except Exception as e:
        print(f"Unexpected error in voice_assist: {e}")
        return jsonify({"error": str(e)}), 500


# ---------------------- RUN APP ---------------------- #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
