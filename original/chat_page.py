"""
╔════════════════════════════════════════════════════════════════════════════╗
║                         كشف الشات الذكي - اختبار                           ║
║                     Smart Chat Detector - Test Version                      ║
╚════════════════════════════════════════════════════════════════════════════╝

هذا الملف للاختبار قبل نقله للبرنامج الرئيسي.
يسمح للمستخدم بتحديد لون الشات المفتوح والمغلق لاكتشاف حالة الشات تلقائياً.

التصميم: مطابق لـ control_page.py
"""

import sys
import os

# تعطيل DPI Scaling
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ═══════════════════════════════════════════════════════════════════════════════
# أداة المصاصة (Eyedropper) - لالتقاط اللون من الشاشة
# ═══════════════════════════════════════════════════════════════════════════════

class EyedropperOverlay(QWidget):
    """
    ═══════════════════════════════════════════════════════════════════
    أداة المصاصة - نافذة لالتقاط اللون من الشاشة
    ═══════════════════════════════════════════════════════════════════
    
    الوظيفة: تغطي الشاشة بالكامل وتسمح للمستخدم بالنقر لالتقاط لون أي بكسل
    
    الإشارات (Signals):
    - color_picked: يُرسَل عند اختيار لون (يحمل QColor)
    - cancelled: يُرسَل عند الإلغاء (ESC أو كليك يمين)
    """
    color_picked = pyqtSignal(QColor)  # إشارة: اللون تم اختياره
    cancelled = pyqtSignal()           # إشارة: تم الإلغاء
    
    def __init__(self):
        super().__init__()
        
        # ════════════════════════════════════════════════════════════
        # إعدادات النافذة
        # ════════════════════════════════════════════════════════════
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |    # بدون إطار (شريط العنوان)
            Qt.WindowType.WindowStaysOnTopHint |   # فوق كل النوافذ
            Qt.WindowType.Tool                     # لا تظهر في شريط المهام
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # لا تأخذ التركيز
        self.setCursor(Qt.CursorShape.CrossCursor)  # شكل الماوس: علامة +
        
        # ════════════════════════════════════════════════════════════
        # تغطية الشاشة
        # ════════════════════════════════════════════════════════════
        screen = QApplication.primaryScreen()
        geo = screen.virtualGeometry()  # أبعاد كل الشاشات المتصلة
        self.setGeometry(geo)           # تغطية كل الشاشات
        
        # ════════════════════════════════════════════════════════════
        # التقاط صورة الشاشة (مرة واحدة فقط عند الفتح)
        # ════════════════════════════════════════════════════════════
        # هذا يمنع الرمش ويضمن قراءة ألوان صحيحة
        self.screen_image = screen.grabWindow(0).toImage()
        
        # ════════════════════════════════════════════════════════════
        # متغيرات الحالة
        # ════════════════════════════════════════════════════════════
        self.current_color = QColor(128, 128, 128)  # اللون الحالي (رمادي افتراضي)
        self.mouse_pos = QPoint(0, 0)               # موقع الماوس الحالي
        
        # ════════════════════════════════════════════════════════════
        # تايمر لتحديث اللون
        # ════════════════════════════════════════════════════════════
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_color)
        # ↓↓↓ سرعة التحديث بالمللي ثانية ↓↓↓
        # 30 = سريع (30 مرة بالثانية)
        # 100 = متوسط
        # 500 = بطيء
        self.timer.start(30)
    
    def update_color(self):
        """
        ════════════════════════════════════════════════════════════
        تحديث اللون الحالي بناءً على موقع الماوس
        ════════════════════════════════════════════════════════════
        تُستدعى تلقائياً كل 30ms (من التايمر)
        """
        pos = QCursor.pos()      # موقع الماوس الآن
        self.mouse_pos = pos     # حفظه للرسم
        
        # قراءة اللون من الصورة المحفوظة (وليس من الشاشة مباشرة)
        if 0 <= pos.x() < self.screen_image.width() and 0 <= pos.y() < self.screen_image.height():
            self.current_color = QColor(self.screen_image.pixel(pos.x(), pos.y()))
        
        self.update()  # إعادة رسم النافذة
    
    def paintEvent(self, event):
        """
        ════════════════════════════════════════════════════════════
        رسم الواجهة: صورة الشاشة + مربع المعاينة + علامة +
        ════════════════════════════════════════════════════════════
        تُستدعى تلقائياً عند كل update()
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # تنعيم الحواف
        
        # رسم صورة الشاشة كخلفية
        painter.drawImage(0, 0, self.screen_image)
        
        # ════════════════════════════════════════════════════════════
        # إعدادات مربع المعاينة
        # ════════════════════════════════════════════════════════════
        # ↓↓↓ حجم مربع المعاينة بالبكسل ↓↓↓
        # 80 = حجم متوسط، 60 = صغير، 120 = كبير
        preview_size = 80
        
        # ↓↓↓ بُعد المربع عن الماوس بالبكسل ↓↓↓
        # 25 = قريب، 50 = بعيد
        offset = 25
        
        # ════════════════════════════════════════════════════════════
        # حساب موقع المعاينة (بجانب الماوس)
        # ════════════════════════════════════════════════════════════
        px = self.mouse_pos.x() + offset  # يمين الماوس
        py = self.mouse_pos.y() + offset  # أسفل الماوس
        
        # إذا خرج من الشاشة، اعكس الاتجاه
        if px + preview_size > self.width():
            px = self.mouse_pos.x() - offset - preview_size  # يسار الماوس
        if py + preview_size > self.height():
            py = self.mouse_pos.y() - offset - preview_size  # فوق الماوس
        
        # ════════════════════════════════════════════════════════════
        # رسم مربع المعاينة
        # ════════════════════════════════════════════════════════════
        rect = QRect(px, py, preview_size, preview_size)
        
        # رسم الظل (مربع أسود شفاف خلف المعاينة)
        painter.setPen(Qt.PenStyle.NoPen)
        # ↓↓↓ شفافية الظل (0=شفاف، 255=معتم) ↓↓↓
        painter.setBrush(QColor(0, 0, 0, 150))
        # ↓↓↓ دائرية زوايا الظل ↓↓↓
        painter.drawRoundedRect(rect.adjusted(1, 1, 1, 1), 12, 12)
        
        # رسم المربع الملون باللون المختار
        painter.setBrush(self.current_color)
        # ↓↓↓ سُمك الإطار الأبيض ↓↓↓
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        # ↓↓↓ دائرية الزوايا ↓↓↓
        painter.drawRoundedRect(rect, 12, 12)
        
        # ════════════════════════════════════════════════════════════
        # كتابة كود اللون (Hex)
        # ════════════════════════════════════════════════════════════
        hex_color = self.current_color.name().upper()  # مثل #FF5500
        
        # خلفية سوداء للنص
        text_rect = QRect(px, py + preview_size - 50, preview_size, 20)
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(text_rect, 0, 0)
        
        # النص
        painter.setPen(QColor(255, 255, 255))
        # ↓↓↓ حجم خط كود اللون ↓↓↓
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, hex_color)
        

    
    def mousePressEvent(self, event):
        """عند الضغط - التقاط اللون"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.timer.stop()
            print(f"[EYEDROPPER] Captured: {self.current_color.name()} at ({self.mouse_pos.x()}, {self.mouse_pos.y()})")
            self.color_picked.emit(self.current_color)
            self.close()
        elif event.button() == Qt.MouseButton.RightButton:
            self.timer.stop()
            self.cancelled.emit()
            self.close()
    
    def keyPressEvent(self, event):
        """إلغاء بـ Escape"""
        if event.key() == Qt.Key.Key_Escape:
            self.timer.stop()
            self.cancelled.emit()
            self.close()
    
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
            print(f"[EYEDROPPER] Error applying WS_EX_NOACTIVATE: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# مربع اللون (Color Box) - بستايل settings_page
# ═══════════════════════════════════════════════════════════════════════════════

class ColorBox(QFrame):
    """
    ═══════════════════════════════════════════════════════════════════
    مربع اختيار اللون - للشات المفتوح أو المغلق
    ═══════════════════════════════════════════════════════════════════
    
    الوظيفة: مربع قابل للنقر لتحديد لون من الشاشة
    
    الإشارات (Signals):
    - color_changed: يُرسَل عند اختيار لون (QColor, x, y)
    - color_cleared: يُرسَل عند مسح اللون (كليك يمين)
    """
    color_changed = pyqtSignal(QColor, int, int)  # إشارة: اللون + الإحداثيات
    color_cleared = pyqtSignal()                   # إشارة: تم المسح
    
    def __init__(self, label_text="", parent=None):
        super().__init__(parent)
        
        # ════════════════════════════════════════════════════════════
        # متغيرات الحالة
        # ════════════════════════════════════════════════════════════
        self.label_text = label_text  # النص (مثل "مفتوح" أو "مغلق")
        self.color = None             # اللون المختار (None = لم يُختر)
        self.pos_x = 0                # إحداثي X للبكسل
        self.pos_y = 0                # إحداثي Y للبكسل
        self.is_set = False           # هل تم تحديد لون؟
        
        # ════════════════════════════════════════════════════════════
        # إعدادات المربع
        # ════════════════════════════════════════════════════════════
        self.setObjectName("ColorBox")
        # ↓↓↓ حجم المربع (عرض, ارتفاع) بالبكسل ↓↓↓
        # 130x75 = حجم متوسط، للتكبير: 150x90، للتصغير: 110x60
        self.setFixedSize(130, 75)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # شكل اليد عند التمرير
        
        # تتبع السحب
        self._drag_started = False
        self._press_pos = None
        self._moved = False
        
        self.setup_ui()
        self.update_style()
    
    def setup_ui(self):
        """
        ════════════════════════════════════════════════════════════
        بناء واجهة المربع: أيقونة + نص الحالة
        ════════════════════════════════════════════════════════════
        """
        layout = QVBoxLayout(self)
        # ↓↓↓ هوامش داخلية (يسار, أعلى, يمين, أسفل) ↓↓↓
        layout.setContentsMargins(8, 0, 0, 10)
        # ↓↓↓ مسافة بين الأيقونة والنص ↓↓↓
        layout.setSpacing(4)
        
        # أيقونة المصاصة - صورة متحركة
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")
        self.icon_label.setFixedHeight(50)  # ↓↓↓ ارتفاع الأيقونة لإنزالها ↓↓↓
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gif_path = os.path.join(script_dir, '..', 'Icons', 'Location.gif')
        if os.path.exists(gif_path):
            self.icon_movie = QMovie(gif_path)
            self.icon_movie.setScaledSize(QSize(80, 80))
            self.icon_label.setMovie(self.icon_movie)
            self.icon_movie.start()
        
        # نص الحالة (✗ مفتوح أو ✓ مفتوح)
        self.status_label = QLabel(f"<span style='color: #00ff00; font-size: 13px;'>❌</span> {self.label_text}")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #ff6b6b;
            font-family: 'Segoe UI';
            font-size: 18px;
            font-weight: normal;
            background: transparent;
        """)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.status_label)
        
        # جعل العناصر الداخلية تمرر أحداث الماوس للمربع
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.status_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
    def update_style(self):
        """تحديث التنسيق حسب الحالة - بستايل settings_page"""
        if self.is_set and self.color:
            # لون محدد - مثل أزرار لون الخلفية/النص في settings_page
            bg_color = self.color.name()
            
            # حساب لون النص والإطار
            brightness = (self.color.red() * 299 + self.color.green() * 587 + self.color.blue() * 114) / 1000
            text_color = "#000000" if brightness > 128 else "#ffffff"
            
            # حساب لون الإطار
            r, g, b = self.color.red(), self.color.green(), self.color.blue()
            factor = 1.3 if brightness < 128 else 0.7
            border_r = int(min(255, max(0, r * factor)))
            border_g = int(min(255, max(0, g * factor)))
            border_b = int(min(255, max(0, b * factor)))
            border_color = f"#{border_r:02X}{border_g:02X}{border_b:02X}"
            
            self.setStyleSheet(f"""
                QFrame#ColorBox {{
                    background: {bg_color};
                    border: 2px solid {border_color};
                    border-radius: 10px;
                }}
                QFrame#ColorBox:hover {{
                    border: 2px solid #c4c4c4;
                }}
            """)
            self.status_label.setText(f"<span style='color: #00ff00; font-size: 18px;'>✔</span> {self.label_text}")
            self.status_label.setStyleSheet(f"""
                color: {text_color};
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: normal;
                background: transparent;
            """)
            self.icon_label.setStyleSheet(f"font-size: 22px; color: {text_color}; background: transparent;")
        else:
            # غير محدد - مثل الأزرار الباهتة
            self.setStyleSheet("""
                QFrame#ColorBox {
                    background: rgba(52, 120, 220, 0.35);
                    border: 2px dashed rgba(100, 150, 250, 0.5);
                    border-radius: 10px;
                }
                QFrame#ColorBox:hover {
                    background: rgba(52, 120, 220, 0.50);
                    border: 2px dashed rgba(100, 150, 250, 0.8);
                }
            """)
            self.status_label.setText(f"<span style='color: #00ff00; font-size: 13px;'>❌</span> {self.label_text}")
            self.status_label.setStyleSheet("""
                color: #FD638D;
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: normal;
                background: transparent;
            """)
            self.icon_label.setStyleSheet("font-size: 22px; background: transparent;")
    
    def mousePressEvent(self, event):
        """تسجيل موقع الضغط"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.pos()
            self._global_press = event.globalPosition().toPoint()
            self._moved = False  # لم يتحرك بعد
        # تمرير الحدث للأب للسحب
        event.ignore()
    
    def mouseMoveEvent(self, event):
        """أي حركة = سحب = إلغاء + تمرير للأب"""
        if self._press_pos is not None:
            self._moved = True
        # تمرير الحدث للأب للسحب
        event.ignore()
    
    def mouseReleaseEvent(self, event):
        """نقر على المربع - يعمل فقط إذا لم يتحرك"""
        if event.button() == Qt.MouseButton.LeftButton:
            # فقط إذا لم يتحرك
            if not self._moved and self.rect().contains(event.pos()):
                self.start_eyedropper()
            self._press_pos = None
            self._moved = False
        elif event.button() == Qt.MouseButton.RightButton:
            if self.rect().contains(event.pos()):
                self.clear_color()
        # تمرير الحدث للأب
        event.ignore()
    
    def start_eyedropper(self):
        """بدء التقاط اللون"""
        self.eyedropper = EyedropperOverlay()
        self.eyedropper.color_picked.connect(self.set_color_with_pos)
        self.eyedropper.show()
    
    def set_color_with_pos(self, color):
        """تعيين اللون مع الموقع"""
        pos = QCursor.pos()
        self.color = color
        self.pos_x = pos.x()
        self.pos_y = pos.y()
        self.is_set = True
        self.update_style()
        self.color_changed.emit(color, self.pos_x, self.pos_y)
    
    def clear_color(self):
        """مسح اللون"""
        self.color = None
        self.pos_x = 0
        self.pos_y = 0
        self.is_set = False
        self.update_style()
        self.color_cleared.emit()
    
    def get_color(self):
        """الحصول على اللون"""
        return self.color if self.is_set else None
    
    def get_position(self):
        """الحصول على الموقع"""
        return (self.pos_x, self.pos_y) if self.is_set else (0, 0)


