import os
import io
import base64
import json
import PIL.Image
import gspread
from google.oauth2 import service_account
from flask import Flask, request, jsonify, render_template, session
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'walone_secret_key_123'

# Gemini Setup
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Google Sheets Function (ပြင်ဆင်ပြီး)
def save_to_sheet(bank_name, amount):
    try:
        # Environment Variable ထဲက JSON ကို ယူခြင်း
        creds_json = os.environ.get('SERVICE_ACCOUNT_JSON')
        creds_dict = json.loads(creds_json)
        
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet = client.open('Walone_Orders').sheet1 
        sheet.append_row([bank_name, amount, "Pending"])
        return True
    except Exception as e:
        print(f"Error saving to sheet: {e}")
        return False

@app.route('/')
def home():
    session['chat_history'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    try:
        response = model.generate_content(user_message)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "မှားယွင်းမှုရှိပါသည်။"})

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.json
    base64_image = data.get("image")
    image_data = base64.b64decode(base64_image)
    img = PIL.Image.open(io.BytesIO(image_data))
    
    # AI Vision ကို မေးခြင်း
    prompt = "ဒီပုံက ငွေလွှဲပြေစာလား? ဘဏ်နာမည်နဲ့ ငွေပမာဏကိုသာ တိကျစွာထုတ်ပေးပါ။ Format: 'ဘဏ်နာမည်,ပမာဏ'"
    response = model.generate_content([prompt, img])
    reply_text = response.text
    
    # Google Sheets ထဲ သိမ်းခြင်း
    try:
        # AI ကပေးတဲ့ output မှာ comma တွေပါနိုင်လို့ သတိထားပါ
        bank, amount = reply_text.split(',')
        if save_to_sheet(bank.strip(), amount.strip()):
            final_reply = f"{reply_text} - အော်ဒါကို Sheets ထဲသို့ အောင်မြင်စွာ မှတ်တမ်းတင်ပြီးပါပြီ။"
        else:
            final_reply = f"AI ရလဒ်: {reply_text} (Sheet ထဲ မသိမ်းနိုင်ခဲ့ပါ - Permission စစ်ဆေးပါ)"
    except Exception as e:
        final_reply = f"AI ရလဒ်: {reply_text} (Error: {str(e)})"
        
    return jsonify({"reply": final_reply})

if __name__ == '__main__':
    app.run(debug=True)
