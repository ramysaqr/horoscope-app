from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
import threading
from horoscope_manager import HoroscopeManager

# تحميل ملف التصميم
KV = '''
#:import NoTransition kivy.uix.screenmanager.NoTransition

MDScreenManager:
    id: screen_manager
    transition: NoTransition()
    
    MDScreen:
        name: "main"
        md_bg_color: 0.1, 0.1, 0.18, 1
        
        MDBoxLayout:
            orientation: "vertical"
            padding: "20dp"
            spacing: "20dp"
            
            MDLabel:
                text: "الأبراج اليومية"
                halign: "center"
                font_style: "H4"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                size_hint_y: None
                height: "60dp"
                
            MDGridLayout:
                id: grid
                cols: 2
                spacing: "15dp"
                padding: "10dp"
                
    MDScreen:
        name: "details"
        md_bg_color: 0.1, 0.1, 0.18, 1
        
        MDBoxLayout:
            orientation: "vertical"
            padding: "20dp"
            spacing: "15dp"
            
            MDIconButton:
                icon: "arrow-right"
                pos_hint: {"right": 1}
                on_release: app.go_back()
                
            MDLabel:
                id: sign_title
                halign: "center"
                font_style: "H5"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                
            MDLabel:
                id: date_label
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.31, 0.82, 0.77, 1
                
            ScrollView:
                MDLabel:
                    id: horoscope_text
                    padding: "15dp", "15dp"
                    halign: "right"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 0.9
                    size_hint_y: None
                    height: self.texture_size[1]
'''

class HoroscopeCard(MDCard):
    def __init__(self, sign, **kwargs):
        super().__init__(**kwargs)
        self.sign = sign
        self.md_bg_color = (0.09, 0.14, 0.27, 1)
        self.padding = "15dp"
        self.radius = [15]
        self.elevation = 2
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = "150dp"
        
        title = MDLabel(
            text=sign,
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H6"
        )
        
        subtitle = MDLabel(
            text="اضغط لمعرفة توقعات اليوم",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.31, 0.82, 0.77, 1)
        )
        
        self.add_widget(title)
        self.add_widget(subtitle)

class HoroscopeApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.horoscope_manager = HoroscopeManager()
        
        # قائمة الأبراج
        self.zodiac_signs = [
            "الحمل", "الثور", "الجوزاء", "السرطان",
            "الأسد", "العذراء", "الميزان", "العقرب",
            "القوس", "الجدي", "الدلو", "الحوت"
        ]
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        return Builder.load_string(KV)
    
    def on_start(self):
        grid = self.root.get_screen("main").ids.grid
        for sign in self.zodiac_signs:
            card = HoroscopeCard(sign)
            card.bind(on_release=lambda x, s=sign: self.show_horoscope(s))
            grid.add_widget(card)
        
        # تنظيف التخزين المؤقت القديم
        self.horoscope_manager.cleanup_old_cache()
    
    def show_horoscope(self, sign):
        screen = self.root.get_screen("details")
        screen.ids.sign_title.text = sign
        screen.ids.horoscope_text.text = "جاري تحميل التوقعات..."
        screen.ids.date_label.text = ""
        self.root.current = "details"
        
        # تحميل التوقعات في خيط منفصل
        threading.Thread(target=self.load_horoscope, args=(sign,)).start()
    
    def load_horoscope(self, sign):
        try:
            result = self.horoscope_manager.get_horoscope(sign)
            
            # تحديث واجهة المستخدم في الخيط الرئيسي
            Clock.schedule_once(lambda dt: self.update_horoscope(
                result['date'],
                result['prediction']
            ))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_horoscope(
                self.horoscope_manager.get_arabic_date(),
                "عذراً، حدث خطأ في جلب التوقعات. يرجى المحاولة مرة أخرى."
            ))
    
    def update_horoscope(self, date, text):
        screen = self.root.get_screen("details")
        screen.ids.date_label.text = date
        screen.ids.horoscope_text.text = text
    
    def go_back(self):
        self.root.current = "main"

if __name__ == '__main__':
    Window.softinput_mode = 'below_target'
    HoroscopeApp().run()
