
import flask
import whisper
import os
from flask import request, jsonify

app = flask.Flask(__name__)
model = whisper.load_model(os.getenv("MODEL_SIZE", "base.en"))

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "no audio file"}), 400

    audio_file = request.files["audio"]
    temp_path = "temp_audio.wav"
    audio_file.save(temp_path)

    try:
        result = model.transcribe(temp_path)
        transcription = result["text"]
    finally:
        os.remove(temp_path)

    return jsonify({"transcription": transcription})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
