import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

# API Key ကို Environment Variable ထဲကနေ ခေါ်သုံးပါ
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    try:
        response = model.generate_content(user_message)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "တစ်ခုခုမှားယွင်းနေပါတယ်ခင်ဗျာ။ နောက်တစ်ခါ ထပ်ကြိုးစားကြည့်ပေးပါ။"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
