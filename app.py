from flask import Flask, render_template, jsonify, redirect, url_for
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz

app = Flask(__name__)
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
    # تحويل التاريخ إلى المنطقة الزمنية العربية
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    
    # قائمة الأشهر العربية
    arabic_months = [
        "يناير", "فبراير", "مارس", "إبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    ]
    
    # تنسيق التاريخ بالعربية
    return f"{now.day} {arabic_months[now.month - 1]} {now.year}"

def get_horoscope(sign):
    date = get_arabic_date()
    prompt = f"""
    اكتب توقعات تفصيلية لـ {sign} ليوم {date}. 
    يجب أن تشمل التوقعات المجالات التالية بالترتيب:

    1. نظرة عامة على اليوم
    2. الحب والعلاقات العاطفية
    3. العمل والحياة المهنية
    4. الصحة والطاقة
    5. المال والأمور المادية

    اجعل التوقعات إيجابية ومفصلة ومفيدة.
    قم بتنسيق الإجابة بحيث يكون كل مجال في فقرة منفصلة مع عنوان بارز.
    """
    
    try:
        response = model.generate_content(prompt)
        return {
            'date': date,
            'prediction': response.text
        }
    except Exception as e:
        return {
            'date': date,
            'prediction': f"عذراً، لم نتمكن من جلب توقعات {sign}"
        }

@app.route('/')
def home():
    return render_template('index.html', signs=ZODIAC_SIGNS)

@app.route('/برج/<sign>')
def horoscope_details(sign):
    if sign in ZODIAC_SIGNS:
        return render_template('horoscope_details.html', sign=sign)
    return redirect(url_for('home'))

@app.route('/api/horoscope/<sign>')
def horoscope_api(sign):
    if sign in ZODIAC_SIGNS:
        result = get_horoscope(ZODIAC_SIGNS[sign])
        return jsonify({
            'sign': sign,
            'date': result['date'],
            'horoscope': result['prediction']
        })
    return jsonify({'error': 'برج غير صحيح'}), 400

if __name__ == '__main__':
    app.run(debug=True)
