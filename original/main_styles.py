import sys
import os

# ========================================
# تعطيل DPI Scaling (مهم جداً!)
# ========================================
# يجب أن يكون قبل استيراد QApplication
# هذه الأسطر تمنع PyQt6 من تكبير العناصر تلقائياً
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# استيراد صفحة حول من الملف المنفصل
try:
    from Styles.about_page import AboutPageContent
except ImportError:
    from about_page import AboutPageContent

# استيراد صفحة التحكم من الملف المنفصل
try:
    from Styles.control_page import ControlPageContent
except ImportError:
    from control_page import ControlPageContent

# استيراد صفحة الإعدادات من الملف المنفصل
try:
    from Styles.settings_page import SettingsPageContent
except ImportError:
    from settings_page import SettingsPageContent

# استيراد صفحة كشف الشات من الملف المنفصل
try:
    from Styles.chat_page import ChatDetectorContent
except ImportError:
    from chat_page import ChatDetectorContent

# ========================================
# استيراد VERSION من version.py تلقائياً
# ========================================
try:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from version import VERSION
except ImportError:
    VERSION = "1.9"  # قيمة افتراضية

class SidebarTest(QDialog):
    """
    نافذة الإعدادات الجديدة مع Sidebar
    
    يتم استدعاؤها من main.py مع config و overlay
    """
    
    def __init__(self, parent=None, config=None, overlay=None):
        super().__init__(parent)
        
        # مراجع للإعدادات والنافذة الرئيسية
        self.config = config  # ConfigManager من main.py
        self.overlay = overlay  # OverlayWindow للـ apply_settings
        
        # ===== متغيرات الحالة =====
        self.nav_buttons = []  # قائمة أزرار التنقل
        
        # ===== إعدادات النافذة =====
        # بدون إطار (frameless) + يبقى فوق النوافذ الأخرى
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        
        # شفافية الخلفية - مهمة لإخفاء الحواف البيضاء!
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # منع أخذ الـ focus عند الإظهار - مهم للـ fullscreen!
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # حجم النافذة - عدّله حسب الحاجة
        self.resize(500, 500)
        
        # استعادة موقع النافذة من CONFIG
        if self.config:
            saved_x = self.config.get('settings_x')
            saved_y = self.config.get('settings_y')
            if saved_x != -1 and saved_y != -1:
                self.move(saved_x, saved_y)
        
        # الشفافية الآن تُطبق على الخلفية فقط (وليس على كل النافذة)
        # يتم ذلك في apply_style عبر rgba مع settings_opacity
        
        self.setup_ui()
        
        # تطبيق WS_EX_NOACTIVATE لمنع أخذ الـ focus
        self.apply_no_activate()
        
        # تمكين السحب من كل مكان في النافذة
        self._install_drag_filter()
    
    def apply_no_activate(self):
        """تطبيق WS_EX_NOACTIVATE لمنع أخذ الـ focus من اللعبة"""
        import ctypes
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        hwnd = int(self.winId())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)
    
    def _install_drag_filter(self):
        """تثبيت event filter على كل الـ widgets لتمكين السحب"""
        def install_on_children(widget):
            widget.installEventFilter(self)
            for child in widget.findChildren(QWidget):
                child.installEventFilter(self)
        install_on_children(self)
    
    def eventFilter(self, obj, event):
        """Event filter لتمكين السحب من أي widget (مع استثناء العناصر التفاعلية)"""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtWidgets import QSlider, QPushButton
        
        # استثناء الـ sliders من السحب
        if isinstance(obj, QSlider):
            return False
        
        # الأزرار المفعّلة: تسمح بالنقر ولكن أيضاً بالسحب
        if isinstance(obj, QPushButton) and obj.isEnabled():
            # عند الضغط: حفظ موقع السحب
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    self._btn_pressed = True
                    self._btn_dragged = False  # لم يتم السحب بعد
            # عند التحريك: تحريك النافذة إذا تم الضغط
            elif event.type() == QEvent.Type.MouseMove:
                if event.buttons() & Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos') and getattr(self, '_btn_pressed', False):
                    self.move(event.globalPosition().toPoint() - self.drag_pos)
                    self._btn_dragged = True  # تم السحب
            # عند الإفلات: إعادة تعيين ومنع النقر إذا تم السحب
            elif event.type() == QEvent.Type.MouseButtonRelease:
                was_dragged = getattr(self, '_btn_dragged', False)
                self._btn_pressed = False
                self._btn_dragged = False
                if was_dragged:
                    # إعادة تطبيق الستايل لإزالة حالة pressed
                    obj.setDown(False)
                    obj.style().unpolish(obj)
                    obj.style().polish(obj)
                    obj.update()
                    return True  # استهلاك الحدث = منع النقر
            return False
        
        # تجاهل عناصر صفحة التحديد (ChatDetectorContent) - تستخدم سحبها الخاص
        parent = obj
        while parent:
            if parent.__class__.__name__ == 'ChatDetectorContent':
                # هذا العنصر داخل صفحة التحديد - لا نحفظ drag_pos
                # نترك الأحداث تمر للأعلى بشكل طبيعي
                return super().eventFilter(obj, event)
            parent = parent.parent() if hasattr(parent, 'parent') and callable(parent.parent) else None
        
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return False
        elif event.type() == QEvent.Type.MouseMove:
            if event.buttons() & Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
                self.move(event.globalPosition().toPoint() - self.drag_pos)
                return False
        return super().eventFilter(obj, event)
    
    def setup_ui(self):
        """
        بناء واجهة المستخدم
        
        الهيكل:
        - Main Layout (أفقي) → Content (يسار) + Sidebar (يمين)
        """
        
        # ===== Main Layout (أفقي) =====
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)  # هوامش خارجية للظل
        main_layout.setSpacing(0)  # لا مسافة بين Content و Sidebar
        
        # ========================================
        # STACKED WIDGET - للتبديل بين الصفحات
        # ========================================
        # يحتوي على 3 صفحات: التحكم (0)، الإعدادات (1)، حول (2)
        
        # إنشاء class مخصص لمنع التحرك
        class FixedStackedWidget(QStackedWidget):
            def wheelEvent(self, event):
                event.accept()  # منع التمرير
            def mousePressEvent(self, event):
                event.accept()  # منع السحب
            def mouseMoveEvent(self, event):
                event.accept()  # منع التحريك
        
        stacked_widget = FixedStackedWidget()
        self.stacked_widget = stacked_widget  # حفظ المرجع للاستخدام في _set_active_button
        
        # ========================================
        # صفحة 0: التحكم (CONTROL PAGE) - مربوطة من control_page.py
        # ========================================
        control_page = QFrame()
        control_page.setObjectName("ContentFrame")
        
        control_layout = QVBoxLayout(control_page)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(0)
        
        # إضافة محتوى صفحة التحكم من الملف المنفصل
        self.control_content = ControlPageContent(control_page, config=self.config, overlay=self.overlay)
        control_layout.addWidget(self.control_content)
        
        stacked_widget.addWidget(control_page)  # index 0
        
        # ========================================
        # صفحة 1: الإعدادات (SETTINGS PAGE) - مربوطة من settings_page.py
        # ========================================
        settings_page = QFrame()
        settings_page.setObjectName("ContentFrame")
        
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(0)
        
        # إضافة محتوى صفحة الإعدادات من الملف المنفصل
        settings_content = SettingsPageContent(settings_page, config=self.config, overlay=self.overlay)
        
        # تثبيت المحتوى في الأعلى ومنع التحرك
        settings_layout.addWidget(settings_content, 0, Qt.AlignmentFlag.AlignTop)
        
        stacked_widget.addWidget(settings_page)  # index 1
        
        # ========================================
        # صفحة 2: تحديد (DETECT PAGE) - صفحة فارغة
        # ========================================
        detect_page = QFrame()
        detect_page.setObjectName("ContentFrame")
        
        detect_layout = QVBoxLayout(detect_page)
        detect_layout.setContentsMargins(0, 0, 0, 0)
        detect_layout.setSpacing(0)
        
        # إضافة محتوى صفحة كشف الشات من الملف المنفصل
        detect_content = ChatDetectorContent(detect_page, config=self.config)
        detect_layout.addWidget(detect_content)
        
        stacked_widget.addWidget(detect_page)  # index 2
        
        # ========================================
        # صفحة 3: حول (ABOUT PAGE) - مربوطة من about_page.py
        # ========================================
        about_page = QFrame()
        about_page.setObjectName("ContentFrame")
        
        about_layout = QVBoxLayout(about_page)
        about_layout.setContentsMargins(0, 0, 0, 0)
        about_layout.setSpacing(0)
        
        # إضافة محتوى صفحة حول من الملف المنفصل
        about_content = AboutPageContent(about_page)
        about_layout.addWidget(about_content)
        
        stacked_widget.addWidget(about_page)  # index 3
        
        # ========================================
        # زر الإغلاق (X) - جديد من الصفر!
        # ========================================
        btn_close = QPushButton("❌", self)
        btn_close.setFixedSize(32, 32)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.close)
        btn_close.move(38, 28)
        
        # Inline stylesheet مباشر
        btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(60, 65, 85, 255);
                color: #ff8080;
                border: 1px solid rgba(255, 100, 100, 0.3);
                border-radius: 18px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 80, 80, 1.0),
                    stop:1 rgba(220, 50, 50, 1.0)
                );
                border: 2px solid #ff5050;
            }}
            QPushButton:pressed {
                background: rgba(180, 40, 40, 1.0);
                border: 2px solid #ff3030;
            }}
        """)
        
        btn_close.raise_()
        self.btn_close = btn_close  # حفظ
        
        # ========================================
        # SIDEBAR (اليمين) - القائمة الجانبية
        # ========================================
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")  # اسم مهم للـ stylesheet
        
        # عرض Sidebar - عدّله هنا!
        # كان 90px - زدته إلى 100px ليطابق الصورة
        sidebar.setFixedWidth(105)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)  # هوامش علوي/سفلي
        sidebar_layout.setSpacing(0)
        
        # =====================================
        # 1. الشعار (Logo) في الأعلى
        # =====================================
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # توسيط
        
        # تحميل الصورة من مجلد Icons
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, '..', 'Icons', 'app_256.png')
        
        if os.path.exists(logo_path):
            # === حجم الشعار - عدّله هنا! ===
            logo_size = 60  # بكسل (60x60)
            
            pixmap = QPixmap(logo_path).scaled(
                logo_size, logo_size,
                Qt.AspectRatioMode.KeepAspectRatio,      # حفظ النسبة
                Qt.TransformationMode.SmoothTransformation  # تنعيم الصورة
            )
            logo_label.setPixmap(pixmap)
        else:
            # إذا الشعار مو موجود - عرض نص
            logo_label.setText("لوحة\nالمفاتيح")
            logo_label.setStyleSheet("""
                color: #ff9a3c;         /* لون برتقالي */
                font-size: 14px;        /* حجم الخط */
                font-weight: bold;      /* خط عريض */
                font-family: 'Segoe UI';  /* نفس خط الشات */
            """)
        
        sidebar_layout.addWidget(logo_label)
        
        # مسافة تحت الشعار
        sidebar_layout.addSpacing(80)  # 25 بكسل
        
        # =====================================
        # 2. أزرار التبويبات (Navigation Buttons)
        # =====================================
        
        # قائمة لتخزين الأزرار - لتتبع الزر النشط
        self.nav_buttons = []
        
        # === زر: التحكم ===
        btn_control = QPushButton("التحكم")
        btn_control.setObjectName("NavButton")
        btn_control.setMinimumHeight(45)  # ارتفاع الزر
        btn_control.setCursor(Qt.CursorShape.PointingHandCursor)  # مؤشر اليد
        btn_control.setProperty("page_index", 0)  # رقم الصفحة (للمستقبل)
        btn_control.clicked.connect(lambda: self._set_active_button(0))  # عند الضغط
        
        self.nav_buttons.append(btn_control)
        sidebar_layout.addWidget(btn_control)
        sidebar_layout.addSpacing(12)  # مسافة بين الأزرار
        
        # === زر: الإعدادات ===
        btn_settings = QPushButton("الإعدادات")
        btn_settings.setObjectName("NavButton")
        btn_settings.setMinimumHeight(45)
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.setProperty("page_index", 1)
        btn_settings.clicked.connect(lambda: self._set_active_button(1))
        
        self.nav_buttons.append(btn_settings)
        sidebar_layout.addWidget(btn_settings)
        sidebar_layout.addSpacing(12)
        
        # === زر: تحديد ===
        btn_detect = QPushButton("تحديد")
        btn_detect.setObjectName("NavButton")
        btn_detect.setMinimumHeight(45)
        btn_detect.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detect.setProperty("page_index", 2)
        btn_detect.clicked.connect(lambda: self._set_active_button(2))
        
        self.nav_buttons.append(btn_detect)
        sidebar_layout.addWidget(btn_detect)
        sidebar_layout.addSpacing(12)
        
        # === زر: حول ===
        btn_about = QPushButton("حول")
        btn_about.setObjectName("NavButton")
        btn_about.setMinimumHeight(45)
        btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_about.setProperty("page_index", 3)
        btn_about.clicked.connect(lambda: self._set_active_button(3))
        
        self.nav_buttons.append(btn_about)
        sidebar_layout.addWidget(btn_about)
        
        # مسافة مرنة - تدفع V1.6 للأسفل
        sidebar_layout.addStretch()
        
        # =====================================
        # 3. رقم الإصدار (Version) في الأسفل
        # =====================================
        version_label = QLabel(f"v{VERSION}")
        version_label.setObjectName("VersionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # توسيط
        
        sidebar_layout.addWidget(version_label)
        
        # ===== إضافة للـ Main Layout =====
        main_layout.addWidget(stacked_widget, 1)  # Stacked Widget يأخذ المساحة المتبقية
        main_layout.addWidget(sidebar)            # Sidebar ثابت (105px)
        
        # تطبيق الألوان والتنسيقات
        self.apply_style()
        
        # === رفع زر X للمقدمة ===
        QTimer.singleShot(200, lambda: self.btn_close.raise_())
        
        # ===== تفعيل أول زر (حول) كـ Default =====
        self._set_active_button(0)  # حول نشط كما في الصورة!
    
    def apply_style(self):
        """
        تطبيق الألوان والحدود والتنسيقات
        
        ملاحظات مهمة:
        - الألوان بنظام #RRGGBB أو rgba(r, g, b, a)
        - القيم بالـ px (pixels)
        - border-radius للزوايا الدائرية
        - settings_opacity يُطبق على الخلفية فقط (النصوص والأزرار تبقى واضحة!)
        """
        
        # قراءة شفافية الإعدادات من CONFIG (أو 255 كقيمة افتراضية)
        opacity = 255
        if self.config:
            opacity = self.config.get('settings_opacity')
        
        self.setStyleSheet(f"""
            /* =====================================
               DIALOG نفسه - الخلفية الشفافة
               ===================================== */
            QDialog {{
                background: transparent;  /* شفاف تماماً - لإخفاء الحواف */
            }}
            
            /* =====================================
               CONTENT (اليسار) - المنطقة الرئيسية
               ===================================== */
            QFrame#ContentFrame {{
                /* === الخلفية - Gradient عمودي مع شفافية من settings_opacity === */
                background: qlineargradient(
                    x1:0, y1:0,    /* نقطة البداية (أعلى) */
                    x2:0, y2:1,    /* نقطة النهاية (أسفل) */
                    stop:0 rgba(30, 36, 54, {opacity}),   /* لون أعلى (داكن أزرق) + شفافية */
                    stop:1 rgba(20, 26, 44, {opacity})    /* لون أسفل (أغمق قليلاً) + شفافية */
                );
                
                /* === الحدود (الإطار الخارجي) === */
                border: 1px solid #4a90e2;  /* أزرق متوسط - يظهر على كل الخلفيات */
                
                /* === الزوايا الدائرية === */
                border-radius: 15px;              /* كل الزوايا 15px */
                border-top-right-radius: 0;       /* الزاوية اليمنى العليا = 0 (لا دائرية) */
                border-bottom-right-radius: 0;    /* الزاوية اليمنى السفلى = 0 */
            }}
            
            /* =====================================
               SIDEBAR (اليمين) - القائمة الجانبية
               ===================================== */
            QWidget#Sidebar {{
                /* === الخلفية - Gradient عمودي (أغمق من Content) + شفافية === */
                background: qlineargradient(
                    x1:0, y1:0,    /* نقطة البداية (أعلى) */
                    x2:0, y2:1,    /* نقطة النهاية (أسفل) */
                    stop:0 rgba(22, 29, 51, {opacity}),   /* لون أعلى (أغمق) + شفافية */
                    stop:1 rgba(11, 16, 40, {opacity})    /* لون أسفل (الأغمق) + شفافية */
                );
                
                /* === الحدود (الإطار الخارجي) === */
                border: 1px solid #4a90e2;  /* أزرق متوسط - نفس Content */
                
                /* === الخط الفاصل (اليسار) === */
                /* هذا الخط يفصل Sidebar عن Content */
                border-left: 0px solid #6bb6ff;  /* أزرق فاتح ساطع - سماكة 1px */
                
                /* === الزوايا الدائرية === */
                border-radius: 15px;             /* كل الزوايا 15px */
                border-top-left-radius: 0;       /* الزاوية اليسرى العليا = 0 */
                border-bottom-left-radius: 0;    /* الزاوية اليسرى السفلى = 0 */
            }}
            
            /* =====================================
               أزرار التبويبات (Navigation Buttons)
               ===================================== */
            QPushButton#NavButton {{
                /* === الألوان === */
                background: transparent;       /* خلفية شفافة (غير نشط) */
                color: #A0D8FF;               /* لون النص (أزرق فاتح) */
                
                /* === الحدود === */
                border: none;                 /* بدون إطار */
                border-radius: 0;             /* بدون زوايا دائرية */
                outline: none;                /* إزالة المربع عند التركيز! */
                
                /* === الخط === */
                font-family: 'Segoe UI';      /* نفس خط الشات! */
                font-size: 20px;              /* حجم الخط */
                font-weight: normal;          /* عادي (مو Bold) */
                
                /* === المحاذاة === */
                text-align: center;           /* نص في المنتصف */
                padding: 10px 5px;            /* هوامش داخلية */
            }}
            
            /* === عند تمرير الماوس (Hover) === */
            QPushButton#NavButton:hover {{
                color: #5A95BF;               /* أغمق قليلاً */
            }}
            
            /* === عند الضغط (Pressed) === */
            QPushButton#NavButton:pressed {{
                color: #48B4FF;               /* أزرق ساطع */
            }}
            
            /* =====================================
               الزر النشط (Active State) - المحدد حالياً
               ===================================== */
            QPushButton#NavButton[active="true"] {{
                /* === الخلفية - Gradient من اليمين لليسار === */
                background: qlineargradient(
                    x1:1, y1:0,    /* البداية: يمين */
                    x2:0, y2:0,    /* النهاية: يسار */
                    stop:0 rgba(74, 144, 226, 0.4),   /* أزرق فاتح (يمين) */
                    stop:1 rgba(74, 144, 226, 0.0)    /* شفاف (يسار) */
                );
                
                /* === لون النص === */
                color: #48B4FF;               /* أزرق ساطع للنص */
                
                /* === الحد الأيمن (Border) === */
                border-right: 3px solid #ff9a3c;  /* خط برتقالي سميك على اليمين */
                
                /* === إزالة focus outline === */
                outline: none;
                border-radius: 0;
                
                /* === رفع النص قليلاً للأعلى === */
                padding: 7px 5px 13px 5px;  /* علوي/يمين/سفلي/يسار - يرفع النص! */
            }}
            
            /* الزر النشط عند Hover - لون أفتح */
            QPushButton#NavButton[active="true"]:hover {{
                color: #A0D8FF;               /* أفتح عند Hover */
            }}
            
            /* =====================================
               رقم الإصدار (Version Label)
               ===================================== */
            QLabel#VersionLabel {{
                /* === الألوان === */
                color: #ff9a3c;               /* برتقالي (مميز!) */
                
                /* === الخط === */
                font-family: 'Segoe UI';      /* نفس خط الشات */
                font-size: 12px;              /* حجم صغير */
                font-weight: bold;            /* عريض */
                
                /* === المحاذاة === */
                padding: 8px 0;               /* مسافة علوي/سفلي */
            }}
            
            /* =====================================
               زر الإغلاق (X) - مثل test3
               ===================================== */
            
            QPushButton#CloseBtn {{
                /* === الخلفية === */
                /* خلفية الزر في الحالة العادية (بدون hover) */
                background: rgba(60, 65, 85, 150);
                /* شرح: rgba(أحمر, أخضر, أزرق, شفافية)
                   - الأرقام الثلاثة الأولى = اللون (0-255)
                   - الرقم الرابع = الشفافية (0=شفاف، 255=صلب)
                   - لتغيير اللون: غيّر الأرقام الثلاثة الأولى
                   - مثال أحمر: rgba(200, 60, 60, 150)
                */
                
                /* === لون النص (رمز X) === */
                color: #ff8080;
                /* شرح: #ff8080 = أحمر فاتح
                   - لتغيير اللون:
                     #ffffff = أبيض
                     #ff0000 = أحمر قوي
                     #4a90e2 = أزرق
                */
                
                /* === حجم الرمز X === */
                font-size: 15px;
                /* شرح: حجم رمز ❌ بالبكسل
                   - لتكبير: 18px أو 20px
                   - لتصغير: 12px أو 14px
                */
                
                /* === سُمك الخط === */
                font-weight: bold;
                /* شرح: عريض
                   - bold = عريض (الحالي)
                   - normal = عادي
                   - lighter = خفيف
                */
                
                /* === نوع الخط === */
                font-family: 'Segoe UI';
                /* شرح: اسم الخط المستخدم
                   - 'Segoe UI' = خط النظام (الحالي)
                   - 'Arial' = Arial
                   - 'Tahoma' = Tahoma
                */
                
                /* === الإطار الخارجي === */
                border: 1px solid rgba(255, 100, 100, 0.3);
                /* شرح: border: [السماكة] [النوع] [اللون]
                   - 1px = سماكة الإطار (جرّب 2px أو 3px)
                   - solid = خط صلب (جرّب dashed للمنقط)
                   - rgba(255, 100, 100, 0.3) = أحمر شفاف
                */
                
                /* === الزوايا الدائرية === */
                border-radius: 18px;
                /* شرح: درجة استدارة الزوايا
                   - 18px = دائري جداً (الحالي)
                   - 4px = مربع تقريباً
                   - 0px = مربع تماماً بدون استدارة
                */
                
                /* === إزالة المربع عند التركيز === */
                outline: none;
                /* شرح: يمنع ظهور مربع أزرق عند الضغط */
            }}
            
            /* === عند تمرير الماوس فوق الزر === */
            QPushButton#CloseBtn:hover {{
                /* الخلفية تتحول لتدرج أحمر  - صلب 100%! */
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 80, 80, 1.0),    /* لون أعلى - صلب! */
                    stop:1 rgba(220, 50, 50, 1.0)     /* لون أسفل - صلب! */
                );
                /* شرح: تدرج عمودي من أعلى لأسفل - بدون شفافية!
                   - stop:0 = اللون في الأعلى
                   - stop:1 = اللون في الأسفل
                   - 1.0 = صلب 100% (كان 0.9/0.85 = شفاف!)
                */
                
                /* الإطار يصير أحمر ساطع */
                border: 2px solid #ff5050;
                /* شرح: إطار أحمر قوي بسماكة 2px */
            }}
            
            /* === عند الضغط على الزر === */
            QPushButton#CloseBtn:pressed {{
                background: rgba(180, 40, 40, 1.0);   /* أحمر داكن صلب */
                border: 2px solid #ff3030;            /* أحمر أغمق */
            }}
            
        """)
    
    # =====================================
    # دالة تبديل الزر النشط
    # =====================================
    
    def _set_active_button(self, index):
        """
        تفعيل زر وتعطيل الباقي + تبديل الصفحة
        
        Parameters:
            index: رقم الزر/الصفحة (0=التحكم, 1=الإعدادات, 2=تحديد, 3=حول)
        
        الآلية:
        - يعطّل كل الأزرار (active="false")
        - يفعّل الزر المحدد (active="true")
        - يبدّل الصفحة في stacked_widget
        - الـ CSS يطبق automatically بناءً على active property
        """
        # === تحديث حالة الأزرار ===
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                # الزر النشط
                btn.setProperty("active", "true")
            else:
                # الأزرار الأخرى
                btn.setProperty("active", "false")
            
            # إعادة تطبيق الـ stylesheet (مهم!)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # === تبديل الصفحة ===
        self.stacked_widget.setCurrentIndex(index)
        
        print(f"[NAV] Active button switched to: {index}")
    
    # =====================================
    # دالة تحديث عرض الموقع (للربط مع main.py)
    # =====================================
    
    def update_loc_display(self):
        """تحديث عرض موقع الكتابة - يُستدعى من main.py بعد حفظ موقع جديد"""
        if hasattr(self, 'control_content') and self.control_content:
            self.control_content.update_loc_display()
    
    # =====================================
    # دوال التحكم بالنافذة (Drag & Close)
    # ====================================="
    
    def mousePressEvent(self, e):
        """
        عند الضغط بالماوس - حفظ الموقع للسحب
        """
        if e.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, e):
        """
        عند تحريك الماوس - سحب النافذة
        """
        if e.buttons() & Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            self.move(e.globalPosition().toPoint() - self.drag_pos)
    
    def mouseReleaseEvent(self, e):
        """
        عند إفلات الماوس - حفظ موقع النافذة
        """
        if e.button() == Qt.MouseButton.LeftButton:
            # حفظ الموقع في CONFIG
            if self.config:
                self.config.set('settings_x', self.x())
                self.config.set('settings_y', self.y())
    
    def keyPressEvent(self, e):
        """
        عند ضغط مفتاح - ESC للإغلاق
        """
        if e.key() == Qt.Key.Key_Escape:
            self.close()


# =====================================
# نقطة الدخول للبرنامج
# =====================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SidebarTest()
    window.show()
    sys.exit(app.exec())


