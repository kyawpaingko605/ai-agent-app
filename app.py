import os
import io
import base64
import json
import PIL.Image
import gspread
from google.oauth2 import service_account
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

# API Key စစ်ဆေးခြင်း
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def save_to_sheet(bank_name, amount):
    try:
        # JSON ကို string အနေနဲ့ယူပြီး dict ပြောင်းခြင်း
        creds_json = os.environ.get('SERVICE_ACCOUNT_JSON')
        creds_dict = json.loads(creds_json)
        
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # Sheet နာမည်အတိအကျ
        sheet = client.open('Walone_Orders').sheet1 
        sheet.append_row([bank_name, amount, "Pending"])
        return True, "Success"
    except Exception as e:
        return False, str(e) # ဘာ Error လဲဆိုတာကို ဒီမှာ သိနိုင်ပါတယ်

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        data = request.json
        base64_image = data.get("image")
        if not base64_image:
            return jsonify({"reply": "ပုံမပါဝင်ပါ"})
            
        image_data = base64.b64decode(base64_image)
        img = PIL.Image.open(io.BytesIO(image_data))
        
        prompt = "ဒီပုံက ငွေလွှဲပြေစာလား? ဘဏ်နာမည်နဲ့ ငွေပမာဏကိုသာ တိကျစွာထုတ်ပေးပါ။ Format: 'ဘဏ်နာမည်,ပမာဏ'"
        response = model.generate_content([prompt, img])
        reply_text = response.text
        
        # split လုပ်လို့မရရင် error တက်မှာမို့လို့ try-except သုံးထားပါတယ်
        parts = reply_text.split(',')
        if len(parts) == 2:
            bank, amount = parts
            success, msg = save_to_sheet(bank.strip(), amount.strip())
            if success:
                return jsonify({"reply": f"အောင်မြင်စွာသိမ်းဆည်းပြီးပါပြီ: {bank}, {amount}"})
            else:
                return jsonify({"reply": f"Sheet Error: {msg}"})
        else:
            return jsonify({"reply": f"AI ရလဒ်: {reply_text} (Format မမှန်ပါ)"})
            
    except Exception as e:
        return jsonify({"reply": f"Server Error: {str(e)}"})

if __name__ == '__main__':
    app.run()
