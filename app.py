from flask import Flask, request, jsonify, render_template  # render_template-ஐ சேர்க்கவும்
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="AQ.Ab8RN6IZ8OCI_Mqj3L_09tctWjbPluhPaCS-8kan64Hy8RMWUw")

import json

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan-link', methods=['POST'])
def scan_link():
    data = request.get_json(silent=True) or {}
    user_input = data.get('message', '')
    if not user_input and request.form:
        user_input = request.form.get('message', '')
    if not user_input and request.data:
        try:
            raw_data = json.loads(request.data.decode('utf-8', errors='ignore'))
            user_input = raw_data.get('message', '')
        except Exception:
            pass
    user_input = (user_input or '').strip()
    
    if not user_input:
        return jsonify({"error": "No message or link provided"}), 400
    
    prompt = f"""
You are ScamShield AI, an advanced multi-modal threat and fraud detection engine. 
Analyze the following input thoroughly and instantly. The input can be a URL, a text message, an article, or a certificate/document description.

Detect if it falls under any of these categories:
1. Phishing or malicious link / Telegram scam job offer.
2. Fake academic or professional certificate / forged credentials.
3. Deepfake AI video context or misleading/fraudulent fake news article.

Provide your response strictly in the following JSON format:
{{
    "is_scam": true/false,
    "risk_level": "High Risk" / "Medium Risk" / "Safe",
    "threat_type": "Phishing Link" / "Fake Certificate" / "AI Video/Article Scam" / "Legitimate",
    "reason": "Crisp 1-2 sentence explanation tailored for users."
}}

Input to analyze: {user_input}
"""

    candidate_models = ['gemini-3.5-flash-lite', 'gemini-3.8-flash']
    response = None
    last_error = None

    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                break
        except Exception as err:
            last_error = err
            continue

    if not response or not response.text:
        return jsonify({"error": f"Analysis failed: {str(last_error)}"}), 500

    raw_text = (response.text or "").strip()
    clean_text = raw_text
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    
    try:
        parsed = json.loads(clean_text)
        return jsonify({"result": parsed, "raw": raw_text})
    except json.JSONDecodeError:
        return jsonify({"result": raw_text})


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)

