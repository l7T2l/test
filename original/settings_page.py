import sys
import os

# ========================================
# تعطيل DPI Scaling (مهم!)
# ========================================
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ========================================
# CLASS 1: SettingsPageContent - للربط مع styles.py
# ========================================
# هذا الـ class يحتوي على المحتوى فقط (بدون إعدادات النافذة)
# يُستخدم داخل QStackedWidget في styles.py

class SettingsPageContent(QWidget):
    """محتوى صفحة الإعدادات - للربط مع الإطار الرئيسي"""
    
    def __init__(self, parent=None, config=None, overlay=None):
        super().__init__(parent)
        
        # مراجع للإعدادات والنافذة الرئيسية
        self.config = config  # ConfigManager من main.py
        self.overlay = overlay  # OverlayWindow للـ apply_settings
        
        # ========================================
        # القيم من CONFIG أو الافتراضية
        # ========================================
        if config:
            self.bg_opacity = config.get('bg_opacity')
            self.text_opacity = config.get('text_opacity')
            self.settings_opacity = config.get('settings_opacity')
            self.font_size = config.get('font_size')
            self.first_line_end = config.get('first_line_end')
            self.bg_color = config.get('bg_color')
            self.text_color = config.get('text_color')
        else:
            self.bg_opacity = 200          # شفافية الخلفية
            self.text_opacity = 255        # شفافية النص
            self.settings_opacity = 255    # شفافية الإعدادات
            self.font_size = 20            # حجم الخط
            self.first_line_end = 115      # نهاية السطر الأول
            self.bg_color = "#000000"      # لون الخلفية (أسود)
            self.text_color = "#FFFF00"    # لون النص (أصفر)
        
        self.setup_ui()
        self.apply_style()
        
        # تطبيق ألوان الأزرار من CONFIG
        self.update_color_buttons()
        
    def setup_ui(self):
        """
        بناء واجهة المستخدم
        كل عنصر له اسم فريد (ObjectName) للتحكم المستقل
        """
        
        # === منع التوسع والتحرك ===
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # === التخطيط الرئيسي ===
        main_layout = QVBoxLayout(self)
        
        # المسافات الخارجية (يسار، أعلى، يمين، أسفل) - القيم الأصلية
        main_layout.setContentsMargins(15, 0, 15, 10)
        
        # المسافة بين البطاقات - القيمة الأصلية
        main_layout.setSpacing(15)
        
        # === إضافة مسافة قبل البرواز ===
        main_layout.addSpacing(10)
        
        # === البرواز (Header Frame) ===
        header_frame_settings = QFrame()
        header_frame_settings.setObjectName("HeaderWidget")
        header_frame_settings.setFixedHeight(50)
        
        header_layout_settings = QHBoxLayout(header_frame_settings)
        header_layout_settings.setContentsMargins(15, 10, 15, 10)
        header_layout_settings.setSpacing(0)
        
        header_layout_settings.addStretch()
        
        # === العنوان ===
        title_label_settings = QLabel("الإعدادات")
        title_label_settings.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #a0d8ff,
                stop:1 #ff9a3c);
            font-family: 'Segoe UI';
            font-size: 18px;
            font-weight: bold;
        """)
        
        header_layout_settings.addWidget(title_label_settings)
        
        # === مسافة بين النص والأيقونة ===
        header_layout_settings.addSpacing(8)
        
        # === أيقونة الإعدادات ===
        icon_label_settings = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path_settings = os.path.join(script_dir, '..', 'Icons', 'Settings_panel.png')
        
        if os.path.exists(icon_path_settings):
            icon_size_settings = 24
            
            pixmap_settings = QPixmap(icon_path_settings).scaled(
                icon_size_settings, icon_size_settings,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            icon_label_settings.setPixmap(pixmap_settings)
        
        header_layout_settings.addWidget(icon_label_settings)
        
        main_layout.addWidget(header_frame_settings)
        
        # ========================================
        # قسم الشفافية
        # ========================================
        # مسار الأيقونة: icons/transparency.png
        trans_icon_path = os.path.join(os.path.dirname(__file__), "..", "Icons", "transparency.png")
        
        trans_section = self._create_section_card(
            "الشفافية",           # النص
            "#4a90e2",            # اللون (أزرق)
            "TransparencySection", # الاسم الفريد
            trans_icon_path       # مسار الأيقونة
        )
        trans_layout = trans_section.layout()
        
        # --- مؤشر شفافية الخلفية ---
        self.sl_bg, self.lbl_bg = self._add_slider(
            trans_layout,
            "شفافية الخلفية",    # النص
            2, 255,              # المدى (من-إلى) - يبدأ من 2 لتجنب bug Qt مع القيمة 1
            self.bg_opacity,     # القيمة الافتراضية
            "BgOpacity",         # الاسم الفريد
            'bg_opacity'         # config_key
        )
        
        # --- مؤشر شفافية النص ---
        self.sl_txt, self.lbl_txt = self._add_slider(
            trans_layout,
            "شفافية النص",
            50, 255,
            self.text_opacity,
            "TextOpacity",
            'text_opacity'
        )
        
        # --- مؤشر شفافية الإعدادات ---
        self.sl_set, self.lbl_set = self._add_slider(
            trans_layout,
            "شفافية الإعدادات",
            100, 255,
            self.settings_opacity,
            "SettingsOpacity",
            'settings_opacity'
        )
        
        main_layout.addWidget(trans_section)
        
        # ========================================
        # قسم النص
        # ========================================
        # مسار الأيقونة: icons/text.png
        text_icon_path = os.path.join(os.path.dirname(__file__), "..", "Icons", "text.png")
        
        text_section = self._create_section_card(
            "النص",
            "#9b59b6",          # بنفسجي
            "TextSection",
            text_icon_path       # مسار الأيقونة
        )
        text_layout = text_section.layout()
        
        # --- مؤشر حجم الخط ---
        self.sl_font, self.lbl_font = self._add_slider(
            text_layout,
            "حجم الخط",
            14, 40,
            self.font_size,
            "FontSize",
            'font_size'
        )
        
        # --- مؤشر نهاية السطر ---
        self.sl_line_end, self.lbl_line_end = self._add_slider(
            text_layout,
            "نهاية السطر الأول",
            0, 300,
            self.first_line_end,
            "LineEnd",
            'first_line_end'
        )
        
        main_layout.addWidget(text_section)
        
        # ========================================
        # قسم الألوان
        # ========================================
        # مسار الأيقونة: icons/color.png
        color_icon_path = os.path.join(os.path.dirname(__file__), "..", "Icons", "color.png")
        
        color_section = self._create_section_card(
            "الألوان",
            "#e67e22",          # برتقالي
            "ColorsSection",
            color_icon_path      # مسار الأيقونة
        )
        color_layout = color_section.layout()
        
        # صف الأزرار
        colors_row = QHBoxLayout()
        colors_row.setSpacing(10)  # مسافة بين الزرين
        
        # --- زر لون الخلفية ---
        self.btn_bg = self._create_color_button(
            "لون الخلفية",
            self.bg_color,
            "BackgroundColor"  # الاسم الفريد
        )
        # ربط الزر بفتح Color Picker
        self.btn_bg.clicked.connect(lambda: self.pick_color('bg'))
        
        # --- زر لون النص ---
        self.btn_txt = self._create_color_button(
            "لون النص",
            self.text_color,
            "TextColor"       # الاسم الفريد
        )
        # ربط الزر بفتح Color Picker
        self.btn_txt.clicked.connect(lambda: self.pick_color('txt'))
        
        colors_row.addWidget(self.btn_bg)
        colors_row.addWidget(self.btn_txt)
        color_layout.addLayout(colors_row)
        
        main_layout.addWidget(color_section)
    
    def wheelEvent(self, event):
        """تعطيل التمرير بالماوس فقط - السحب يعمل من main_styles"""
        event.accept()  # قبول الحدث ومنع انتشاره
        
    def _create_section_card(self, title, accent_color, object_name, icon_path=None):
        """
        إنشاء بطاقة قسم مع تحكم مستقل
        
        Parameters:
            title: نص العنوان
            accent_color: لون العنوان
            object_name: الاسم الفريد (مثل TransparencySection)
            icon_path: مسار الأيقونة (اختياري)
        
        Returns:
            card: البطاقة الجاهزة
        """
        # === البطاقة الرئيسية ===
        card = QWidget()
        card.setObjectName(f"{object_name}Card")  # مثل: TransparencySectionCard
        
        card_layout = QVBoxLayout(card)
        
        # === مسافات داخلية ===
        # (يسار، أعلى، يمين، أسفل)
        card_layout.setContentsMargins(12, 10, 12, 10)
        
        # === مسافة بين العنوان والمحتوى ===
        card_layout.setSpacing(11)
        
        # === حاوية العنوان ===
        # نستخدم HBoxLayout لدفع العنوان لليمين
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        # مساحة فارغة على اليسار - تدفع العنوان والأيقونة لليمين
        title_layout.addStretch()
        
        # === العنوان أولاً ===
        title_label = QLabel(title)
        title_label.setObjectName(f"{object_name}Title")  # مثل: TransparencySectionTitle
        # الخط يأتي من الـ stylesheet ✅
        title_label.setStyleSheet(f"color: {accent_color};")  #  اللون فقط هنا
        title_layout.addWidget(title_label)
        
        # === الأيقونة بعد العنوان (إن وجدت) ===
        if icon_path and os.path.exists(icon_path):
            # مسافة صغيرة بين العنوان والأيقونة (5px)
            title_layout.addSpacing(5)
            
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            # تصغير الأيقونة لـ 18×18 بكسل
            scaled_pixmap = pixmap.scaled(
                24, 24,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(scaled_pixmap)
            icon_label.setFixedSize(24, 24)
            title_layout.addWidget(icon_label)
        
        card_layout.addWidget(title_container)
        
        return card
        
    def _add_slider(self, parent_layout, label_text, min_val, max_val, default_val, object_name, config_key=None):
        """
        إنشاء مؤشر مع تحكم مستقل
        
        Parameters:
            parent_layout: التخطيط الأب
            label_text: النص (مثل "شفافية الخلفية")
            min_val: القيمة الدنيا
            max_val: القيمة القصوى
            default_val: القيمة الافتراضية
            object_name: الاسم الفريد (مثل BgOpacity)
            config_key: مفتاح الحفظ في CONFIG (مثل 'bg_opacity')
        
        Returns:
            (slider, value_label): المؤشر ومربع القيمة
        """
        # === الحاوية ===
        container = QWidget()
        l = QHBoxLayout(container)
        
        # === مسافات داخلية ===
        l.setContentsMargins(0, 4, 0, 4)
        
        # === مسافة بين العناصر ===
        l.setSpacing(8)
        
        # ========== مربع القيمة (الأرقام الزرقاء) ==========
        val_lbl = QLabel(str(default_val))
        val_lbl.setObjectName(f"{object_name}Value")
        val_lbl.setFixedSize(35, 24)
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # ========== المؤشر ==========
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setObjectName(f"{object_name}Slider")
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        slider.setInvertedAppearance(True)
        slider.setFixedHeight(22)
        
        # === التحكم في خطوة التحريك ===
        slider.setSingleStep(1)
        slider.setPageStep(1)
        
        # ========== التسمية (النص) ==========
        lbl = QLabel(label_text)
        lbl.setObjectName(f"{object_name}Label")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # === تحديث القيمة عند التحريك + حفظ في CONFIG ===
        def on_value_changed(val):
            val_lbl.setText(str(val))
            if self.config and config_key:
                self.config.set(config_key, val)
            # تطبيق شفافية الإعدادات على خلفية النافذة فقط (النصوص تبقى واضحة!)
            if config_key == 'settings_opacity':
                # الحصول على نافذة SidebarTest الأب
                settings_dialog = self.window()
                if settings_dialog and hasattr(settings_dialog, 'apply_style'):
                    # إعادة تطبيق الستايل مع الشفافية الجديدة
                    settings_dialog.apply_style()
            # تطبيق الإعدادات الأخرى على OverlayWindow
            if self.overlay and hasattr(self.overlay, 'apply_settings'):
                self.overlay.apply_settings()
        
        slider.valueChanged.connect(on_value_changed)
        
        # === ترتيب العناصر: قيمة | مؤشر | نص ===
        l.addWidget(val_lbl, 0)
        l.addWidget(slider, 1)
        l.addWidget(lbl, 0)
        
        parent_layout.addWidget(container)
        
        return slider, val_lbl
        
    def _create_color_button(self, text, color, object_name):
        """
        إنشاء زر لون مع تحكم مستقل
        
        Parameters:
            text: النص (مثل "لون الخلفية")
            color: اللون الافتراضي
            object_name: الاسم الفريد (مثل BackgroundColor)
        
        Returns:
            btn: الزر الجاهز
        """
        btn = QPushButton(text)
        btn.setObjectName(f"{object_name}Button")  # مثل: BackgroundColorButton
        
        # === ارتفاع الزر ===
        # يتم التحكم فيه من الـ stylesheet ✅
        
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # الخط يأتي من الـ stylesheet ✅
        # اللون يأتي من الـ stylesheet ✅
        # الحجم يأتي من الـ stylesheet ✅
        
        return btn
    
    def update_color_buttons(self):
        """
        تحديث ألوان أزرار اللون من القيم المحفوظة
        يُستدعى عند إنشاء الصفحة وبعد تغيير اللون
        """
        # تطبيق لون الخلفية على الزر
        bg = self.bg_color
        txt_color = self.get_contrasting_text_color(bg)
        border_color = self.get_border_color(bg)
        
        self.btn_bg.setStyleSheet(f"""
            QPushButton#BackgroundColorButton {{
                background: {bg};
                color: {txt_color};
                border: 2px solid {border_color};
                border-radius: 10px;
                min-height: 25px;
                padding: 8px 16px;
                font-family: 'Segoe UI';
                font-size: 18px;
            }}
            QPushButton#BackgroundColorButton:hover {{
                border: 2px solid {self.get_hover_border_color(bg)};
            }}
        """)
        
        # تطبيق لون النص على الزر
        txt = self.text_color
        txt_txt_color = self.get_contrasting_text_color(txt)
        txt_border_color = self.get_border_color(txt)
        
        self.btn_txt.setStyleSheet(f"""
            QPushButton#TextColorButton {{
                background: {txt};
                color: {txt_txt_color};
                border: 2px solid {txt_border_color};
                border-radius: 10px;
                min-height: 25px;
                padding: 8px 16px;
                font-family: 'Segoe UI';
                font-size: 18px;
            }}
            QPushButton#TextColorButton:hover {{
                border: 2px solid {self.get_hover_border_color(txt)};
            }}
        """)
    
    # ========================================
    # دوال مساعدة للألوان الذكية
    # ========================================
    
    def get_luminance(self, hex_color):
        """
        حساب سطوع اللون (luminance)
        
        يستخدم لتحديد إذا كان اللون فاتح أو غامق
        
        Parameters:
            hex_color: اللون بصيغة #RRGGBB
        
        Returns:
            float: قيمة السطوع (0.0 = أسود، 1.0 = أبيض)
        """
        # إزالة # إن وجدت
        hex_color = hex_color.lstrip('#')
        
        # تحويل من Hex إلى RGB
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        # حساب السطوع حسب معادلة W3C
        # الأخضر له تأثير أكبر على السطوع من الأحمر والأزرق
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        
        return luminance
    
    def get_contrasting_text_color(self, bg_color):
        """
        اختيار لون النص المناسب (أبيض أو أسود) حسب لون الخلفية
        
        Parameters:
            bg_color: لون الخلفية #RRGGBB
        
        Returns:
            str: "#ffffff" (أبيض) أو "#000000" (أسود)
        """
        luminance = self.get_luminance(bg_color)
        
        # إذا كان اللون فاتح → نص أسود
        # إذا كان اللون غامق → نص أبيض
        # الحد الفاصل: 0.5
        if luminance > 0.5:
            return "#000000"  # نص أسود للخلفيات الفاتحة
        else:
            return "#ffffff"  # نص أبيض للخلفيات الغامقة
    
    def get_border_color(self, base_color):
        """
        توليد لون الإطار من اللون الأساسي
        
        - إذا كان اللون فاتح → إطار أغمق
        - إذا كان اللون غامق → إطار أفتح
        
        Parameters:
            base_color: اللون الأساسي #RRGGBB
        
        Returns:
            str: لون الإطار #RRGGBB
        """
        luminance = self.get_luminance(base_color)
        
        # إزالة #
        hex_color = base_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        if luminance > 0.5:
            # لون فاتح → إطار أغمق (تقليل 30%)
            factor = 0.7
        else:
            # لون غامق → إطار أفتح (زيادة 30%)
            factor = 1.3
        
        # تطبيق العامل
        r = int(min(255, max(0, r * factor)))
        g = int(min(255, max(0, g * factor)))
        b = int(min(255, max(0, b * factor)))
        
        return f"#{r:02X}{g:02X}{b:02X}"
    
    def get_hover_border_color(self, base_color):
        """
        توليد لون الإطار عند التمرير (أكثر سطوعاً/غمقاناً)
        
        Parameters:
            base_color: اللون الأساسي #RRGGBB
        
        Returns:
            str: لون الإطار عند التمرير #RRGGBB
        """
        luminance = self.get_luminance(base_color)
        
        hex_color = base_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        if luminance > 0.5:
            # لون فاتح → hover أغمق أكثر (تقليل 50%)
            factor = 0.5
        else:
            # لون غامق → hover أفتح أكثر (زيادة 50%)
            factor = 1.5
        
        r = int(min(255, max(0, r * factor)))
        g = int(min(255, max(0, g * factor)))
        b = int(min(255, max(0, b * factor)))
        
        return f"#{r:02X}{g:02X}{b:02X}"
    
    # ========================================
    # دالة Color Picker المخصص
    # ========================================
    
    def pick_color(self, target):
        """
        فتح Color Picker مخصص فوق الزر
        
        Parameters:
            target: 'bg' لزر الخلفية، 'txt' لزر النص
        """
        # إغلاق picker سابق إن موجود
        if hasattr(self, '_color_picker') and self._color_picker:
            self._color_picker.close()
            self._color_picker = None
        
        # === إنشاء نافذة Color Picker ===
        picker = QFrame(self)
        picker.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        picker.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        picker.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # منع أخذ الـ focus
        self._color_picker = picker
        
        # === إغلاق عند النقر خارج الـ picker ===
        from PyQt6.QtCore import QTimer
        import win32api
        
        def check_click_outside():
            if not hasattr(self, '_color_picker') or not self._color_picker:
                return
            # فحص إذا تم الضغط على زر الماوس الأيسر
            if win32api.GetAsyncKeyState(0x01) & 0x8000:  # VK_LBUTTON
                cursor_pos = QCursor.pos()
                picker_rect = self._color_picker.geometry()
                if not picker_rect.contains(cursor_pos):
                    self._color_picker.close()
                    self._color_picker = None
        
        click_timer = QTimer(picker)
        click_timer.timeout.connect(check_click_outside)
        click_timer.start(100)  # فحص كل 100ms
        
        # === الحاوية بحدود مرئية ===
        container = QFrame(picker)
        container.setObjectName("ColorContainer")
        container.setStyleSheet("""
            QFrame#ColorContainer {
                background-color: rgba(30, 30, 30, 255);
                border-radius: 8px;
                border: 2px solid #888;
            }
        """)
        
        picker_layout = QVBoxLayout(picker)
        picker_layout.setContentsMargins(0, 0, 0, 0)
        picker_layout.addWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(4)
        
        # === دالة عند اختيار لون ===
        def on_color_click(color):
            picker.close()
            self._color_picker = None
            
            # حفظ اللون
            if target == 'bg':
                self.bg_color = color
                if self.config:
                    self.config.set('bg_color', color)
                btn = self.btn_bg
                btn_name = "BackgroundColorButton"
            else:  # txt
                self.text_color = color
                if self.config:
                    self.config.set('text_color', color)
                btn = self.btn_txt
                btn_name = "TextColorButton"
            
            # استدعاء apply_settings لتحديث الواجهة الرئيسية
            if self.overlay and hasattr(self.overlay, 'apply_settings'):
                self.overlay.apply_settings()
            
            # === حساب الألوان الذكية تلقائياً ===
            
            # 1️⃣ لون النص - يتكيف مع سطوع/غمقان الخلفية
            text_color = self.get_contrasting_text_color(color)
            # إذا كانت الخلفية فاتحة → نص أسود
            # إذا كانت الخلفية غامقة → نص أبيض
            
            # 2️⃣ لون الإطار - يتكيف مع اللون الأساسي
            border_color = self.get_border_color(color)
            # إذا كانت الخلفية فاتحة → إطار أغمق
            # إذا كانت الخلفية غامقة → إطار أفتح
            
            # 3️⃣ لون الإطار عند التمرير - أكثر وضوحاً
            hover_border = self.get_hover_border_color(color)
            # تتحرك أكثر في نفس الاتجاه (أغمق أو أفتح)
            
            # === تطبيق الألوان على الزر ===
            btn.setStyleSheet(f"""
                QPushButton#{btn_name} {{
                    /* اللون الأساسي */
                    background: {color};  /* اللون المختار */
                    
                    /* لون النص - تلقائي حسب السطوع */
                    color: {text_color};  /* أبيض أو أسود حسب الخلفية */
                    
                    /* لون الإطار - متناسق مع الخلفية */
                    border: 2px solid {border_color};  /* أغمق أو أفتح */
                    
                    /* الشكل والحجم */
                    border-radius: 10px;
                    min-height: 25px;
                    padding: 8px 16px;
                    font-family: 'Segoe UI';
                    font-size: 18px;
                    font-weight: normal;
                }}
                QPushButton#{btn_name}:hover {{
                    /* الإطار عند التمرير - أكثر وضوحاً */
                    border: 2px solid {hover_border};
                }}
            """)
            
            print(f"✓ اللون المختار: {color}")
            print(f"  → لون النص: {text_color}")
            print(f"  → لون الإطار: {border_color}")
            print(f"  → إطار التمرير: {hover_border}")
        
        # === شبكة 48 لون (6 صفوف × 8 أعمدة) ===
        basic_colors = [
            # Row 1: Reds/Pinks
            "#FF8080", "#FF0000", "#803333", "#FF0066", "#FF00FF", "#FF80FF", "#CC00CC", "#800080",
            # Row 2: Oranges/Yellows
            "#FFCC80", "#FF8000", "#804000", "#FF6600", "#FFFF00", "#FFFF80", "#CCCC00", "#808000",
            # Row 3: Greens
            "#80FF80", "#00FF00", "#008000", "#00FF66", "#00FFCC", "#80FFCC", "#00CC66", "#006633",
            # Row 4: Cyans/Blues
            "#80FFFF", "#00FFFF", "#008080", "#0066FF", "#0000FF", "#8080FF", "#0000CC", "#000080",
            # Row 5: Purples/Magentas
            "#CC80FF", "#9900FF", "#660099", "#CC00FF", "#FF00CC", "#FF80CC", "#990066", "#660033",
            # Row 6: Grays/Black/White
            "#FFFFFF", "#E0E0E0", "#C0C0C0", "#A0A0A0", "#808080", "#606060", "#404040", "#000000",
        ]
        
        grid = QGridLayout()
        grid.setSpacing(2)
        
        for i, color in enumerate(basic_colors):
            btn = QPushButton()
            btn.setFixedSize(15, 15)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 1px solid rgba(60, 60, 60, 100);
                }}
                QPushButton:hover {{ border: 1px solid white; }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, c=color: on_color_click(c))
            grid.addWidget(btn, i // 8, i % 8)
        
        main_layout.addLayout(grid)
        
        # === الحجم والموقع - فوق الزر ===
        picker.setFixedSize(150, 125)
        
        target_btn = self.btn_txt if target == 'txt' else self.btn_bg
        btn_pos = target_btn.mapToGlobal(QPoint(0, 0))
        # وسط فوق الزر
        picker.move(btn_pos.x() + (target_btn.width() // 2) - 75, btn_pos.y() - 130)
        
        picker.show()
        
        # تطبيق WS_EX_NOACTIVATE لمنع الخروج من fullscreen
        import ctypes
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        hwnd = int(picker.winId())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)
        
    def apply_style(self):
        """
        تطبيق الأنماط
        
        ✅ كل عنصر له stylesheet منفصل
        ✅ تحكم مستقل كامل
        ✅ شروحات مفصلة لكل خاصية
        """
        self.setStyleSheet("""
            /* =====================================
               HEADER WIDGET - برواز الإعدادات
               ===================================== */
            QFrame#HeaderWidget {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:0, y2:1,
                    stop:0 rgba(40, 45, 65, 200),
                    stop:1 rgba(30, 35, 55, 180)
                );
                border: 1px solid rgba(100, 150, 250, 0.2);
                border-radius: 10px;
            }
            
            /* =========================================
               النافذة الرئيسية
               ========================================= */
            QWidget {
                color: #ffffff;
                font-family: 'Segoe UI';
            }
            
            /* =========================================
               بطاقة قسم الشفافية
               ========================================= */
            QWidget#TransparencySectionCard {
                /* الخلفية - تدرج لوني */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 40, 60, 180),   /* اللون العلوي */
                    stop:1 rgba(25, 30, 50, 160));  /* اللون السفلي */
                
                /* الإطار */
                border: 1px solid rgba(100, 150, 250, 0.25);
                
                /* الزوايا */
                border-radius: 10px;  /* 10px = دائرية الزوايا */
            }
            
            /* === عنوان قسم الشفافية === */
            QLabel#TransparencySectionTitle {
                /* اللون يأتي من الكود (setStyleSheet) */
                
                /* ===== نوع الخط (font-family) ===== */
                font-family: 'Segoe UI';  /* سيغوي يو آي */
                /* لتغيير الخط: 'Arial', 'Tahoma', 'Calibri' */
                
                /* ===== حجم الخط (font-size) ===== */
                font-size: 18px;
                
                /* ===== سُمك الخط (font-weight) ===== */
                font-weight: bold;  /* عريض */
                /* بدائل: normal (عادي), 600 (متوسط), 900 (عريض جداً) */
            }
            
            /* =========================================
               بطاقة قسم النص
               ========================================= */
            QWidget#TextSectionCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 40, 60, 180),
                    stop:1 rgba(25, 30, 50, 160));
                border: 1px solid rgba(100, 150, 250, 0.25);
                border-radius: 10px;
            }
            
            /* === عنوان قسم النص === */
            QLabel#TextSectionTitle {
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: bold;
            }
            
            /* =========================================
               بطاقة قسم الألوان
               ========================================= */
            QWidget#ColorsSectionCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 40, 60, 180),
                    stop:1 rgba(25, 30, 50, 160));
                border: 1px solid rgba(100, 150, 250, 0.25);
                border-radius: 10px;
            }
            
            /* === عنوان قسم الألوان === */
            QLabel#ColorsSectionTitle {
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: bold;
            }
            
            /* =========================================
               مربع قيمة شفافية الخلفية
               ========================================= */
            QLabel#BgOpacityValue {
                /* الخلفية */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 120, 180, 0.9),   /* أزرق فاتح */
                    stop:1 rgba(54, 100, 160, 0.8));  /* أزرق غامق */
                
                /* النص */
                color: #d2e2f7;  /* أبيض */
                
                /* الإطار */
                border: 2px solid rgba(100, 150, 250, 0.6);  /* أزرق شفاف */
                border-radius: 6px;  /* زوايا دائرية */
                
                /* ===== الخط ===== */
                font-family: 'Segoe UI';  /* نوع الخط */
                font-size: 14px;          /* حجم الخط - كبّر: 12px, صغّر: 9px */
                font-weight: normal;        /* عريض */
            }
            
            /* === مؤشر شفافية الخلفية === */
            QSlider#BgOpacitySlider::groove:horizontal {
                /* المسار */
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(74, 144, 226, 0.4),   /* أزرق */
                    stop:1 rgba(155, 89, 182, 0.4));  /* بنفسجي */
                height: 6px;          /* سماكة المسار */
                border-radius: 3px;
            }
            
            /* الجزء المملوء (من اليمين) - يوضح التقدم */
            QSlider#BgOpacitySlider::add-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 160, 240, 0.9),   /* أزرق ساطع */
                    stop:1 rgba(155, 89, 182, 0.9));   /* بنفسجي ساطع */
                border-radius: 3px;
            }
            
            QSlider#BgOpacitySlider::handle:horizontal {
                /* المقبض (الدائرة) */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #eef2f7,  /* أبيض فاتح */
                    stop:1 #4a90e2); /* أبيض مزرق */
                border: 2px solid #4a90e2;  /* إطار أزرق */
                width: 14px;   /* عرض المقبض */
                height: 14px;  /* ارتفاع المقبض */
                margin: -5px 0;  /* لرفع المقبض فوق المسار */
                border-radius: 7px;  /* دائري */
            }
            
            QSlider#BgOpacitySlider::handle:horizontal:hover {
                /* عند التمرير */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5ab69,  /* أبيض نقي */
                    stop:1 #d66602);
                border: 2px solid #d66602;  /* أزرق فاتح */
            }
            
            /* === تسمية شفافية الخلفية === */
            QLabel#BgOpacityLabel {
                color: #c0cfe0;           /* أبيض مزرق */
                
                /* ===== الخط ===== */
                font-family: 'Segoe UI';  /* نوع الخط */
                font-size: 17px;          /* حجم الخط - كبّر: 11px, صغّر: 9px */
            }
            
            /* =========================================
               مربع قيمة شفافية النص
               ========================================= */
            QLabel#TextOpacityValue {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 120, 180, 0.9),
                    stop:1 rgba(54, 100, 160, 0.8));
                color: #d2e2f7;
                border: 2px solid rgba(100, 150, 250, 0.6);
                border-radius: 6px;
                
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: normal;
            }
            
            /* === مؤشر شفافية النص === */
            QSlider#TextOpacitySlider::groove:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(74, 144, 226, 0.4),
                    stop:1 rgba(155, 89, 182, 0.4));
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider#TextOpacitySlider::add-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 160, 240, 0.9),
                    stop:1 rgba(155, 89, 182, 0.9));
                border-radius: 3px;
            }
            
            QSlider#TextOpacitySlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #eef2f7,
                    stop:1 #4a90e2);
                border: 2px solid #4a90e2;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            
            QSlider#TextOpacitySlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5ab69,
                    stop:1 #d66602);
                border: 2px solid #d66602;
            }
            
            /* === تسمية شفافية النص === */
            QLabel#TextOpacityLabel {
                color: #c0cfe0;
                font-family: 'Segoe UI';
                font-size: 17px;
            }
            
            /* =========================================
               مربع قيمة شفافية الإعدادات
               ========================================= */
            QLabel#SettingsOpacityValue {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 120, 180, 0.9),
                    stop:1 rgba(54, 100, 160, 0.8));
                color: #d2e2f7;
                border: 2px solid rgba(100, 150, 250, 0.6);
                border-radius: 6px;
                
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: normal;
            }
            
            /* === مؤشر شفافية الإعدادات === */
            QSlider#SettingsOpacitySlider::groove:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(74, 144, 226, 0.4),
                    stop:1 rgba(155, 89, 182, 0.4));
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider#SettingsOpacitySlider::add-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 160, 240, 0.9),
                    stop:1 rgba(155, 89, 182, 0.9));
                border-radius: 3px;
            }
            
            QSlider#SettingsOpacitySlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #eef2f7,
                    stop:1 #4a90e2);
                border: 2px solid #4a90e2;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            
            QSlider#SettingsOpacitySlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5ab69,
                    stop:1 #d66602);
                border: 2px solid #d66602;
            }
            
            /* === تسمية شفافية الإعدادات === */
            QLabel#SettingsOpacityLabel {
                color: #c0cfe0;
                font-family: 'Segoe UI';
                font-size: 17px;
            }
            
            /* =========================================
               مربع قيمة حجم الخط
               ========================================= */
            QLabel#FontSizeValue {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 120, 180, 0.9),
                    stop:1 rgba(54, 100, 160, 0.8));
                color: #d2e2f7;
                border: 2px solid rgba(100, 150, 250, 0.6);
                border-radius: 6px;
                
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: normal;
            }
            
            /* === مؤشر حجم الخط === */
            QSlider#FontSizeSlider::groove:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(74, 144, 226, 0.4),
                    stop:1 rgba(155, 89, 182, 0.4));
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider#FontSizeSlider::add-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 160, 240, 0.9),
                    stop:1 rgba(155, 89, 182, 0.9));
                border-radius: 3px;
            }
            
            QSlider#FontSizeSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #eef2f7,
                    stop:1 #4a90e2);
                border: 2px solid #4a90e2;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            
            QSlider#FontSizeSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5ab69,
                    stop:1 #d66602);
                border: 2px solid #d66602;
            }
            
            /* === تسمية حجم الخط === */
            QLabel#FontSizeLabel {
                color: #c0cfe0;
                font-family: 'Segoe UI';
                font-size: 17px;
            }
            
            /* =========================================
               مربع قيمة نهاية السطر
               ========================================= */
            QLabel#LineEndValue {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 120, 180, 0.9),
                    stop:1 rgba(54, 100, 160, 0.8));
                color: #d2e2f7;
                border: 2px solid rgba(100, 150, 250, 0.6);
                border-radius: 6px;
                
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: normal;
            }
            
            /* === مؤشر نهاية السطر === */
            QSlider#LineEndSlider::groove:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(74, 144, 226, 0.4),
                    stop:1 rgba(155, 89, 182, 0.4));
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider#LineEndSlider::add-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 160, 240, 0.9),
                    stop:1 rgba(155, 89, 182, 0.9));
                border-radius: 3px;
            }
            
            QSlider#LineEndSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #eef2f7,
                    stop:1 #4a90e2);
                border: 2px solid #4a90e2;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            
            QSlider#LineEndSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5ab69,
                    stop:1 #d66602);
                border: 2px solid #d66602;
            }
            
            /* === تسمية نهاية السطر === */
            QLabel#LineEndLabel {
                color: #c0cfe0;
                font-family: 'Segoe UI';
                font-size: 17px;
            }
            
            /* =========================================
               زر لون الخلفية
               ========================================= */
            QPushButton#BackgroundColorButton {
                background: #000000;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 10px;
                min-height: 25px;
                padding: 8px 16px;
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: normal;
            }
            
            QPushButton#BackgroundColorButton:hover {
                border: 2px solid #777777;
            }
            
            /* =========================================
               زر لون النص
               ========================================= */
            QPushButton#TextColorButton {
                background: #FFFF00;
                color: #000000;
                border: 2px solid #d4af37;
                border-radius: 10px;
                min-height: 25px;
                padding: 8px 16px;
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: normal;
            }
            
            QPushButton#TextColorButton:hover {
                border: 2px solid #e5c04a;
            }
        """)


# ========================================
# CLASS 2: SettingsTestWindow - للاختبار المستقل
# ========================================
# هذا الـ class يحتوي على إعدادات النافذة للاختبار
# يُستخدم عند تشغيل settings_page.py مباشرة

class SettingsTestWindow(QWidget):
    """نافذة اختبار صفحة الإعدادات - مستقلة"""
    
    def __init__(self):
        super().__init__()
        
        # خلفية شفافة + بدون إطار + فوق كل النوافذ
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(370, 520)
        
        # إضافة المحتوى
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # استخدام SettingsPageContent للمحتوى
        self.content = SettingsPageContent(self)
        layout.addWidget(self.content)
    
    def mousePressEvent(self, event):
        """حفظ الموقع عند الضغط"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """سحب النافذة"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsTestWindow()
    window.show()
    sys.exit(app.exec())
