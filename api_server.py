from flask import Flask, jsonify
from flask_cors import CORS
from horoscope_manager import HoroscopeManager

app = Flask(__name__)
CORS(app)  # للسماح بالوصول من التطبيق

horoscope_manager = HoroscopeManager()

@app.route('/api/signs', methods=['GET'])
def get_signs():
    """الحصول على قائمة الأبراج"""
    signs = [
        {"id": "aries", "name": "الحمل", "icon": "aries.png"},
        {"id": "taurus", "name": "الثور", "icon": "taurus.png"},
        {"id": "gemini", "name": "الجوزاء", "icon": "gemini.png"},
        {"id": "cancer", "name": "السرطان", "icon": "cancer.png"},
        {"id": "leo", "name": "الأسد", "icon": "leo.png"},
        {"id": "virgo", "name": "العذراء", "icon": "virgo.png"},
        {"id": "libra", "name": "الميزان", "icon": "libra.png"},
        {"id": "scorpio", "name": "العقرب", "icon": "scorpio.png"},
        {"id": "sagittarius", "name": "القوس", "icon": "sagittarius.png"},
        {"id": "capricorn", "name": "الجدي", "icon": "capricorn.png"},
        {"id": "aquarius", "name": "الدلو", "icon": "aquarius.png"},
        {"id": "pisces", "name": "الحوت", "icon": "pisces.png"}
    ]
    return jsonify({"signs": signs})

@app.route('/api/horoscope/<sign>', methods=['GET'])
def get_horoscope(sign):
    """الحصول على توقعات برج معين"""
    result = horoscope_manager.get_horoscope(sign)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
