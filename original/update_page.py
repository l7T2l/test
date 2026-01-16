import sys
import os
import subprocess
import tempfile
import shutil

# تعطيل DPI Scaling
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

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


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                            إعدادات التخصيص                                  ║
# ║                    غيّر هذه القيم لتعديل مظهر النافذة                        ║
# ╚════════════════════════════════════════════════════════════════════════════╝

# ─────────────────────────────────────────────────────────────────────────────
# 📐 أبعاد النافذة
# ─────────────────────────────────────────────────────────────────────────────
WINDOW_WIDTH = 420          # عرض النافذة (بكسل)
# الارتفاع ديناميكي - يتغير تلقائياً حسب المحتوى

# ─────────────────────────────────────────────────────────────────────────────
# 🖼️ الشعار (Logo)
# ─────────────────────────────────────────────────────────────────────────────
LOGO_SIZE = 90              # حجم الشعار (بكسل) - عرض وارتفاع
LOGO_MIN_HEIGHT = 100       # الحد الأدنى لارتفاع منطقة الشعار

# ─────────────────────────────────────────────────────────────────────────────
# 📝 الخطوط
# ─────────────────────────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"    # نوع الخط (غيّره لـ Arial, Tahoma, etc.)
TITLE_FONT_SIZE = 26        # حجم خط العنوان (26 ليتناسب مع النص العربي)
VERSION_FONT_SIZE = 22      # حجم خط رقم الإصدار
LABEL_FONT_SIZE = 18        # حجم خط العناوين الفرعية
BUTTON_FONT_SIZE = 18       # حجم خط الأزرار
CHANGELOG_FONT_SIZE = 18    # حجم خط نص "ما الجديد"
PROGRESS_FONT_SIZE = 15     # حجم خط شريط التقدم

# ─────────────────────────────────────────────────────────────────────────────
# 🎨 الألوان
# ─────────────────────────────────────────────────────────────────────────────
# ألوان العنوان
TITLE_COLOR = "#A0D8FF"             # لون العنوان (أزرق فاتح)

# ألوان الإصدار
CURRENT_VERSION_COLOR = "#ff9a3c"   # لون الإصدار الحالي (برتقالي)
NEW_VERSION_COLOR = "#58D58D"       # لون الإصدار الجديد (أخضر)
VERSION_TITLE_COLOR = "#8090a8"     # لون عنوان الإصدار (رمادي)
ARROW_COLOR = "#6090c0"             # لون السهم (أزرق)

# ألوان الأزرار
LATER_BTN_COLOR = "#FFDBDB"         # لون نص زر "تحديث لاحقاً" (أحمر فاتح)
UPDATE_BTN_COLOR = "#E8FFF0"        # لون نص زر "التحديث الآن" (أخضر فاتح)
RESTART_BTN_COLOR = "#E8F4FF"       # لون نص زر "إعادة التشغيل" (أزرق فاتح)

# ألوان الحالة
COMPLETE_COLOR = "#58D58D"          # لون رسالة "تم التحديث بنجاح" (أخضر)
PROGRESS_LABEL_COLOR = "#8090a8"    # لون نص التقدم (رمادي)

# ─────────────────────────────────────────────────────────────────────────────
# 📏 المسافات والحواف
# ─────────────────────────────────────────────────────────────────────────────
CONTAINER_MARGIN = 8        # المسافة الخارجية للنافذة (للظل)
CONTENT_PADDING = 25        # المسافة الداخلية للمحتوى
CONTENT_SPACING = 15        # المسافة بين العناصر
BUTTON_HEIGHT = 48          # ارتفاع الأزرار
BUTTON_SPACING = 15         # المسافة بين الأزرار
BORDER_RADIUS = 15          # استدارة حواف النافذة
BUTTON_RADIUS = 14          # استدارة حواف الأزرار
PROGRESS_HEIGHT = 25        # ارتفاع شريط التقدم

# ─────────────────────────────────────────────────────────────────────────────
# 🌐 رابط التحديث
# ─────────────────────────────────────────────────────────────────────────────
VERSION_URL = "https://raw.githubusercontent.com/l7T2l/Smart-Keyboard/refs/heads/main/version.json"
# ملف version.json يجب أن يحتوي على:
# {
#   "version": "2.0",
#   "download_url": "https://github.com/.../Smart-Keyboard-v2.0.zip",
#   "changelog": [
#     "إصلاح مشاكل الكتابة العربية",
#     "تحسين الأداء",
#     "إصلاح أخطاء"
#   ]
# }


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                          CLASS: UpdateDialog                                ║
# ║                            نافذة التحديث                                     ║
# ╚════════════════════════════════════════════════════════════════════════════╝

