import sys
import os

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ========================================
# استيراد VERSION من version.py تلقائياً
# ========================================
try:
    # إضافة المسار الأب للوصول لـ version.py
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from version import VERSION
except ImportError:
    VERSION = "1.9"  # قيمة افتراضية في حالة الفشل

# ========================================
# CLASS 1: AboutPageContent - للربط مع styles.py
# ========================================
# هذا الـ class يحتوي على المحتوى فقط (بدون إعدادات النافذة)
# يُستخدم داخل QStackedWidget في styles.py

class AboutPageContent(QWidget):
    """محتوى صفحة حول - للربط مع الإطار الرئيسي"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        
        content_layout = QVBoxLayout(self)
        content_layout.setContentsMargins(30, 10, 30, 30)
        content_layout.setSpacing(0)
        
        content_layout.addStretch(1)
        
        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, '..', 'Icons', 'app_256.png')
        
        if os.path.exists(logo_path):
            logo_size = 100
            pixmap = QPixmap(logo_path).scaled(
                logo_size, logo_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pixmap)
        
        content_layout.addWidget(logo_lbl)
        content_layout.addSpacing(15)
        
        app_name = QLabel("Smart Keyboard")
        app_name.setObjectName("AppName")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet("""
            color: #A0D8FF;
            font-family: 'Segoe UI';
            font-size: 23px;
            font-weight: bold;
        """)
        
        content_layout.addWidget(app_name)
        content_layout.addSpacing(5)
        
        app_name_ar = QLabel("لوحة المفاتيح الذكية")
        app_name_ar.setObjectName("AppNameAr")
        app_name_ar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name_ar.setStyleSheet("""
            color: #C0D0E8;
            font-family: 'Segoe UI';
            font-size: 18px;
        """)
        
        content_layout.addWidget(app_name_ar)
        content_layout.addSpacing(3)
        
        app_desc = QLabel("للألعاب والبرامج غير الداعمة للغة العربية")
        app_desc.setObjectName("AppDesc")
        app_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_desc.setStyleSheet("""
            color: #6a7a8f;
            font-family: 'Segoe UI';
            font-size: 15px;
        """)
        
        content_layout.addWidget(app_desc)
        content_layout.addSpacing(18)
        
        sep_container = QWidget()
        sep_layout = QHBoxLayout(sep_container)
        sep_layout.setContentsMargins(0, 0, 0, 0)
        sep_layout.addStretch()
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedWidth(170)
        separator.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent,
                stop:0.5 #FF8C24,
                stop:1 transparent
            );
            min-height: 4px;
            max-height: 4px;
            border: none;
        """)
        
        sep_layout.addWidget(separator)
        sep_layout.addStretch()
        
        content_layout.addWidget(sep_container)
        content_layout.addSpacing(18)
        
        dev_lbl = QLabel("Developed by Reem (7T2)")
        dev_lbl.setObjectName("DevName")
        dev_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_lbl.setStyleSheet("""
            color: #C0D0E8;
            font-family: 'Segoe UI';
            font-size: 15px;
        """)
        
        content_layout.addWidget(dev_lbl)
        content_layout.addSpacing(3)
        
        dev_ar_lbl = QLabel(
    "تم التطوير بواسطة ريــReemـم (7T2)<br>"
    "البرنامج <span style='color: #58D58D;'>مجاني</span> لخدمة جميع العرب<br>"
    "أرجو منكم الدعاء لي بالخير هو أفضل دعم"
)
        dev_ar_lbl.setObjectName("DevNameAr")
        dev_ar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_ar_lbl.setStyleSheet("""
            color: #8090a8;
            font-family: 'Segoe UI';
            font-size: 15px;
        """)
        
        content_layout.addWidget(dev_ar_lbl)
        content_layout.addSpacing(18)
        
        ver_lbl = QLabel(f"v{VERSION}")
        ver_lbl.setObjectName("VerLbl")
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver_lbl.setStyleSheet("""
            color: #ff9a3c;
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: normal;
        """)
        
        content_layout.addWidget(ver_lbl)
        content_layout.addSpacing(5)
        content_layout.addSpacing(50)
        
        copy_lbl = QLabel("حقوق النشر Copyright © 2026")
        copy_lbl.setObjectName("CopyLbl")
        copy_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copy_lbl.setStyleSheet("""
            color: #8090a8;
            font-family: 'Segoe UI';
            font-size: 13px;
        """)
        
        content_layout.addWidget(copy_lbl)


# ========================================
# CLASS 2: AboutPageTest - للاختبار المستقل
# ========================================
# هذا الـ class يحتوي على إعدادات النافذة للاختبار
# يُستخدم عند تشغيل about_page.py مباشرة

class AboutPageTest(QWidget):
    """نافذة اختبار صفحة حول - مستقلة"""
    
    def __init__(self):
        super().__init__()
        
        # خلفية شفافة + بدون إطار
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedSize(370, 460)
        
        # إضافة المحتوى
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # استخدام AboutPageContent للمحتوى
        content = AboutPageContent(self)
        layout.addWidget(content)
    
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
    window = AboutPageTest()
    window.show()
    sys.exit(app.exec())