# ═══════════════════════════════════════════════════════════════════════════════
# محتوى صفحة كشف الشات - بستايل control_page
# ═══════════════════════════════════════════════════════════════════════════════

class ChatDetectorContent(QWidget):
    """
    ═══════════════════════════════════════════════════════════════════
    محتوى صفحة كشف الشات - المحتوى الرئيسي
    ═══════════════════════════════════════════════════════════════════
    
    الوظيفة: يحتوي على كل عناصر الواجهة (إطار العنوان، مربعات الألوان، إلخ)
    """
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        
        self.config = config  # مرجع لإعدادات البرنامج (اختياري)
        
        self.setup_ui()
        self.apply_style()
        
        # تحميل الألوان المحفوظة (بعد setup_ui)
        self.load_saved_colors()
    
    def load_saved_colors(self):
        """تحميل الألوان المحفوظة من الإعدادات"""
        if not self.config:
            return
        
        # تحميل لون الشات المفتوح
        open_color = self.config.get('chat_open_color')
        open_x = self.config.get('chat_detect_x')
        open_y = self.config.get('chat_detect_y')
        
        if open_color and open_color.strip():
            # تعيين اللون بدون إشعار (لتجنب الحفظ مرة أخرى)
            self.open_color_box.color = QColor(open_color)
            self.open_color_box.pos_x = open_x if open_x != -1 else 0
            self.open_color_box.pos_y = open_y if open_y != -1 else 0
            self.open_color_box.is_set = True
            self.open_color_box.update_style()
            print(f"[DETECTOR] Loaded open color: {open_color} at ({open_x}, {open_y})")
        
        # تحميل لون الشات المغلق
        closed_color = self.config.get('chat_closed_color')
        
        if closed_color and closed_color.strip():
            self.closed_color_box.color = QColor(closed_color)
            self.closed_color_box.pos_x = open_x if open_x != -1 else 0  # نفس الموقع
            self.closed_color_box.pos_y = open_y if open_y != -1 else 0
            self.closed_color_box.is_set = True
            self.closed_color_box.update_style()
            print(f"[DETECTOR] Loaded closed color: {closed_color}")
        
        # تحديث الحالة
        self.update_status()
    
    def setup_ui(self):
        """
        ════════════════════════════════════════════════════════════
        بناء واجهة صفحة كشف الشات
        ════════════════════════════════════════════════════════════
        """
        
        # ════════════════════════════════════════════════════════════
        # التخطيط الرئيسي (main_layout)
        # ════════════════════════════════════════════════════════════
        # هوامش 0 = لإتاحة إطار العنوان يأخذ العرض الكامل
        main_layout = QVBoxLayout(self)
        # ↓↓↓ هوامش النافذة الرئيسية (يسار, أعلى, يمين, أسفل) ↓↓↓
        main_layout.setContentsMargins(0, 0, 0, 0)
        # ↓↓↓ مسافة بين العناصر ↓↓↓
        main_layout.setSpacing(25)
        
        # ↓↓↓ مسافة قبل إطار العنوان ↓↓↓
        main_layout.addSpacing(10)
        
        # ════════════════════════════════════════════════════════════
        # إطار العنوان (Header)
        # ════════════════════════════════════════════════════════════
        # حاوية لإطار العنوان (للتحكم في margins منفصلة)
        header_container = QWidget()
        header_container_layout = QHBoxLayout(header_container)
        # ↓↓↓ هوامش إطار العنوان من الجوانب ↓↓↓
        # 15 = يترك مسافة من اليمين واليسار
        header_container_layout.setContentsMargins(15, 0, 15, 0)
        
        header_frame = QFrame()
        header_frame.setObjectName("HeaderWidget")
        # ↓↓↓ ارتفاع إطار العنوان ↓↓↓
        header_frame.setFixedHeight(50)
        
        header_layout = QHBoxLayout(header_frame)
        # ↓↓↓ هوامش داخل إطار العنوان (يسار, أعلى, يمين, أسفل) ↓↓↓
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(0)
        
        header_layout.addStretch()  # دفع العنوان لليمين
        
        # العنوان
        title_label = QLabel("تحديد لون موقع الكتابة")
        title_label.setObjectName("HeaderTitle")
        header_layout.addWidget(title_label)
        
        # أيقونة sniper
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sniper_icon_path = os.path.join(script_dir, '..', 'Icons', 'sniper.png')
        if os.path.exists(sniper_icon_path):
            sniper_icon = QLabel()
            sniper_pixmap = QPixmap(sniper_icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            sniper_icon.setPixmap(sniper_pixmap)
            sniper_icon.setStyleSheet("background: transparent;")
            header_layout.addSpacing(8)
            header_layout.addWidget(sniper_icon)
        
        header_container_layout.addWidget(header_frame)
        main_layout.addWidget(header_container)
        # ↓↓↓ مسافة بعد إطار العنوان ↓↓↓
        main_layout.addSpacing(10)
        
        # ════════════════════════════════════════════════════════════
        # حاوية المحتوى (content_container)
        # ════════════════════════════════════════════════════════════
        # هذه الحاوية لها margins أكبر = المحتوى أضيق من العنوان
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        # ↓↓↓ هوامش المحتوى (يسار, أعلى, يمين, أسفل) ↓↓↓
        # 30 = محتوى أضيق من العنوان بـ 30 بكسل من كل جانب
        content_layout.setContentsMargins(30, 0, 30, 10)
        content_layout.setSpacing(0)
        
        # ════════════════════════════════════════════════════════════
        # النص التوضيحي
        # ════════════════════════════════════════════════════════════
        desc_lbl = QLabel("حدد لون الشات عندما يكون مفتوح ومغلق\nليتم كشف حالته تلقائياً")
        desc_lbl.setObjectName("DescLabel")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)  # التفاف النص
        content_layout.addWidget(desc_lbl)
        
        # ↓↓↓ مسافة بين النص ومربعات الألوان ↓↓↓
        content_layout.addSpacing(16)
        
        # ════════════════════════════════════════════════════════════
        # مربعات الألوان (مفتوح + مغلق)
        # ════════════════════════════════════════════════════════════
        colors_container = QWidget()
        colors_layout = QHBoxLayout(colors_container)
        colors_layout.setContentsMargins(0, 0, 0, 0)
        # ↓↓↓ مسافة بين مربع "مفتوح" و "مغلق" ↓↓↓
        colors_layout.setSpacing(15)
        
        # مربع "مفتوح"
        self.open_color_box = ColorBox("مفتوح")
        self.open_color_box.color_changed.connect(self.on_open_color_changed)
        self.open_color_box.color_cleared.connect(self.on_open_color_cleared)
        
        # مربع "مغلق"
        self.closed_color_box = ColorBox("مغلق")
        self.closed_color_box.color_changed.connect(self.on_closed_color_changed)
        self.closed_color_box.color_cleared.connect(self.on_closed_color_cleared)
        
        colors_layout.addStretch()
        colors_layout.addWidget(self.open_color_box)
        colors_layout.addWidget(self.closed_color_box)
        colors_layout.addStretch()
        
        content_layout.addWidget(colors_container)
        content_layout.addSpacing(16)
        
        # === مربع الحالة - تحت مربعي الألوان مباشرة ===
        self.status_frame = QFrame()
        self.status_frame.setObjectName("StatusFrame")
        self.status_frame.setMinimumHeight(50)
        
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(8)
        
        # مسافة يسار
        status_layout.addStretch()
        
        # نص الحالة
        self.status_label = QLabel("في انتظار تحديد الألوان...")
        self.status_label.setObjectName("StatusLabel")
        status_layout.addWidget(self.status_label)
        
        # أيقونة الحالة
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(24, 24)
        status_layout.addWidget(self.status_icon)
        
        # مسافة يمين
        status_layout.addStretch()
        
        content_layout.addWidget(self.status_frame)
        
        content_layout.addSpacing(16)
        
        # === إطار التعليمات ===
        hint_frame = QFrame()
        hint_frame.setObjectName("HintFrame")
        hint_frame_layout = QVBoxLayout(hint_frame)
        hint_frame_layout.setContentsMargins(15, 12, 15, 12)
        
        hint_lbl = QLabel(
            "💡 اضغط على المربع ثم اختر اللون من الشاشة\n"
            "   • كليك يسار - تحديد اللون\n"
            "   • كليك يمين - إعادة تعيين"
        )
        hint_lbl.setObjectName("HintLabel")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_frame_layout.addWidget(hint_lbl)
        
        content_layout.addWidget(hint_frame)
        content_layout.addSpacing(16)
        
        # === زر اختبار الكشف ===
        self.test_btn = QPushButton("اختبار الكشف الشات")
        self.test_btn.setObjectName("TestButton")
        self.test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_btn.setMinimumHeight(60)
        self.test_btn.clicked.connect(self.test_detection)
        self.test_btn.setEnabled(False)
        content_layout.addWidget(self.test_btn)
        
        content_layout.addStretch()
        
        main_layout.addWidget(content_container)
        
        # تحديث الحالة الأولية
        self.update_status()
    
    def on_open_color_changed(self, color, x, y):
        """عند تغيير لون المفتوح"""
        print(f"[DETECTOR] Open color set: {color.name()} at ({x}, {y})")
        
        # حفظ في الإعدادات
        if self.config:
            self.config.set('chat_open_color', color.name())
            self.config.set('chat_detect_x', x)
            self.config.set('chat_detect_y', y)
            print(f"[DETECTOR] Saved open color to config")
        
        self.update_status()
    
    def on_open_color_cleared(self):
        """عند مسح لون المفتوح"""
        print("[DETECTOR] Open color cleared")
        
        # مسح من الإعدادات
        if self.config:
            self.config.set('chat_open_color', '')
            self.config.set('chat_detect_x', -1)
            self.config.set('chat_detect_y', -1)
        
        self.update_status()
    
    def on_closed_color_changed(self, color, x, y):
        """عند تغيير لون المغلق"""
        print(f"[DETECTOR] Closed color set: {color.name()} at ({x}, {y})")
        
        # حفظ في الإعدادات
        if self.config:
            self.config.set('chat_closed_color', color.name())
            print(f"[DETECTOR] Saved closed color to config")
        
        self.update_status()
    
    def on_closed_color_cleared(self):
        """عند مسح لون المغلق"""
        print("[DETECTOR] Closed color cleared")
        
        # مسح من الإعدادات
        if self.config:
            self.config.set('chat_closed_color', '')
        
        self.update_status()
    
    def update_status(self):
        """تحديث حالة الكشف وستايل مربع الحالة"""
        open_set = self.open_color_box.is_set
        closed_set = self.closed_color_box.is_set
        
        # مسار الأيقونات
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(script_dir, '..', 'Icons')
        
        if open_set and closed_set:
            # جاهز - أخضر + أيقونة time_on
            self.status_label.setText("جاهز للكشف")
            icon_path = os.path.join(icons_dir, 'time_on.png')
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.status_icon.setPixmap(pixmap)
            self.style_status_ready()
            self.test_btn.setEnabled(True)
            self.style_test_btn_enabled()
        else:
            # في انتظار - رمادي
            if not open_set and not closed_set:
                # لم يتم تحديد أي لون - أيقونة time
                self.status_label.setText("في انتظار تحديد الألوان...")
                icon_path = os.path.join(icons_dir, 'time.png')
            elif open_set:
                # تم تحديد المفتوح فقط - أيقونة time_add
                self.status_label.setText("حدد لون الشات المغلق...")
                icon_path = os.path.join(icons_dir, 'time_add.png')
            else:
                # تم تحديد المغلق فقط - أيقونة time_add
                self.status_label.setText("حدد لون الشات المفتوح...")
                icon_path = os.path.join(icons_dir, 'time_add.png')
            
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.status_icon.setPixmap(pixmap)
            
            self.style_status_waiting()
            self.test_btn.setEnabled(False)
            self.style_test_btn_disabled()
    
    def test_detection(self):
        """اختبار الكشف - يفحص اللون في الموقع المحفوظ"""
        open_color = self.open_color_box.get_color()
        closed_color = self.closed_color_box.get_color()
        open_pos = self.open_color_box.get_position()
        
        if not open_color or not closed_color:
            return
        
        # التقاط لون من الموقع المحفوظ باستخدام PrintWindow API
        x, y = open_pos
        try:
            import ctypes
            from ctypes import wintypes
            
            # البحث عن نافذة اللعبة (foreground window)
            game_hwnd = ctypes.windll.user32.GetForegroundWindow()
            
            # التحقق من صحة النافذة
            if game_hwnd and ctypes.windll.user32.IsWindow(game_hwnd):
                # الحصول على أبعاد النافذة
                rect = wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(game_hwnd, ctypes.byref(rect))
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                
                # تحويل إحداثيات الشاشة إلى إحداثيات النافذة
                local_x = x - rect.left
                local_y = y - rect.top
                
                # تحقق أن الإحداثيات داخل النافذة
                if 0 <= local_x < width and 0 <= local_y < height:
                    # إنشاء DC متوافق و bitmap
                    hdc_screen = ctypes.windll.user32.GetDC(game_hwnd)
                    hdc_mem = ctypes.windll.gdi32.CreateCompatibleDC(hdc_screen)
                    
                    # إنشاء bitmap
                    hbitmap = ctypes.windll.gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
                    old_bitmap = ctypes.windll.gdi32.SelectObject(hdc_mem, hbitmap)
                    
                    # PrintWindow لنسخ محتوى النافذة
                    PW_RENDERFULLCONTENT = 0x00000002
                    result = ctypes.windll.user32.PrintWindow(game_hwnd, hdc_mem, PW_RENDERFULLCONTENT)
                    
                    if result:
                        # قراءة البكسل من الصورة الملتقطة
                        pixel = ctypes.windll.gdi32.GetPixel(hdc_mem, local_x, local_y)
                    else:
                        # fallback إلى GetDC العادي
                        pixel = ctypes.windll.gdi32.GetPixel(hdc_screen, local_x, local_y)
                    
                    # تنظيف
                    ctypes.windll.gdi32.SelectObject(hdc_mem, old_bitmap)
                    ctypes.windll.gdi32.DeleteObject(hbitmap)
                    ctypes.windll.gdi32.DeleteDC(hdc_mem)
                    ctypes.windll.user32.ReleaseDC(game_hwnd, hdc_screen)
                else:
                    # الإحداثيات خارج النافذة
                    hdc = ctypes.windll.user32.GetDC(0)
                    pixel = ctypes.windll.gdi32.GetPixel(hdc, x, y)
                    ctypes.windll.user32.ReleaseDC(0, hdc)
            else:
                # لا يوجد نافذة - استخدم GetPixel العادي
                hdc = ctypes.windll.user32.GetDC(0)
                pixel = ctypes.windll.gdi32.GetPixel(hdc, x, y)
                ctypes.windll.user32.ReleaseDC(0, hdc)
            
            # تحويل للـ RGB
            r = pixel & 0xFF
            g = (pixel >> 8) & 0xFF
            b = (pixel >> 16) & 0xFF
            current_color = QColor(r, g, b)
            
            # مقارنة دقيقة
            open_match = self.colors_match_exact(current_color, open_color)
            closed_match = self.colors_match_exact(current_color, closed_color)
            
            print(f"[TEST] Position: ({x}, {y})")
            print(f"[TEST] Current: R={current_color.red()} G={current_color.green()} B={current_color.blue()} ({current_color.name()})")
            print(f"[TEST] Open:    R={open_color.red()} G={open_color.green()} B={open_color.blue()} ({open_color.name()})")
            print(f"[TEST] Closed:  R={closed_color.red()} G={closed_color.green()} B={closed_color.blue()} ({closed_color.name()})")
            print(f"[TEST] Match Open: {open_match}, Match Closed: {closed_match}")
            
            if open_match and not closed_match:
                self.status_label.setText("<span style='color: #00ff00; font-size: 18px;'>✔</span> الشات مفتوح")
                self.style_status_open()
            elif closed_match and not open_match:
                self.status_label.setText("<span style='color: #00ff00; font-size: 18px;'>✔</span> الشات مغلق")
                self.style_status_closed()
            elif open_match and closed_match:
                self.status_label.setText("⚠️ الألوان متشابهة")
                self.style_status_similar()
            else:
                self.status_label.setText("لون غير معروف❗")
                self.style_status_unknown()
        except Exception as e:
            print(f"[TEST] Error: {e}")
            self.status_label.setText("⁉️ خطأ في الكشف")
            self.style_status_unknown()
    
    def colors_match_exact(self, c1, c2, tolerance=25):
        """
        ════════════════════════════════════════════════════════════
        مقارنة دقيقة بين لونين
        ════════════════════════════════════════════════════════════
        
        المعاملات:
        - c1, c2: اللونان للمقارنة (QColor)
        - tolerance: هامش الخطأ المسموح لكل قناة (0-255)
        
        ↓↓↓ تأثير قيمة tolerance ↓↓↓
        - 0  = تطابق تام (لون مطابق 100%)
        - 25 = تسامح متوسط (يقبل اختلاف بسيط في الإضاءة)
        - 50 = تسامح عالي (يقبل ألوان متشابهة)
        
        الإرجاع: True إذا تطابق اللونان، False إذا لم يتطابقا
        """
        # مقارنة كل قناة (أحمر، أخضر، أزرق) مع هامش الخطأ
        return (abs(c1.red() - c2.red()) <= tolerance and      # الأحمر
                abs(c1.green() - c2.green()) <= tolerance and  # الأخضر
                abs(c1.blue() - c2.blue()) <= tolerance)       # الأزرق
    
    # ═══════════════════════════════════════════════════════════════════
    # دوال الستايل المنفصلة - كل عنصر له دالة خاصة
    # ═══════════════════════════════════════════════════════════════════
    
    def style_status_waiting(self):
        """ستايل مربع الحالة - انتظار"""
        # إظهار الأيقونة
        self.status_icon.show()
        self.status_frame.setStyleSheet("""
            QFrame#StatusFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 40, 60, 180),
                    stop:1 rgba(25, 30, 50, 160));
                border: 1px solid rgba(100, 150, 250, 0.25);
                border-radius: 10px;
            }
        """)
        self.status_label.setStyleSheet("""
            QLabel#StatusLabel {
                color: #8090a8;
                font-family: 'Segoe UI';
                font-size: 18px;
                background: transparent;
            }
        """)
    
    def style_status_ready(self):
        """ستايل مربع الحالة - جاهز للكشف"""
        # إظهار الأيقونة
        self.status_icon.show()
        self.status_frame.setStyleSheet("""
            QFrame#StatusFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 140, 80, 0.5),
                    stop:1 rgba(60, 110, 65, 0.6));
                border: 2px solid rgba(106, 200, 120, 0.6);
                border-radius: 10px;
            }
        """)
        self.status_label.setStyleSheet("""
            QLabel#StatusLabel {
                color: #b8e6c3;
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: normal;
                background: transparent;
            }
        """)
    
    def style_status_open(self):
        """ستايل مربع الحالة - الشات مفتوح"""
        # إخفاء الأيقونة بالكامل
        self.status_icon.hide()
        self.status_frame.setStyleSheet("""
            QFrame#StatusFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 140, 80, 0.5),
                    stop:1 rgba(60, 110, 65, 0.6));
                border: 2px solid rgba(106, 200, 120, 0.6);
                border-radius: 10px;
            }
        """)
        self.status_label.setStyleSheet("""
            QLabel#StatusLabel {
                color: #b8e6c3;
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: normal;
                background: transparent;
            }
        """)
    
    def style_status_closed(self):
        """ستايل مربع الحالة - الشات مغلق"""
        # إخفاء الأيقونة بالكامل
        self.status_icon.hide()
        self.status_frame.setStyleSheet("""
            QFrame#StatusFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 0, 0, 0.5),
                    stop:1 rgba(200, 0, 0, 0.5));
                border: 2px solid rgba(200, 0, 0, 0.8);
                border-radius: 10px;
            }
        """)
        self.status_label.setStyleSheet("""
            QLabel#StatusLabel {
                color: #FFDBDB;
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: normal;
                background: transparent;
            }
        """)
    
    def style_status_similar(self):
        """ستايل مربع الحالة - الألوان متشابهة"""
        # إخفاء الأيقونة بالكامل
        self.status_icon.hide()
        self.status_frame.setStyleSheet("""
            QFrame#StatusFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 150, 0, 0.3),
                    stop:1 rgba(150, 100, 0, 0.4));
                border: 2px solid rgba(200, 150, 100, 0.6);
                border-radius: 10px;
            }
        """)
        self.status_label.setStyleSheet("""
            QLabel#StatusLabel {
                color: #ffd280;
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: normal;
                background: transparent;
            }
        """)
    
    def style_status_unknown(self):
        """ستايل مربع الحالة - لون غير معروف"""
        # إخفاء الأيقونة بالكامل
        self.status_icon.hide()
        self.status_frame.setStyleSheet("""
            QFrame#StatusFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 40, 60, 180),
                    stop:1 rgba(25, 30, 50, 160));
                border: 1px solid rgba(100, 150, 250, 0.25);
                border-radius: 10px;
            }
        """)
        self.status_label.setStyleSheet("""
            QLabel#StatusLabel {
                color: #8090a8;
                font-family: 'Segoe UI';
                font-size: 18px;
                background: transparent;
            }
        """)
    
    def style_test_btn_enabled(self):
        """ستايل زر الاختبار - مفعّل"""
        # إزالة الشفافية للماوس - الزر يعمل الآن
        self.test_btn.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.test_btn.setStyleSheet("""
            QPushButton#TestButton {
                background: rgba(52, 120, 220, 0.85);
                color: #d0e8ff;
                font-family: 'Segoe UI';
                font-size: 22px;
                font-weight: normal;
                border: 2px solid #69aff5;
                border-radius: 10px;
                padding: 6px 14px;
            }
            QPushButton#TestButton:hover {
                background: rgba(52, 120, 220, 0.65);
            }
        """)
    
    def style_test_btn_disabled(self):
        """ستايل زر الاختبار - معطّل"""
        # جعل الزر شفاف للماوس - يسمح بسحب النافذة من فوقه
        self.test_btn.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.test_btn.setStyleSheet("""
            QPushButton#TestButton {
                background: rgba(52, 120, 220, 0.35);
                color: #d0e8ff;
                font-family: 'Segoe UI';
                font-size: 22px;
                font-weight: normal;
                border: 2px solid #5090c0;
                border-radius: 10px;
                padding: 6px 14px;
            }
        """)
    
    def apply_style(self):
        """تطبيق CSS"""
        self.setStyleSheet("""
            /* برواز العنوان */
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
            
            /* عنوان البرواز */
            QLabel#HeaderTitle {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a0d8ff,
                    stop:1 #ff9a3c);
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: bold;
            }
            
            /* النص التوضيحي */
            QLabel#DescLabel {
                color: #c0c8d8;
                font-family: 'Segoe UI';
                font-size: 18px;
            }
            
            /* إطار التعليمات */
            QFrame#HintFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 56, 74, 150),
                    stop:1 rgba(40, 46, 64, 150));
                border: 1px solid rgba(100, 150, 250, 0.15);
                border-radius: 8px;
            }
            
            /* نص التعليمات */
            QLabel#HintLabel {
                color: #8090a8;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# نافذة الاختبار المستقلة
# ═══════════════════════════════════════════════════════════════════════════════

class ChatDetectorTest(QWidget):
    """
    ═══════════════════════════════════════════════════════════════════
    نافذة الاختبار المستقلة
    ═══════════════════════════════════════════════════════════════════
    
    الوظيفة: نافذة شفافة قابلة للسحب لاختبار كشف الشات
    تُستخدم عند تشغيل الملف مباشرة (python test_chat_detector.py)
    """
    
    def __init__(self):
        super().__init__()
        
        # ════════════════════════════════════════════════════════════
        # إعدادات النافذة
        # ════════════════════════════════════════════════════════════
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |    # بدون إطار (شريط العنوان)
            Qt.WindowType.WindowStaysOnTopHint     # فوق كل النوافذ
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # خلفية شفافة
        
        # ↓↓↓ حجم النافذة (عرض, ارتفاع) بالبكسل ↓↓↓
        # 370 = نفس عرض صفحة التحكم
        # 420 = ارتفاع مناسب للمحتوى (بعد إضافة الأيقونات)
        self.setFixedSize(370, 441)
        
        # ════════════════════════════════════════════════════════════
        # إضافة المحتوى
        # ════════════════════════════════════════════════════════════
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ChatDetectorContent = المحتوى الرئيسي
        self.content = ChatDetectorContent(self)
        layout.addWidget(self.content)
        
        # توسيط النافذة في الشاشة
        QTimer.singleShot(10, self._center)
    
    def _center(self):
        """توسيط النافذة"""
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )


# ═══════════════════════════════════════════════════════════════════════════════
# التشغيل
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    window = ChatDetectorTest()
    window.show()
    
    sys.exit(app.exec())
