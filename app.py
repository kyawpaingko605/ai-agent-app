import PIL.Image  # ပုံတွေကို processing လုပ်ဖို့
import io
import base64
import os
from flask import Flask, request, jsonify, render_template, session
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'walone_secret_key_123' # လိုအပ်ပါက ပြောင်းလဲနိုင်ပါတယ်

# Gemini Setup
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def home():
    session['chat_history'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    history = session.get('chat_history', [])
    
    try:
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(user_message)
        
        history.append({"role": "user", "parts": [user_message]})
        history.append({"role": "model", "parts": [response.text]})
        session['chat_history'] = history
        
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "မှားယွင်းမှုရှိပါသည်။ Key ကို စစ်ဆေးပေးပါ။"})

if __name__ == '__main__':
    app.run(debug=True)
