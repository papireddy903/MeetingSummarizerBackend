from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
import PyPDF2
import docx

app = Flask(__name__)
CORS(app)

client = genai.Client()

def extract_text(file):
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif filename.endswith(".docx"):
        doc = docx.Document(file)
        text = "\n".join([p.text for p in doc.paragraphs])
    elif filename.endswith(".txt"):
        text = file.read().decode("utf-8")
    else:
        text = "Unsupported file format"
    return text

@app.route("/api/summarize", methods=["POST"])
def summarize():
    try:
        prompt = request.form.get("prompt", "")
        file = request.files["file"]

        transcript = extract_text(file)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are a meeting summarizer."
            ),
            contents=f"Transcript: {transcript}\nPrompt: {prompt}"
        )

        return jsonify({"summary": response.text})
    
    except Exception as e:
        return jsonify({"error": str(e)})
