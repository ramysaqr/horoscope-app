from flask import Flask, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)  # للسماح بالوصول من AppCreator24
load_dotenv()

# تكوين Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# قائمة الأبراج باللغة العربية
ZODIAC_SIGNS = {
    "الحمل": "برج الحمل",
    "الثور": "برج الثور",
    "الجوزاء": "برج الجوزاء",
    "السرطان": "برج السرطان",
    "الأسد": "برج الأسد",
    "العذراء": "برج العذراء",
    "الميزان": "برج الميزان",
    "العقرب": "برج العقرب",
    "القوس": "برج القوس",
    "الجدي": "برج الجدي",
    "الدلو": "برج الدلو",
    "الحوت": "برج الحوت"
}

def get_arabic_date():
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    
    arabic_months = [
        "يناير", "فبراير", "مارس", "إبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    ]
    
    return f"{now.day} {arabic_months[now.month - 1]} {now.year}"

@app.route('/api/signs', methods=['GET'])
def get_signs():
    """الحصول على قائمة الأبراج"""
    return jsonify({
        'signs': list(ZODIAC_SIGNS.keys())
    })

@app.route('/api/horoscope/<sign>', methods=['GET'])
def get_horoscope(sign):
    """الحصول على توقعات برج معين"""
    if sign not in ZODIAC_SIGNS:
        return jsonify({'error': 'برج غير صحيح'}), 400

    date = get_arabic_date()
    prompt = f"""
    اكتب توقعات تفصيلية لـ {ZODIAC_SIGNS[sign]} ليوم {date}. 
    يجب أن تشمل التوقعات المجالات التالية بالترتيب:

    1. نظرة عامة على اليوم
    2. الحب والعلاقات العاطفية
    3. العمل والحياة المهنية
    4. الصحة والطاقة
    5. المال والأمور المادية

    اجعل التوقعات إيجابية ومفصلة ومفيدة.
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({
            'sign': sign,
            'date': date,
            'horoscope': response.text
        })
    except Exception as e:
        return jsonify({
            'error': f"حدث خطأ في جلب التوقعات: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
