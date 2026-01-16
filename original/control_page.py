import sys
import os

# تعطيل DPI Scaling
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ========================================
# CLASS 1: ControlPageContent - للربط مع styles.py
# ========================================
# هذا الـ class يحتوي على المحتوى فقط (بدون إعدادات النافذة)
# يُستخدم داخل QStackedWidget في styles.py

class ControlPageContent(QWidget):
    """محتوى صفحة التحكم - للربط مع الإطار الرئيسي"""
    
    def __init__(self, parent=None, config=None, overlay=None):
        super().__init__(parent)
        
        # مراجع للإعدادات والنافذة الرئيسية
        self.config = config  # ConfigManager من main.py
        self.overlay = overlay  # OverlayWindow للـ apply_settings
        
        # متغيرات الحالة
        self.current_send_mode = config.get('send_mode') if config else 'enter'
        
        self.setup_ui()
        self.apply_style()
        
        # تهيئة الحالة
        self.update_loc_display()
        self.update_send_mode_buttons()
    
    def setup_ui(self):
        """بناء واجهة صفحة التحكم"""
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 0, 15, 10)
        main_layout.setSpacing(0)
        
        main_layout.addSpacing(10)
        
        # === البرواز ===
        header_frame = QFrame()
        header_frame.setObjectName("HeaderWidget")
        header_frame.setFixedHeight(50)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(0)
        
        header_layout.addStretch()
        
        # === العنوان أولاً ===
        title_label = QLabel("التحكم")
        title_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #a0d8ff,
                stop:1 #ff9a3c);
            font-family: 'Segoe UI';
            font-size: 18px;
            font-weight: bold;
        """)
        
        header_layout.addWidget(title_label)
        
        # === مسافة بين النص والأيقونة ===
        header_layout.addSpacing(8)
        
        # === أيقونة التحكم ثانياً ===
        icon_label = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, '..', 'Icons', 'control.png')
        
        if os.path.exists(icon_path):
            icon_size = 24
            
            pixmap = QPixmap(icon_path).scaled(
                icon_size, icon_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
        
        header_layout.addWidget(icon_label)
        
        main_layout.addWidget(header_frame)
        main_layout.addSpacing(15)
        
        # قسم موقع الكتابة
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(script_dir, '..', 'Icons')
        
        # أيقونة موقع الكتابة
        mouse_icon_path = os.path.join(icons_dir, 'mouse_site.png')
        loc_section = self._create_section_card(
            "موقع الكتابة", 
            "#58D58D", 
            mouse_icon_path,
            "LocationSectionCard"
        )
        loc_layout = loc_section.layout()
        
        self.lbl_loc = QLabel("❌ غير محدد موقع الكتابة")
        self.lbl_loc.setObjectName("LocationLabel")
        self.lbl_loc.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_loc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_loc.setMinimumHeight(60)
        loc_layout.addWidget(self.lbl_loc)
        
        self.btn_reset_loc = self._create_glow_button("إعادة تعيين موقع الكتابة", "#e74c3c")
        self.btn_reset_loc.setObjectName("ResetLocationButton")
        self.btn_reset_loc.clicked.connect(self.reset_location)
        loc_layout.addWidget(self.btn_reset_loc)
        
        hint = QLabel("حدد موقع الكتابة في الفأرة وضغط مرتين على insert")
        hint.setObjectName("LocationHintLabel")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loc_layout.addWidget(hint)
        
        main_layout.addWidget(loc_section)
        main_layout.addSpacing(18)
        
        # قسم طريقة الإرسال
        # أيقونة طريقة الإرسال
        keyboard_icon_path = os.path.join(icons_dir, 'keyboard.png')
        send_section = self._create_section_card(
            "طريقة الإرسال", 
            "#ff9a3c", 
            keyboard_icon_path,
            "SendMethodSectionCard"
        )
        send_layout = send_section.layout()
        
        send_row = QHBoxLayout()
        send_row.setSpacing(12)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(script_dir, '..', 'Icons')
        
        self.btn_enter_mode = self._create_glow_button("Enter ", "#4a90e2")
        self.btn_enter_mode.setObjectName("EnterModeButton")
        self.btn_enter_mode.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        enter_icon = os.path.join(icons_dir, 'Enter.png')
        if os.path.exists(enter_icon):
            self.btn_enter_mode.setIcon(QIcon(enter_icon))
            self.btn_enter_mode.setIconSize(QSize(24, 24))
        self.btn_enter_mode.clicked.connect(lambda: self.set_send_mode('enter'))
        
        self.btn_mouse_mode = self._create_glow_button("Mouse ", "#9b59b6")
        self.btn_mouse_mode.setObjectName("MouseModeButton")
        self.btn_mouse_mode.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        mouse_icon = os.path.join(icons_dir, 'Mouse.png')
        if os.path.exists(mouse_icon):
            self.btn_mouse_mode.setIcon(QIcon(mouse_icon))
            self.btn_mouse_mode.setIconSize(QSize(24, 24))
        self.btn_mouse_mode.clicked.connect(lambda: self.set_send_mode('mouse'))
        
        send_row.addWidget(self.btn_enter_mode)
        send_row.addWidget(self.btn_mouse_mode)
        send_layout.addLayout(send_row)
        
        self.lbl_send_mode = QLabel("")
        self.lbl_send_mode.setObjectName("SendModeHintLabel")
        self.lbl_send_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_send_mode.setWordWrap(True)
        send_layout.addWidget(self.lbl_send_mode)
        
        main_layout.addWidget(send_section)
        
        main_layout.addStretch()
    
    def _create_section_card(self, title, accent_color, icon_path=None, object_name="SectionCard"):
        """Create a beautiful section card with title and shadow"""
        card = QWidget()
        card.setObjectName(object_name)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 15, 18, 15)
        card_layout.setSpacing(12)
        
        # === Title container with icon ===
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        title_layout.addStretch()
        
        # Section title label
        title_label = QLabel(title)
        title_label.setObjectName(f"{object_name}Title")
        title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {accent_color};")
        title_layout.addWidget(title_label)
        
        # Add icon if provided
        if icon_path and os.path.exists(icon_path):
            icon_label = QLabel()
            icon_size = 24
            
            pixmap = QPixmap(icon_path).scaled(
                icon_size, icon_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
            title_layout.addWidget(icon_label)
        
        card_layout.addWidget(title_container)
        
        # Add subtle shadow to card
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(15)
        card_shadow.setColor(QColor(0, 0, 0, 80))
        card_shadow.setOffset(0, 3)
        card.setGraphicsEffect(card_shadow)
        
        return card
    
    def _create_glow_button(self, text, color):
        """Create a button with glow effect"""
        btn = QPushButton(text)
        btn.setObjectName("GlowButton")
        btn.setMinimumHeight(48)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
    
    def update_loc_display(self):
        """Update location label display from CONFIG"""
        if self.config:
            x = self.config.get('game_click_x')
            y = self.config.get('game_click_y')
            game_name = self.config.get('game_name')
            if x != -1:
                if game_name:
                    # استخراج اسم البرنامج فقط (بعد آخر - أو الاسم كامل)
                    if ' - ' in game_name:
                        display_name = game_name.split(' - ')[-1].strip()
                    else:
                        display_name = game_name
                    self.lbl_loc.setText(f"<span style='color: #00ff00; font-size: 18px;'>✔</span> {display_name}<br>X: {x}, Y: {y}")
                else:
                    self.lbl_loc.setText(f"<span style='color: #00ff00; font-size: 18px;'>✔</span> X: {x}, Y: {y}")
            else:
                self.lbl_loc.setText("<span style='font-size: 13px;'>❌</span> غير محدد موقع الكتابة")
        else:
            self.lbl_loc.setText("<span style='color: #00ff00; font-size: 18px;'>✔</span> 3DXChat<br>X: 1366, Y: 1003")
    
    def reset_location(self):
        """Reset saved location to CONFIG"""
        if self.config:
            self.config.set('game_click_x', -1)
            self.config.set('game_click_y', -1)
            self.config.set('game_name', '')
        self.update_loc_display()
        print("✓ Location reset!")
    
    def set_send_mode(self, mode):
        """Set the send mode (enter or mouse) to CONFIG"""
        if self.config:
            self.config.set('send_mode', mode)
        self.current_send_mode = mode
        self.update_send_mode_buttons()
        print(f"[SETTINGS] Send mode changed to: {mode}")
    
    def update_send_mode_buttons(self):
        """Update send mode button styles based on current selection"""
        if self.current_send_mode == 'enter':
            # Enter نشط - أزرق قوي
            self.btn_enter_mode.setStyleSheet("""
                QPushButton#EnterModeButton {
                    background: rgba(52, 120, 220, 0.85);
                    color: #ffffff;
                    border: 2px solid #60a0e0;
                }
                QPushButton#EnterModeButton:hover {
                    background: rgba(52, 120, 220, 0.65);
                }
            """)
            
            # Mouse غير نشط - أزرق باهت
            self.btn_mouse_mode.setStyleSheet("""
                QPushButton#MouseModeButton {
                    background: rgba(52, 120, 220, 0.35);
                    color: #d0e8ff;
                    border: 2px solid #5090c0;
                }
                QPushButton#MouseModeButton:hover {
                    background: rgba(52, 120, 220, 0.50);
                }
            """)
            
            self.lbl_send_mode.setText("إرسال النص عن طريق الـ Enter")
        else:
            # Mouse نشط - أزرق قوي
            self.btn_mouse_mode.setStyleSheet("""
                QPushButton#MouseModeButton {
                    background: rgba(52, 120, 220, 0.85);
                    color: #ffffff;
                    border: 2px solid #60a0e0;
                }
                QPushButton#MouseModeButton:hover {
                    background: rgba(52, 120, 220, 0.65);
                }
            """)
            
            # Enter غير نشط - أزرق باهت
            self.btn_enter_mode.setStyleSheet("""
                QPushButton#EnterModeButton {
                    background: rgba(52, 120, 220, 0.35);
                    color: #d0e8ff;
                    border: 2px solid #5090c0;
                }
                QPushButton#EnterModeButton:hover {
                    background: rgba(52, 120, 220, 0.50);
                }
            """)
            
            self.lbl_send_mode.setText("إرسال النص عن طريق الـ Mouse")
    
    def apply_style(self):
        """تطبيق CSS"""
        self.setStyleSheet("""
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
            
            QWidget#LocationSectionCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 40, 60, 180),
                    stop:1 rgba(25, 30, 50, 160));
                border: 1px solid rgba(100, 150, 250, 0.25);
                border-radius: 10px;
            }
            
            QLabel#LocationSectionCardTitle {
                font-family: 'Segoe UI';
                font-size: 18px;
                padding: 5px;
            }
            
            QWidget#SendMethodSectionCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 40, 60, 180),
                    stop:1 rgba(25, 30, 50, 160));
                border: 1px solid rgba(100, 150, 250, 0.25);
                border-radius: 10px;
            }
            
            QLabel#SendMethodSectionCardTitle {
                font-family: 'Segoe UI';
                font-size: 18px;
                padding: 5px;
            }
            
            QLabel#LocationLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 140, 80, 0.5),
                    stop:1 rgba(60, 110, 65, 0.6));
                color: #b8e6c3;
                border: 2px solid rgba(106, 200, 120, 0.5);
                border-radius: 10px;
                padding: 15px;
                font-family: 'Segoe UI';
                font-size: 18px;
            }
            
            QLabel#LocationHintLabel {
                color: #8090a8;
                font-family: 'Segoe UI';
                font-size: 15px;
            }
            
            QLabel#SendModeHintLabel {
                color: #8090a8;
                font-family: 'Segoe UI';
                font-size: 15px;
            }
            
            QPushButton#ResetLocationButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 0, 0, 0.5),
                    stop:1 rgba(200, 0, 0, 0.5));
                color: #FFDBDB;
                font-family: 'Segoe UI';
                font-size: 23px;
                font-weight: normal;
                border: 2px solid rgba(200, 0, 0, 1);
                border-radius: 14px;
                padding: 10px 16px;
            }
            
            QPushButton#ResetLocationButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(2, 247, 106, 0.5),
                    stop:1 rgba(2, 247, 106, 0.5));
                border: 2px solid rgba(2, 247, 106, 1);
            }
            
            QPushButton#ResetLocationButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 168, 62, 0.5),
                    stop:1 rgba(0, 168, 62, 0.5));
            }
            
            QPushButton#EnterModeButton {
                background: rgba(52, 120, 220, 0.85);
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 20px;
                font-weight: normal;
                border: 2px solid #60a0e0;
                border-radius: 10px;
                padding: 6px 14px;
            }
            
            QPushButton#EnterModeButton:hover {
                background: rgba(52, 120, 220, 0.65);
            }
            
            QPushButton#MouseModeButton {
                background: rgba(52, 120, 220, 0.85);
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 20px;
                font-weight: normal;
                border: 2px solid #60a0e0;
                border-radius: 10px;
                padding: 6px 14px;
            }
            
            QPushButton#MouseModeButton:hover {
                background: rgba(52, 120, 220, 0.65);
            }
        """)


# ========================================
# CLASS 2: ControlPageTest - للاختبار المستقل
# ========================================
# هذا الـ class يحتوي على إعدادات النافذة للاختبار
# يُستخدم عند تشغيل control_page.py مباشرة

class ControlPageTest(QWidget):
    """نافذة اختبار صفحة التحكم - مستقلة"""
    
    def __init__(self):
        super().__init__()
        
        # خلفية شفافة + بدون إطار
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(370, 520)
        
        # إضافة المحتوى
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # استخدام ControlPageContent للمحتوى
        self.content = ControlPageContent(self)
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

# البرنامج الرئيسي
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ControlPageTest()
    window.show()
    sys.exit(app.exec())
