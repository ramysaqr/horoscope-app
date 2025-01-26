import sqlite3
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pytz
import json
import random

class HoroscopeManager:
    def __init__(self):
        # إعداد قاعدة البيانات
        self.conn = sqlite3.connect('horoscope.db')
        self.create_tables()
        
        # تحميل مفاتيح API
        load_dotenv()
        self.api_keys = self._load_api_keys()
        self.setup_gemini()
    
    def create_tables(self):
        # جدول التوقعات
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS horoscopes (
            sign TEXT,
            date TEXT,
            prediction TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (sign, date)
        )
        ''')
        
        # جدول إحصائيات API
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS api_stats (
            api_key TEXT PRIMARY KEY,
            requests_count INTEGER DEFAULT 0,
            last_used TIMESTAMP
        )
        ''')
        self.conn.commit()
    
    def _load_api_keys(self):
        """تحميل مفاتيح API من ملف .env"""
        keys = []
        main_key = os.getenv('GEMINI_API_KEY')
        if main_key:
            keys.append(main_key)
        
        # تحميل مفاتيح إضافية إذا وجدت
        for i in range(1, 6):  # دعم حتى 5 مفاتيح إضافية
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                keys.append(key)
        
        return keys
    
    def setup_gemini(self):
        """إعداد Gemini API مع مفتاح عشوائي"""
        if not self.api_keys:
            raise Exception("لم يتم العثور على أي مفاتيح API!")
        
        current_key = random.choice(self.api_keys)
        genai.configure(api_key=current_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def get_arabic_date(self):
        """الحصول على التاريخ بالعربية"""
        cairo_tz = pytz.timezone('Africa/Cairo')
        now = datetime.now(cairo_tz)
        
        arabic_months = [
            "يناير", "فبراير", "مارس", "إبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ]
        
        return f"{now.day} {arabic_months[now.month - 1]} {now.year}"
    
    def get_horoscope(self, sign):
        """الحصول على توقعات برج معين"""
        date = self.get_arabic_date()
        
        # محاولة استرجاع التوقعات من التخزين المؤقت
        cached = self._get_cached_horoscope(sign, date)
        if cached:
            return {
                'sign': sign,
                'date': date,
                'prediction': cached,
                'source': 'cache'
            }
        
        # إذا لم يتم العثور على توقعات مخزنة، نجلب توقعات جديدة
        try:
            prediction = self._fetch_new_horoscope(sign, date)
            self._cache_horoscope(sign, date, prediction)
            
            return {
                'sign': sign,
                'date': date,
                'prediction': prediction,
                'source': 'api'
            }
        except Exception as e:
            # في حالة الفشل، نحاول استخدام مفتاح API آخر
            self.setup_gemini()
            try:
                prediction = self._fetch_new_horoscope(sign, date)
                self._cache_horoscope(sign, date, prediction)
                return {
                    'sign': sign,
                    'date': date,
                    'prediction': prediction,
                    'source': 'api_fallback'
                }
            except:
                return {
                    'sign': sign,
                    'date': date,
                    'prediction': f"عذراً، لم نتمكن من جلب توقعات {sign}",
                    'source': 'error'
                }
    
    def _get_cached_horoscope(self, sign, date):
        """استرجاع التوقعات المخزنة"""
        cursor = self.conn.execute(
            'SELECT prediction FROM horoscopes WHERE sign = ? AND date = ?',
            (sign, date)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def _cache_horoscope(self, sign, date, prediction):
        """تخزين التوقعات في قاعدة البيانات"""
        self.conn.execute(
            'INSERT OR REPLACE INTO horoscopes (sign, date, prediction) VALUES (?, ?, ?)',
            (sign, date, prediction)
        )
        self.conn.commit()
    
    def _fetch_new_horoscope(self, sign, date):
        """جلب توقعات جديدة من Gemini API"""
        prompt = f"""
        اكتب توقعات تفصيلية لـ {sign} ليوم {date}. 
        يجب أن تشمل التوقعات المجالات التالية بالترتيب:

        1. نظرة عامة على اليوم
        2. الحب والعلاقات العاطفية
        3. العمل والحياة المهنية
        4. الصحة والطاقة
        5. المال والأمور المادية

        اجعل التوقعات إيجابية ومفصلة ومفيدة.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def cleanup_old_cache(self, days=7):
        """تنظيف التوقعات القديمة"""
        self.conn.execute(
            'DELETE FROM horoscopes WHERE julianday(CURRENT_TIMESTAMP) - julianday(created_at) > ?',
            (days,)
        )
        self.conn.commit()
    
    def __del__(self):
        """إغلاق اتصال قاعدة البيانات"""
        self.conn.close()