class UpdateDialog(QDialog):
    """
    نافذة التحديث التلقائي
    
    تعرض:
    - شعار البرنامج
    - عنوان "تحديث جديد متاح"
    - الإصدار الحالي والجديد
    - زرين: تحديث لاحقاً / التحديث الآن
    - شريط تقدم عند التحميل
    - رسالة اكتمال + زر إعادة التشغيل
    
    Attributes:
        config: إعدادات البرنامج (للشفافية)
        current_version: رقم الإصدار الحالي
        new_version: رقم الإصدار الجديد
        download_url: رابط تحميل الإصدار الجديد
        is_downloading: هل التحميل جاري؟
    """
    
    def __init__(self, parent=None, config=None, current_version="1.9", new_version="2.0", download_url="", changelog=None):
        """
        إنشاء نافذة التحديث
        
        Args:
            parent: النافذة الأم (اختياري)
            config: ConfigManager من main.py (للشفافية)
            current_version: الإصدار الحالي المثبت
            new_version: الإصدار الجديد المتاح
            download_url: رابط تحميل الإصدار الجديد
            changelog: قائمة التغييرات (list أو نص)
        """
        super().__init__(parent)
        
        # ─────────────────────────────────────────────────────────────────────
        # المتغيرات الأساسية
        # ─────────────────────────────────────────────────────────────────────
        self.config = config
        self.current_version = current_version
        self.new_version = new_version
        self.download_url = download_url
        self.changelog = changelog if changelog else []  # قائمة التغييرات
        self.is_downloading = False
        self.is_changelog_visible = False  # هل مربع "ما الجديد" ظاهر؟
        
        # ─────────────────────────────────────────────────────────────────────
        # إعدادات النافذة
        # ─────────────────────────────────────────────────────────────────────
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |      # بدون إطار Windows
            Qt.WindowType.WindowStaysOnTopHint |     # تبقى فوق كل النوافذ
            Qt.WindowType.Tool                       # لا تظهر في شريط المهام
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)    # خلفية شفافة
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)    # لا تأخذ التركيز
        
        # عرض ثابت، ارتفاع ديناميكي
        self.setFixedWidth(WINDOW_WIDTH)
        
        # بناء الواجهة
        self.setup_ui()
        self.apply_style()
        
        # متغير السحب
        self.drag_pos = None
        self._btn_pressed = False
        self._btn_dragged = False
        
        # تثبيت eventFilter على كل العناصر للسحب
        self._install_drag_filter()
        
        # ضبط الحجم والموقع
        QTimer.singleShot(10, self._center_and_show)
    
    def _install_drag_filter(self):
        """تثبيت event filter على كل الـ widgets الفرعية"""
        def install_on_children(widget):
            widget.installEventFilter(self)
            for child in widget.findChildren(QWidget):
                child.installEventFilter(self)
        install_on_children(self)
    
    def eventFilter(self, obj, event):
        """Event filter لتمكين السحب من الأزرار"""
        from PyQt6.QtCore import QEvent
        
        # الأزرار: تسمح بالنقر ولكن أيضاً بالسحب
        if isinstance(obj, QPushButton) and obj.isEnabled():
            # عند الضغط: حفظ موقع السحب
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    self._btn_pressed = True
                    self._btn_dragged = False
            # عند التحريك: تحريك النافذة
            elif event.type() == QEvent.Type.MouseMove:
                if event.buttons() & Qt.MouseButton.LeftButton and self.drag_pos and self._btn_pressed:
                    self.move(event.globalPosition().toPoint() - self.drag_pos)
                    self._btn_dragged = True
            # عند الإفلات: منع النقر إذا تم السحب
            elif event.type() == QEvent.Type.MouseButtonRelease:
                was_dragged = self._btn_dragged
                self._btn_pressed = False
                self._btn_dragged = False
                if was_dragged:
                    obj.setDown(False)
                    obj.style().unpolish(obj)
                    obj.style().polish(obj)
                    obj.update()
                    return True  # استهلاك الحدث = منع النقر
            return False
        
        return super().eventFilter(obj, event)
    
    # ─────────────────────────────────────────────────────────────────────────
    # ضبط الحجم
    # ─────────────────────────────────────────────────────────────────────────
    def adjust_size(self):
        """ضبط حجم النافذة ديناميكياً حسب المحتوى المرئي"""
        self.adjustSize()
    
    def _center_and_show(self):
        """تثبيت الارتفاع وتوسيط النافذة - يُستدعى مرة واحدة عند البدء"""
        self.adjustSize()
        self.fixed_height = self.height()  # حفظ الارتفاع
        self.setFixedHeight(self.fixed_height)  # تثبيت الارتفاع
        self._center()
        
        # رفع النافذة للمقدمة بدون سرقة focus
        self.raise_()
        # لا نستخدم activateWindow لأنها تخرج من fullscreen
        print(f"[UPDATE] Dialog shown at ({self.x()}, {self.y()}) size: {self.width()}x{self.height()}")
    
    def showEvent(self, event):
        """تطبيق WS_EX_NOACTIVATE لمنع سرقة focus من fullscreen"""
        super().showEvent(event)
        try:
            import ctypes
            hwnd = int(self.winId())
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            WS_EX_TOPMOST = 0x00000008
            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | WS_EX_NOACTIVATE | WS_EX_TOPMOST)
        except Exception as e:
            print(f"[UPDATE] Error applying WS_EX_NOACTIVATE: {e}")
    
    def _center(self):
        """توسيط النافذة على الشاشة"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = (screen_geo.width() - self.width()) // 2
            y = (screen_geo.height() - self.height()) // 2
            self.move(x, y)
    
    # ─────────────────────────────────────────────────────────────────────────
    # بناء الواجهة
    # ─────────────────────────────────────────────────────────────────────────
    def setup_ui(self):
        """بناء جميع عناصر الواجهة"""
        
        # ═══════════════════════════════════════════════════════════════════
        # الإطار الرئيسي
        # ═══════════════════════════════════════════════════════════════════
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(CONTAINER_MARGIN, CONTAINER_MARGIN, 
                                        CONTAINER_MARGIN, CONTAINER_MARGIN)
        
        # الحاوية الرئيسية (الخلفية الملونة)
        container = QFrame()
        container.setObjectName("UpdateContainer")
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(CONTENT_PADDING, CONTENT_PADDING, 
                                             CONTENT_PADDING, CONTENT_PADDING)
        container_layout.setSpacing(CONTENT_SPACING)
        
        # ═══════════════════════════════════════════════════════════════════
        # 1️⃣ الشعار (Logo) - يختفي عند فتح changelog
        # ═══════════════════════════════════════════════════════════════════
        self.logo_lbl = QLabel()
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_lbl.setMinimumHeight(LOGO_MIN_HEIGHT)
        
        # تحميل صورة الشعار
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(script_dir, '..', 'Icons')
        logo_path = os.path.join(icons_dir, 'app_256.png')
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                LOGO_SIZE, LOGO_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.logo_lbl.setPixmap(pixmap)
        
        container_layout.addWidget(self.logo_lbl)
        
        # ═══════════════════════════════════════════════════════════════════
        # 2️⃣ العنوان - يختفي عند فتح changelog
        # ═══════════════════════════════════════════════════════════════════
        self.title_lbl = QLabel("يتوفر إصدار جديد")
        self.title_lbl.setObjectName("TitleLabel")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        container_layout.addWidget(self.title_lbl)
        
        # ═══════════════════════════════════════════════════════════════════
        # 3️⃣ مربع "ما الجديد" - مخفي مبدئياً (يظهر بدل الشعار والعنوان)
        # ═══════════════════════════════════════════════════════════════════
        self.changelog_container = QFrame()
        self.changelog_container.setObjectName("ChangelogContainer")
        self.changelog_container.setVisible(False)
        self.changelog_container.setMinimumHeight(150)
        
        changelog_layout = QVBoxLayout(self.changelog_container)
        changelog_layout.setContentsMargins(15, 15, 5, 15)
        changelog_layout.setSpacing(8)
        
        # منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setObjectName("ChangelogScroll")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.verticalScrollBar().setSingleStep(4)
        
        # نص التغييرات
        self.changelog_text = QLabel()
        self.changelog_text.setObjectName("ChangelogText")
        self.changelog_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.changelog_text.setWordWrap(True)
        self.changelog_text.setContentsMargins(0, 0, 10, 0)
        
        # عرض الـ changelog كما هو
        if self.changelog:
            if isinstance(self.changelog, list):
                # إذا كان قائمة، اجمعها بأسطر جديدة
                self.changelog_text.setText('\n'.join(self.changelog))
            else:
                # إذا كان نص، اعرضه كما هو
                self.changelog_text.setText(self.changelog)
        
        scroll_area.setWidget(self.changelog_text)
        changelog_layout.addWidget(scroll_area)
        
        container_layout.addWidget(self.changelog_container)
        
        # ═══════════════════════════════════════════════════════════════════
        # 4️⃣ معلومات الإصدار + زر Open/Close
        # ═══════════════════════════════════════════════════════════════════
        self.version_container = QFrame()
        self.version_container.setObjectName("VersionContainer")
        version_layout = QHBoxLayout(self.version_container)
        version_layout.setContentsMargins(20, 15, 20, 15)
        version_layout.setSpacing(0)
        
        # ──── الإصدار الجديد (يسار) ────
        new_ver_layout = QVBoxLayout()
        new_ver_layout.setSpacing(5)
        
        new_ver_title = QLabel("الإصدار الجديد")
        new_ver_title.setObjectName("VersionTitle")
        new_ver_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.new_ver_value = QLabel(f"v{self.new_version}")
        self.new_ver_value.setObjectName("NewVersionValue")
        self.new_ver_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        new_ver_layout.addWidget(new_ver_title)
        new_ver_layout.addWidget(self.new_ver_value)
        
        # ──── زر Open/Close (وسط - بدل السهم) ────
        self.toggle_btn = QPushButton()
        self.toggle_btn.setObjectName("ToggleButton")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.clicked.connect(self.toggle_changelog)
        
        # تحميل أيقونة open
        open_icon_path = os.path.join(icons_dir, 'open.png')
        if os.path.exists(open_icon_path):
            self.open_icon = QIcon(open_icon_path)
            self.toggle_btn.setIcon(self.open_icon)
            self.toggle_btn.setIconSize(QSize(30, 30))
        
        # تحميل أيقونة close
        close_icon_path = os.path.join(icons_dir, 'close.png')
        if os.path.exists(close_icon_path):
            self.close_icon = QIcon(close_icon_path)
        
        # ──── الإصدار الحالي (يمين) ────
        current_ver_layout = QVBoxLayout()
        current_ver_layout.setSpacing(5)
        
        current_ver_title = QLabel("الإصدار الحالي")
        current_ver_title.setObjectName("VersionTitle")
        current_ver_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.current_ver_value = QLabel(f"v{self.current_version}")
        self.current_ver_value.setObjectName("CurrentVersionValue")
        self.current_ver_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        current_ver_layout.addWidget(current_ver_title)
        current_ver_layout.addWidget(self.current_ver_value)
        
        # ترتيب: جديد [زر] حالي
        version_layout.addLayout(new_ver_layout)
        version_layout.addWidget(self.toggle_btn)
        version_layout.addLayout(current_ver_layout)
        
        container_layout.addWidget(self.version_container)
        
        # ═══════════════════════════════════════════════════════════════════
        # 4️⃣ شريط التقدم (مخفي مبدئياً)
        # ═══════════════════════════════════════════════════════════════════
        self.progress_container = QWidget()
        self.progress_container.setVisible(False)  # مخفي حتى يبدأ التحميل
        
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 5, 0, 5)
        progress_layout.setSpacing(8)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("UpdateProgressBar")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(PROGRESS_HEIGHT)
        
        # نص التقدم (مثل: جاري التحميل... 50%)
        self.progress_label = QLabel("جاري التحميل...")
        self.progress_label.setObjectName("ProgressLabel")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        
        container_layout.addWidget(self.progress_container)
        
        # ═══════════════════════════════════════════════════════════════════
        # 5️⃣ الأزرار (تحديث لاحقاً / التحديث الآن)
        # ═══════════════════════════════════════════════════════════════════
        self.buttons_container = QWidget()
        buttons_layout = QHBoxLayout(self.buttons_container)
        buttons_layout.setContentsMargins(0, 5, 0, 0)
        buttons_layout.setSpacing(BUTTON_SPACING)
        
        # ──── زر تحديث لاحقاً (أحمر) ────
        self.btn_later = QPushButton("التحديث لاحقاً")
        self.btn_later.setObjectName("LaterButton")
        self.btn_later.setMinimumHeight(BUTTON_HEIGHT)
        self.btn_later.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_later.clicked.connect(self.close)  # يغلق النافذة
        
        # ──── زر التحديث الآن (أخضر) ────
        self.btn_update = QPushButton("التحديث الآن")
        self.btn_update.setObjectName("UpdateButton")
        self.btn_update.setMinimumHeight(BUTTON_HEIGHT)
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.start_update)  # يبدأ التحديث
        
        buttons_layout.addWidget(self.btn_later)
        buttons_layout.addWidget(self.btn_update)
        
        container_layout.addWidget(self.buttons_container)
        
        # ═══════════════════════════════════════════════════════════════════
        # 6️⃣ رسالة الاكتمال (مخفية مبدئياً)
        # ═══════════════════════════════════════════════════════════════════
        self.complete_container = QWidget()
        self.complete_container.setVisible(False)  # مخفية حتى ينتهي التحميل
        
        complete_layout = QVBoxLayout(self.complete_container)
        complete_layout.setContentsMargins(0, 5, 0, 0)
        complete_layout.setSpacing(15)
        
        # نص "تم التحديث بنجاح!"
        self.complete_label = QLabel("تم التحديث بنجاح!")
        self.complete_label.setObjectName("CompleteLabel")
        self.complete_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # زر إعادة التشغيل
        self.btn_restart = QPushButton("إعادة التشغيل")
        self.btn_restart.setObjectName("RestartButton")
        self.btn_restart.setMinimumHeight(BUTTON_HEIGHT)
        self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restart.clicked.connect(self.restart_app)
        
        complete_layout.addWidget(self.complete_label)
        complete_layout.addWidget(self.btn_restart)
        
        container_layout.addWidget(self.complete_container)
        
        # إضافة الحاوية للإطار الرئيسي
        main_layout.addWidget(container)
    
    # ─────────────────────────────────────────────────────────────────────────
    # تبديل عرض/إخفاء "ما الجديد"
    # ─────────────────────────────────────────────────────────────────────────
    def toggle_changelog(self):
        """تبديل عرض/إخفاء مربع ما الجديد"""
        self.is_changelog_visible = not self.is_changelog_visible
        
        if self.is_changelog_visible:
            # فتح - عرض "ما الجديد"
            self.logo_lbl.setVisible(False)
            self.title_lbl.setVisible(False)
            self.changelog_container.setVisible(True)
            if hasattr(self, 'close_icon'):
                self.toggle_btn.setIcon(self.close_icon)
        else:
            # إغلاق - عرض الشعار
            self.logo_lbl.setVisible(True)
            self.title_lbl.setVisible(True)
            self.changelog_container.setVisible(False)
            if hasattr(self, 'open_icon'):
                self.toggle_btn.setIcon(self.open_icon)
    
    # ─────────────────────────────────────────────────────────────────────────
    # تطبيق الألوان والتنسيقات (CSS)
    # ─────────────────────────────────────────────────────────────────────────
    def apply_style(self):
        """تطبيق الألوان والتنسيقات على جميع العناصر"""
        
        # قراءة شفافية الإعدادات من CONFIG
        opacity = 255
        if self.config:
            opacity = self.config.get('settings_opacity')
        
        self.setStyleSheet(f"""
            /* ═══════════════════════════════════════════════════════════════
               الحاوية الرئيسية (الخلفية)
               ═══════════════════════════════════════════════════════════════ */
            QFrame#UpdateContainer {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 36, 54, {opacity}),    /* اللون العلوي */
                    stop:1 rgba(20, 26, 44, {opacity})     /* اللون السفلي */
                );
                border: 1px solid #4a90e2;                  /* لون الحدود */
                border-radius: {BORDER_RADIUS}px;           /* استدارة الحواف */
            }}
            
            /* ═══════════════════════════════════════════════════════════════
               العنوان
               ═══════════════════════════════════════════════════════════════ */
            QLabel#TitleLabel {{
                color: {TITLE_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: {TITLE_FONT_SIZE}px;
                font-weight: normal;
            }}
            
            /* ═══════════════════════════════════════════════════════════════
               حاوية الإصدارات
               ═══════════════════════════════════════════════════════════════ */
            QFrame#VersionContainer {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(40, 46, 64, 180),
                    stop:1 rgba(30, 36, 54, 180)
                );
                border: 1px solid rgba(100, 150, 250, 0.25);
                border-radius: 12px;
            }}
            
            /* عنوان الإصدار (الحالي/الجديد) */
            QLabel#VersionTitle {{
                color: {VERSION_TITLE_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: {LABEL_FONT_SIZE}px;
            }}
            
            /* الإصدار الحالي (برتقالي) */
            QLabel#CurrentVersionValue {{
                color: {CURRENT_VERSION_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: {VERSION_FONT_SIZE}px;
                font-weight: normal;
            }}
            
            /* الإصدار الجديد (أخضر) */
            QLabel#NewVersionValue {{
                color: {NEW_VERSION_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: {VERSION_FONT_SIZE}px;
                font-weight: normal;
            }}
            
            /* ═══════════════════════════════════════════════════════════════
               زر Open/Close
               ═══════════════════════════════════════════════════════════════ */
            QPushButton#ToggleButton {{
                background: transparent;
                border: none;
            }}
            QPushButton#ToggleButton:hover {{
                background: rgba(100, 150, 200, 0.2);
                border-radius: 20px;
            }}
            
            /* ═══════════════════════════════════════════════════════════════
               حاوية "ما الجديد"
               ═══════════════════════════════════════════════════════════════ */
            QFrame#ChangelogContainer {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 56, 74, 200),
                    stop:1 rgba(40, 46, 64, 200));
                border: 1px solid rgba(100, 150, 250, 0.2);
                border-radius: 12px;
            }}
            
            /* نص التغييرات */
            QLabel#ChangelogText {{
                color: {VERSION_TITLE_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: {CHANGELOG_FONT_SIZE}px;
                background: transparent;
                padding-right: 0px;
            }}
            
            /* منطقة التمرير */
            QScrollArea#ChangelogScroll {{
                background: transparent;
                border: none;
            }}
            QScrollArea#ChangelogScroll QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin-left: 5px;
            }}
            QScrollArea#ChangelogScroll QScrollBar::handle:vertical {{
                background: rgba(62, 81, 130, 0.8);
                border-radius: 5px;
                min-height: 25px;
            }}
            QScrollArea#ChangelogScroll QScrollBar::add-line:vertical,
            QScrollArea#ChangelogScroll QScrollBar::sub-line:vertical,
            QScrollArea#ChangelogScroll QScrollBar::add-page:vertical,
            QScrollArea#ChangelogScroll QScrollBar::sub-page:vertical {{
                background: transparent;
                height: 0px;
            }}
            
            /* ═══════════════════════════════════════════════════════════════
               زر تحديث لاحقاً (أحمر)
               ═══════════════════════════════════════════════════════════════ */
            QPushButton#LaterButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 0, 0, 0.5),
                    stop:1 rgba(200, 0, 0, 0.5)
                );
                color: {LATER_BTN_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: {BUTTON_FONT_SIZE}px;
                border: 2px solid rgba(200, 0, 0, 1);
                border-radius: {BUTTON_RADIUS}px;
                padding: 10px 20px;
            }}
            QPushButton#LaterButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 0, 0, 0.7),
                    stop:1 rgba(200, 0, 0, 0.7)
                );
                border: 2px solid rgba(200, 0, 0, 1);
            }}
            
            /* ═══════════════════════════════════════════════════════════════
               زر التحديث الآن (أخضر)
               ═══════════════════════════════════════════════════════════════ */
            QPushButton#UpdateButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(2, 247, 106, 0.5),
                    stop:1 rgba(2, 247, 106, 0.5)
                );
                color: {UPDATE_BTN_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: {BUTTON_FONT_SIZE}px;
                border: 2px solid rgba(2, 247, 106, 1);
                border-radius: {BUTTON_RADIUS}px;
                padding: 10px 20px;
            }}
            QPushButton#UpdateButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(2, 247, 106, 0.7),
                    stop:1 rgba(2, 247, 106, 0.7)
                );
                border: 2px solid rgba(2, 247, 106, 1);
            }}
            
            /* ═══════════════════════════════════════════════════════════════
               شريط التقدم
               ═══════════════════════════════════════════════════════════════ */
            QProgressBar#UpdateProgressBar {{
                background: rgba(40, 46, 64, 180);
                border: 1px solid rgba(100, 150, 250, 0.3);
                border-radius: 12px;
                text-align: center;
                color: #A0D8FF;
                font-family: '{FONT_FAMILY}';
                font-size: {PROGRESS_FONT_SIZE}px;
            }}
            /* الجزء الممتلئ من شريط التقدم */
            QProgressBar#UpdateProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(46, 204, 113, 0.9),    /* أخضر */
                    stop:1 rgba(52, 152, 219, 0.9)     /* أزرق */
                );
                border-radius: 10px;
            }}
            
            /* نص التقدم */
            QLabel#ProgressLabel {{
                color: {PROGRESS_LABEL_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: 14px;
            }}
            
            /* ═══════════════════════════════════════════════════════════════
               رسالة الاكتمال
               ═══════════════════════════════════════════════════════════════ */
            QLabel#CompleteLabel {{
                color: {COMPLETE_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: {BUTTON_FONT_SIZE}px;
                font-weight: normal;
            }}
            
            /* ═══════════════════════════════════════════════════════════════
               زر إعادة التشغيل (أزرق)
               ═══════════════════════════════════════════════════════════════ */
            QPushButton#RestartButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(52, 152, 219, 0.7),
                    stop:1 rgba(41, 128, 185, 0.7)
                );
                color: {RESTART_BTN_COLOR};
                font-family: '{FONT_FAMILY}';
                font-size: {BUTTON_FONT_SIZE}px;
                border: 2px solid rgba(52, 152, 219, 0.8);
                border-radius: {BUTTON_RADIUS}px;
                padding: 10px 20px;
            }}
            QPushButton#RestartButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(52, 152, 219, 0.9),
                    stop:1 rgba(41, 128, 185, 0.9)
                );
                border: 2px solid rgba(100, 180, 240, 1);
            }}
        """)
    
    # ─────────────────────────────────────────────────────────────────────────
    # بدء التحديث
    # ─────────────────────────────────────────────────────────────────────────
    def start_update(self):
        """
        بدء عملية التحديث الحقيقية
        
        يقوم بـ:
        1. إخفاء الأزرار
        2. عرض شريط التقدم
        3. تحميل الملف الجديد من download_url
        """
        self.is_downloading = True
        
        # إخفاء الأزرار وعرض شريط التقدم
        self.buttons_container.setVisible(False)
        self.progress_container.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("جاري بدء التحميل...")
        
        # ضبط حجم النافذة
        QTimer.singleShot(10, self.adjust_size)
        
        # بدء التحميل الحقيقي
        self._start_download()
    
    def _start_download(self):
        """بدء تحميل الملف الجديد"""
        if not self.download_url:
            self.progress_label.setText("خطأ: رابط التحميل غير متوفر")
            return
        
        # إنشاء Network Manager
        self.network_manager = QNetworkAccessManager()
        
        # إنشاء الطلب
        request = QNetworkRequest(QUrl(self.download_url))
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,
                           QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy)
        
        # بدء التحميل
        self.reply = self.network_manager.get(request)
        
        # ربط إشارات التقدم
        self.reply.downloadProgress.connect(self._on_download_progress)
        self.reply.finished.connect(self._on_download_finished)
        self.reply.errorOccurred.connect(self._on_download_error)
        
        self.progress_label.setText("جاري التحميل...")
    
    def _on_download_progress(self, bytes_received, bytes_total):
        """تحديث شريط التقدم"""
        if bytes_total > 0:
            percent = int((bytes_received / bytes_total) * 100)
            self.progress_bar.setValue(percent)
            
            # حساب الحجم بـ MB
            received_mb = bytes_received / (1024 * 1024)
            total_mb = bytes_total / (1024 * 1024)
            self.progress_label.setText(f"جاري التحميل... {percent}% ({received_mb:.1f}/{total_mb:.1f} MB)")
    
    def _on_download_error(self, error):
        """عند حدوث خطأ في التحميل"""
        self.is_downloading = False
        self.progress_label.setText(f"خطأ في التحميل: {error}")
        
        # إظهار الأزرار مرة أخرى
        QTimer.singleShot(2000, lambda: self._show_buttons_again())
    
    def _show_buttons_again(self):
        """إظهار الأزرار بعد الخطأ"""
        self.progress_container.setVisible(False)
        self.buttons_container.setVisible(True)
        QTimer.singleShot(10, self.adjust_size)
    
    def _on_download_finished(self):
        """عند اكتمال التحميل"""
        if self.reply.error() != QNetworkReply.NetworkError.NoError:
            return  # تم التعامل مع الخطأ في _on_download_error
        
        # قراءة البيانات
        data = self.reply.readAll()
        print(f"[UPDATE] Downloaded {len(data)} bytes")
        
        # الحصول على مسار exe المحفوظ في الإعدادات
        current_exe = ""
        if self.config:
            current_exe = self.config.get('exe_path')
            print(f"[UPDATE] Config exe_path: {current_exe}")
        
        # إذا لم يكن هناك مسار محفوظ، استخدام Downloads كاحتياط
        if not current_exe or not os.path.exists(os.path.dirname(current_exe)):
            downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            current_exe = os.path.join(downloads_dir, "Smart Keyboard.exe")
            print(f"[UPDATE] No saved path, using Downloads: {current_exe}")
        
        # تحديد مجلد البرنامج
        self.target_dir = os.path.dirname(current_exe)
        self.exe_name = os.path.basename(current_exe)
        
        # حفظ ملف ZIP
        zip_path = os.path.join(self.target_dir, "update.zip")
        
        print(f"[UPDATE] Target dir: {self.target_dir}")
        print(f"[UPDATE] EXE name: {self.exe_name}")
        print(f"[UPDATE] ZIP path: {zip_path}")
        
        try:
            with open(zip_path, 'wb') as f:
                f.write(data.data())
            
            print(f"[UPDATE] Saved ZIP to: {zip_path}")
            
            # حفظ المسارات للاستخدام عند إعادة التشغيل
            self.zip_path = zip_path
            self.current_exe_path = current_exe
            
            # بدء عملية التثبيت (فك الضغط)
            self._start_installation()
            
        except Exception as e:
            print(f"[UPDATE] Error saving file: {e}")
            self.progress_label.setText(f"خطأ في الحفظ: {str(e)}")
            self._show_buttons_again()
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # عملية التثبيت (فك الضغط)
    # ─────────────────────────────────────────────────────────────────────────
    def _start_installation(self):
        """بدء عملية التثبيت - فك ضغط ZIP"""
        print("[UPDATE] Starting installation...")
        
        # تغيير النص والشريط لوضع التثبيت
        self.progress_label.setText("جاري التثبيت...")
        self.progress_bar.setRange(0, 0)  # شريط متحرك (indeterminate)
        
        # تأخير بسيط ثم فك الضغط
        QTimer.singleShot(500, self._extract_zip)
    
    def _extract_zip(self):
        """فك ضغط ZIP"""
        import zipfile
        
        try:
            print(f"[UPDATE] Extracting ZIP: {self.zip_path}")
            
            # تحديد مجلد الفك المؤقت
            self.extract_dir = os.path.join(self.target_dir, "_update_temp")
            
            # حذف المجلد المؤقت إذا كان موجوداً
            if os.path.exists(self.extract_dir):
                shutil.rmtree(self.extract_dir)
            os.makedirs(self.extract_dir)
            
            # فك الضغط
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_dir)
            
            print(f"[UPDATE] Extracted to: {self.extract_dir}")
            
            # إعادة الشريط للوضع العادي
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            
            # إظهار رسالة النجاح
            self.on_download_complete()
            
        except Exception as e:
            print(f"[UPDATE] Error extracting ZIP: {e}")
            self.progress_label.setText(f"خطأ في التثبيت: {str(e)}")
            self.progress_bar.setRange(0, 100)
            self._show_buttons_again()
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # اكتمال التحميل
    # ─────────────────────────────────────────────────────────────────────────
    def on_download_complete(self):
        """
        عند اكتمال التحميل والتثبيت
        
        يقوم بـ:
        1. إخفاء شريط التقدم
        2. إخفاء معلومات الإصدار
        3. عرض رسالة النجاح وزر إعادة التشغيل
        4. تشغيل تأثير الوميض على رسالة النجاح
        """
        self.is_downloading = False
        
        # إخفاء شريط التقدم والإصدارات
        self.progress_container.setVisible(False)
        self.version_container.setVisible(False)
        
        # عرض رسالة الاكتمال
        self.complete_container.setVisible(True)
        
        # تشغيل تأثير الوميض
        self._start_blink_animation()
        
        # ضبط حجم النافذة
        QTimer.singleShot(10, self.adjust_size)
    
    # ─────────────────────────────────────────────────────────────────────────
    # تأثير الوميض
    # ─────────────────────────────────────────────────────────────────────────
    def _start_blink_animation(self):
        """
        تشغيل تأثير الوميض على رسالة "تم التحديث بنجاح!"
        
        يتناوب بين الظهور والاختفاء بدون توقف
        """
        self.blink_timer = QTimer()
        self.blink_visible = True
        
        def toggle_visibility():
            self.blink_visible = not self.blink_visible
            
            # تغيير الشفافية (ظاهر/مخفي)
            if self.blink_visible:
                self.complete_label.setStyleSheet(f"""
                    color: {COMPLETE_COLOR};
                    font-family: '{FONT_FAMILY}';
                    font-size: {BUTTON_FONT_SIZE}px;
                    font-weight: normal;
                """)
            else:
                self.complete_label.setStyleSheet(f"""
                    color: rgba(88, 213, 141, 0.3);
                    font-family: '{FONT_FAMILY}';
                    font-size: {BUTTON_FONT_SIZE}px;
                    font-weight: normal;
                """)
        
        self.blink_timer.timeout.connect(toggle_visibility)
        self.blink_timer.start(400)  # 400ms لكل تبديل
    
    # ─────────────────────────────────────────────────────────────────────────
    # إعادة التشغيل
    # ─────────────────────────────────────────────────────────────────────────
    def restart_app(self):
        """
        إعادة تشغيل التطبيق بعد التحديث
        
        يقوم بـ:
        1. تشغيل PowerShell script لنسخ الملفات
        2. إغلاق التطبيق الحالي
        3. Script ينسخ الملفات ويشغل البرنامج الجديد
        """
        print("[UPDATE] Starting update process...")
        
        # إيقاف الوميض
        if hasattr(self, 'blink_timer'):
            self.blink_timer.stop()
        
        # التحقق من وجود المسارات
        if not hasattr(self, 'extract_dir') or not hasattr(self, 'target_dir'):
            print("[UPDATE] No update files found, just closing...")
            QApplication.quit()
            return
        
        print(f"[UPDATE] Extract dir: {self.extract_dir}")
        print(f"[UPDATE] Target dir: {self.target_dir}")
        print(f"[UPDATE] EXE name: {self.exe_name}")
        
        # البحث عن المجلد المستخرج (قد يكون داخل مجلد فرعي)
        source_dir = self.extract_dir
        extracted_items = os.listdir(self.extract_dir)
        if len(extracted_items) == 1:
            possible_dir = os.path.join(self.extract_dir, extracted_items[0])
            if os.path.isdir(possible_dir):
                source_dir = possible_dir
        
        print(f"[UPDATE] Source dir: {source_dir}")
        
        # إنشاء PowerShell script
        ps_script = f'''
# انتظار إغلاق البرنامج
Start-Sleep -Seconds 2

# نسخ الملفات الجديدة
$source = "{source_dir}"
$target = "{self.target_dir}"
$exe = "{self.exe_name}"

# الملفات المحفوظة (لا تُحذف)
$preserve = @("config.json", "_update_temp", "update.zip")

# حذف الملفات القديمة (ما عدا المحفوظة)
Get-ChildItem -Path $target -Exclude $preserve | ForEach-Object {{
    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
}}

# نسخ الملفات الجديدة
Get-ChildItem -Path $source | ForEach-Object {{
    Copy-Item -Path $_.FullName -Destination $target -Recurse -Force
}}

# تنظيف الملفات المؤقتة
Remove-Item -Path "{self.extract_dir}" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "{self.zip_path}" -Force -ErrorAction SilentlyContinue

# إنشاء ملف علامة نجاح التحديث
$flagFile = Join-Path $target ".update_success"
"{self.new_version}" | Out-File -FilePath $flagFile -Encoding UTF8

# تشغيل البرنامج الجديد
$newExe = Join-Path $target $exe
Start-Process -FilePath $newExe -WorkingDirectory $target
'''
        
        # حفظ السكربت
        script_path = os.path.join(tempfile.gettempdir(), "smart_keyboard_update.ps1")
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(ps_script)
            
            print(f"[UPDATE] Created PowerShell script: {script_path}")
            
            # تشغيل PowerShell بصمت
            subprocess.Popen(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden', '-File', script_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # إغلاق التطبيق
            print("[UPDATE] Closing main application...")
            QApplication.quit()
            
        except Exception as e:
            print(f"[UPDATE] Error launching updater: {e}")
            self.progress_label.setText(f"خطأ في التحديث: {str(e)}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # سحب النافذة
    # ─────────────────────────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        """عند الضغط بالماوس - حفظ موقع السحب"""
        if e.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._dragged = False  # لم يتم السحب بعد
    
    def mouseMoveEvent(self, e):
        """عند تحريك الماوس - سحب النافذة"""
        if e.buttons() & Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(e.globalPosition().toPoint() - self.drag_pos)
            self._dragged = True  # تم السحب
    
    def mouseReleaseEvent(self, e):
        """عند إفلات الماوس - إعادة تعيين حالة السحب"""
        if e.button() == Qt.MouseButton.LeftButton:
            was_dragged = getattr(self, '_dragged', False)
            self._dragged = False
            # إذا تم السحب، أعد تطبيق الستايل على الزر المضغوط
            if was_dragged:
                widget = self.childAt(e.pos())
                if isinstance(widget, QPushButton):
                    widget.setDown(False)
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)
                    widget.update()


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                         دالة التحقق من التحديث                               ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def check_for_updates(parent=None, config=None, silent=False):
    """
    التحقق من وجود تحديث جديد وعرض نافذة التحديث إذا وُجد
    
    Args:
        parent: النافذة الأم (اختياري)
        config: ConfigManager من main.py
        silent: إذا True، لا يعرض رسائل الخطأ
    
    Returns:
        UpdateDialog أو None
    """
    import json
    import urllib.request
    import urllib.error
    
    try:
        # جلب version.json من GitHub
        print(f"[UPDATE] Checking for updates from {VERSION_URL}")
        
        req = urllib.request.Request(
            VERSION_URL,
            headers={'User-Agent': 'Smart-Keyboard-Updater/1.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        new_version = data.get('version', '')
        download_url = data.get('download_url', '')
        changelog = data.get('changelog', '')
        
        print(f"[UPDATE] Current: {VERSION}, Latest: {new_version}")
        
        # مقارنة الإصدارات
        if not new_version or not download_url:
            print("[UPDATE] Invalid version data")
            return None
        
        # تحويل الإصدار لأرقام للمقارنة
        def version_tuple(v):
            return tuple(map(int, v.replace('v', '').split('.')))
        
        try:
            current_tuple = version_tuple(VERSION)
            new_tuple = version_tuple(new_version)
        except ValueError:
            # إذا فشل التحويل، قارن كنصوص
            current_tuple = VERSION
            new_tuple = new_version
        
        if new_tuple > current_tuple:
            print(f"[UPDATE] New version available: {new_version}")
            
            # إنشاء وعرض نافذة التحديث
            dialog = UpdateDialog(
                parent=parent,
                config=config,
                current_version=VERSION,
                new_version=new_version,
                download_url=download_url,
                changelog=changelog  # قائمة التغييرات من version.json
            )
            dialog.show()
            return dialog
        else:
            print("[UPDATE] Already up to date")
            return None
            
    except urllib.error.URLError as e:
        if not silent:
            print(f"[UPDATE] Network error: {e}")
        return None
    except json.JSONDecodeError as e:
        if not silent:
            print(f"[UPDATE] Invalid JSON: {e}")
        return None
    except Exception as e:
        if not silent:
            print(f"[UPDATE] Error checking for updates: {e}")
        return None


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                         نافذة نجاح التحديث                                  ║
# ╚════════════════════════════════════════════════════════════════════════════╝
# ثوابت نافذة النجاح
SUCCESS_WINDOW_WIDTH = 280
SUCCESS_LOGO_SIZE = 80
SUCCESS_TITLE_SIZE = 20
SUCCESS_BTN_SIZE = 16
SUCCESS_BTN_HEIGHT = 48
SUCCESS_PADDING = 25
SUCCESS_BTN_MARGIN = 15


class UpdateSuccessDialog(QDialog):
    """نافذة إعلام المستخدم بنجاح التحديث"""
    
    def __init__(self, new_version="", parent=None):
        super().__init__(parent)
        self.new_version = new_version
        self._drag_pos = None
        
        # قراءة الإعدادات للشفافية
        self.config = None
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
        except:
            pass
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(SUCCESS_WINDOW_WIDTH)
        
        self.setup_ui()
        self.apply_style()
        
        QTimer.singleShot(10, self._center)
    
    def _center(self):
        self.adjustSize()
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # السحب والتحريك
    # ═══════════════════════════════════════════════════════════════════════════
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self._drag_pos = None
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        self.container = QFrame()
        self.container.setObjectName("SuccessContainer")
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(SUCCESS_PADDING, SUCCESS_PADDING, SUCCESS_PADDING, SUCCESS_PADDING)
        container_layout.setSpacing(7)
        
        # الشعار
        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Icons')
        logo_path = os.path.join(icons_dir, 'app_256.png')
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(SUCCESS_LOGO_SIZE, SUCCESS_LOGO_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pixmap)
        
        container_layout.addWidget(logo_lbl)
        
        # العنوان
        title_lbl = QLabel("تم التحديث بنجاح")
        title_lbl.setObjectName("SuccessTitle")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_lbl)
        
        # رسالة الحالة
        status_lbl = QLabel("البرنامج قيد التشغيل")
        status_lbl.setObjectName("SuccessStatus")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(status_lbl)
        
        container_layout.addSpacing(10)
        
        # زر إغلاق
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(SUCCESS_BTN_MARGIN, 0, SUCCESS_BTN_MARGIN, 0)
        
        ok_btn = QPushButton("إغـلاق")
        ok_btn.setObjectName("SuccessButton")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setFixedHeight(SUCCESS_BTN_HEIGHT)
        
        btn_layout.addWidget(ok_btn)
        container_layout.addWidget(btn_container)
        
        main_layout.addWidget(self.container)
    
    def apply_style(self):
        # قراءة الشفافية من الإعدادات
        opacity = 245
        if self.config:
            opacity = self.config.get('settings_opacity', 245)
        
        self.setStyleSheet(f"""
            QFrame#SuccessContainer {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 36, 54, {opacity}), stop:1 rgba(20, 26, 44, {opacity}));
                border: 1px solid #4a90e2;
                border-radius: {BORDER_RADIUS}px;
            }}
            QLabel#SuccessTitle {{
                color: #02f76a;
                font-family: '{FONT_FAMILY}';
                font-size: {SUCCESS_TITLE_SIZE}px;
            }}
            QLabel#SuccessStatus {{
                color: #A0D8FF;
                font-family: '{FONT_FAMILY}';
                font-size: 16px;
            }}
            QPushButton#SuccessButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(2, 247, 106, 0.5), stop:1 rgba(2, 247, 106, 0.5));
                color: white;
                font-family: '{FONT_FAMILY}';
                font-size: {SUCCESS_BTN_SIZE}px;
                border: 2px solid rgba(2, 247, 106, 1);
                border-radius: {BUTTON_RADIUS}px;
            }}
            QPushButton#SuccessButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(2, 247, 106, 0.7), stop:1 rgba(2, 247, 106, 0.7));
            }}
        """)


def show_update_success(new_version=""):
    """دالة لعرض نافذة نجاح التحديث"""
    dialog = UpdateSuccessDialog(new_version)
    dialog.exec()
    return dialog


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                              للاختبار المستقل                               ║
# ╚════════════════════════════════════════════════════════════════════════════╝
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # إنشاء النافذة للاختبار
    window = UpdateDialog(
        current_version="1.9",    # الإصدار الحالي
        new_version="1.9",        # الإصدار الجديد
        download_url=""           # رابط التحميل (فارغ للاختبار)
    )
    window.show()
    
    sys.exit(app.exec())
