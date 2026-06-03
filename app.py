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

# Google Sheets ချိတ်ဆက်ခြင်း
def save_to_sheet(bank_name, amount):
    try:
        # Render Environment Variable ထဲက JSON ကို ယူမယ်
        creds_json = os.environ.get('SERVICE_ACCOUNT_JSON')
        creds_dict = json.loads(creds_json)
        
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # သင့် Google Sheet နာမည်ကို ထည့်ပါ
        sheet = client.open('Walone_Orders').sheet1 
        sheet.append_row([bank_name, amount, "Pending"])
        return True
    except Exception as e:
        print(f"Error saving to sheet: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.json
    base64_image = data.get("image")
    image_data = base64.b64decode(base64_image)
    img = PIL.Image.open(io.BytesIO(image_data))
    
    prompt = "ဒီပုံက ငွေလွှဲပြေစာလား? ဘဏ်နာမည်နဲ့ ငွေပမာဏကိုသာ တိကျစွာထုတ်ပေးပါ။ Format: 'ဘဏ်နာမည်,ပမာဏ'"
    response = model.generate_content([prompt, img])
    reply_text = response.text
    
    try:
        bank, amount = reply_text.split(',')
        if save_to_sheet(bank.strip(), amount.strip()):
            final_reply = f"{reply_text} - အော်ဒါကို Sheets ထဲသို့ အောင်မြင်စွာ မှတ်တမ်းတင်ပြီးပါပြီ။"
        else:
            final_reply = f"AI ရလဒ်: {reply_text} (Sheet ထဲ မသိမ်းနိုင်ခဲ့ပါ)"
    except:
        final_reply = f"AI ရလဒ်: {reply_text} (Format မှားနေသည်)"
        
    return jsonify({"reply": final_reply})

if __name__ == '__main__':
    app.run(debug=True)
