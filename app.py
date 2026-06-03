import os
import io
import base64
import json
import PIL.Image
import gspread
from google.oauth2 import service_account
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Gemini Setup
genai_api_key = os.environ.get("GEMINI_API_KEY")
import google.generativeai as genai
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def save_to_sheet(bank_name, amount):
    try:
        creds_json = os.environ.get('SERVICE_ACCOUNT_JSON')
        if not creds_json:
            return False, "Environment Variable မတွေ့ရှိပါ"
        
        creds_dict = json.loads(creds_json)
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet = client.open('Walone_Orders').sheet1 
        sheet.append_row([bank_name, amount, "Pending"])
        return True, "အောင်မြင်သည်"
    except Exception as e:
        return False, str(e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        data = request.json
        base64_image = data.get("image")
        image_data = base64.b64decode(base64_image)
        img = PIL.Image.open(io.BytesIO(image_data))
        
        prompt = "ဒီပုံက ငွေလွှဲပြေစာလား? ဘဏ်နာမည်နဲ့ ငွေပမာဏကိုသာ တိကျစွာထုတ်ပေးပါ။ Format: 'ဘဏ်နာမည်,ပမာဏ'"
        response = model.generate_content([prompt, img])
        reply_text = response.text
        
        bank, amount = reply_text.split(',')
        success, msg = save_to_sheet(bank.strip(), amount.strip())
        
        if success:
            return jsonify({"reply": f"{reply_text} - အော်ဒါကို Sheets ထဲသို့ အောင်မြင်စွာ မှတ်တမ်းတင်ပြီးပါပြီ။"})
        else:
            return jsonify({"reply": f"AI ရလဒ်: {reply_text} (Sheet Error: {msg})"})
    except Exception as e:
        return jsonify({"reply": f"Error ဖြစ်နေသည်: {str(e)}"})

if __name__ == '__main__':
    app.run()
