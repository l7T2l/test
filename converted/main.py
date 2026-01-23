import sys
import json
import os
import keyboard
import win32gui
import win32con
import win32api
import pyperclip
import time
import ctypes
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from logic import ArabicProcessor
from media_filter import get_filter, MediaFilter

# ========================================
# استيراد نافذة الإعدادات الجديدة من Styles
# ========================================
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Styles'))
# استيراد صريح لضمان تضمينها في Nuitka
from Styles import about_page, control_page, settings_page, main_styles
from Styles.main_styles import SidebarTest as NewSettingsDialog
from Styles.update_page import check_for_updates, show_update_success

# =================================================================================
# PROFESSIONAL OVERLAY CHAT - SMART KEYBOARD
# Version: 1.7 (2025-12-30) - Bug Fixes & Improvements
# =================================================================================
# v1.7 Changes:
# - Fixed: Qt rgba(1) bug - slider minimum now 2 instead of 0
# - Fixed: Context menu paste using custom_paste() with internal clipboard
# - Fixed: Context menu clicks not affecting needs_enter state
# - Added: Context menu background opacity follows chat background
# - Removed: Deprecated _restore_opacity and _soft_hide_for_fullscreen functions
# =================================================================================
# استيراد رقم الإصدار من الملف المركزي
from version import VERSION

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.defaults = {
            "x": 586, "y": 418, "w": 468, "h": 90,
            "bg_color": "#000000", "text_color": "#FFFF00",
            "bg_opacity": 200, "text_opacity": 255,
            "settings_opacity": 230,
            "font_size": 20,
            "first_line_end": 0,  # Where first line ends (left margin in pixels)
            "hotkey": "insert",
            "game_click_x": -1, "game_click_y": -1,
            "game_name": "",  # Name of target game/app
            "settings_x": -1, "settings_y": -1,
            "pinned_mode": False,
            "send_mode": "enter",  # "enter" = fast keyboard, "mouse" = click on chat
            "favorite_colors": ["", "", "", "", "", ""],  # 6 favorite color slots
            "exe_path": "",  # مسار الـ exe للتحديث التلقائي
            # ═══════════════════════════════════════════════════════════════
            # إعدادات كشف الشات التلقائي
            # ═══════════════════════════════════════════════════════════════
            "chat_open_color": "",       # لون الشات المفتوح (hex)
            "chat_closed_color": "",     # لون الشات المغلق (hex)
            "chat_detect_x": -1,         # إحداثي X للكشف
            "chat_detect_y": -1,         # إحداثي Y للكشف
            "chat_detect_enabled": False, # تفعيل الكشف التلقائي
            "chat_open_enters": 0,       # عدد Enter عند الشات مفتوح (0 = لا شيء)
            "chat_closed_enters": 1      # عدد Enter عند الشات مغلق (1 = فتح فقط)
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.defaults, **json.load(f)}
            except:
                pass
        return self.defaults.copy()

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Config Save Error: {e}")

    def get(self, key):
        return self.config.get(key, self.defaults[key])

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

CONFIG = ConfigManager()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(400, 500)
        self.drag_pos = None
        self.setup_ui()
        self.load_settings()
        
        # Apply WS_EX_NOACTIVATE after window is created
        QTimer.singleShot(0, self.apply_no_activate)
    
    def apply_no_activate(self):
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | WS_EX_NOACTIVATE)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = QFrame()
        self.frame.setObjectName("SettingsFrame")
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setSpacing(12)
        frame_layout.setContentsMargins(20, 20, 20, 20)

        # Header - RTL: Close on left, Title on right
        header = QHBoxLayout()
        btn_close = QPushButton("✖")
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,30); border: none; border-radius: 5px; font-size: 14px; }
            QPushButton:hover { background: rgba(220, 60, 60, 0.8); color: white; }
        """)
        title = QLabel("الإعدادات ⚙️")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header.addWidget(btn_close)
        header.addStretch()
        header.addWidget(title)
        frame_layout.addLayout(header)

        # Helper for Sliders - RTL: Text (right), Slider (middle), Number (left)
        def add_slider(label_text, min_val, max_val, config_key, callback=None):
            container = QWidget()
            l = QHBoxLayout(container)
            l.setContentsMargins(0,0,0,0)
            l.setSpacing(8)
            
            # Number label (left) - fixed width
            val_lbl = QLabel("0")
            val_lbl.setFixedWidth(35)
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
            val_lbl.setStyleSheet("color: #3498db; font-weight: bold;")
            
            # Slider (middle) - stretches to fill space, inverted for RTL
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setInvertedAppearance(True)  # Start from right, go to left
            slider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            slider.setSingleStep(1)
            slider.setPageStep(1)
            
            # Text label (right) - fits content, no minimum width
            lbl = QLabel(label_text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            def on_change(val):
                val_lbl.setText(str(val))
                CONFIG.set(config_key, val)
                if callback: callback()
                self.update_style()
                
            slider.valueChanged.connect(on_change)
            
            # RTL order: Number - Slider - Text
            l.addWidget(val_lbl, 0)  # 0 = don't stretch
            l.addWidget(slider, 1)   # 1 = stretch to fill
            l.addWidget(lbl, 0)      # 0 = don't stretch (fit content)
            frame_layout.addWidget(container)
            return slider, val_lbl

        self.sl_bg, self.lbl_bg = add_slider("شفافية الخلفية", 2, 255, 'bg_opacity', self.parent().apply_settings)
        self.sl_txt, self.lbl_txt = add_slider("شفافية النص", 50, 255, 'text_opacity', self.parent().apply_settings)
        self.sl_set, self.lbl_set = add_slider("شفافية الإعدادات", 100, 255, 'settings_opacity')
        self.sl_font, self.lbl_font = add_slider("حجم الخط", 14, 40, 'font_size', self.parent().apply_settings)
        self.sl_line_end, self.lbl_line_end = add_slider("نهاية السطر الأول", 0, 300, 'first_line_end', self.parent().apply_settings)

        # Colors
        frame_layout.addWidget(QLabel("🎨 الألوان", styleSheet="font-weight: bold; font-size: 15px; margin-top: 10px;"))
        colors = QHBoxLayout()
        self.btn_bg = QPushButton("لون الخلفية")
        self.btn_bg.setMinimumHeight(40)
        self.btn_bg.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_bg.clicked.connect(lambda: self.pick_color('bg'))
        
        self.btn_txt = QPushButton("لون النص")
        self.btn_txt.setMinimumHeight(40)
        self.btn_txt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_txt.clicked.connect(lambda: self.pick_color('txt'))
        
        colors.addWidget(self.btn_bg)
        colors.addWidget(self.btn_txt)
        frame_layout.addLayout(colors)
        self.update_color_buttons()

        # Location - Olive bubble style
        frame_layout.addWidget(QLabel("📍 موقع الكتابة", styleSheet="font-weight: bold; font-size: 15px; margin-top: 10px;"))
        self.lbl_loc = QLabel("غير محدد")
        self.lbl_loc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_loc.setStyleSheet("""
            background: rgba(74, 95, 53, 0.55);
            color: #d4e8c0;
            border: 2px solid #6a8f55;
            border-radius: 14px;
            padding: 10px;
            font-size: 15px;
        """)
        frame_layout.addWidget(self.lbl_loc)
        
        self.btn_reset_loc = QPushButton("إعادة تعيين موقع الشات")
        self.btn_reset_loc.setMinimumHeight(40)
        self.btn_reset_loc.clicked.connect(self.reset_location)
        self.btn_reset_loc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset_loc.setStyleSheet("""
            QPushButton {
                background: rgba(200, 60, 60, 0.85);
                color: #ffe0e0;
                border: 2px solid #e06060;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 15px;
            }
            QPushButton:hover {
                background: rgba(200, 60, 60, 0.65);
            }
        """)
        frame_layout.addWidget(self.btn_reset_loc)
        
        frame_layout.addWidget(QLabel("اضغط على الزر أعلاه لتغيير الموقع", styleSheet="color: #888; font-size: 12px;"))
        # Send Mode Selection
        frame_layout.addWidget(QLabel("📧 طريقة الإرسال", styleSheet="font-weight: bold; font-size: 15px; margin-top: 10px;"))
        
        send_mode_container = QWidget()
        send_mode_layout = QHBoxLayout(send_mode_container)
        send_mode_layout.setContentsMargins(0, 0, 0, 0)
        send_mode_layout.setSpacing(8)
        
        # Get icons path
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(script_dir, 'Icons')
        
        # Enter button with PNG icon - RTL: text on right, icon on left
        self.btn_enter_mode = QPushButton("لوحة المفاتيح  ")
        self.btn_enter_mode.setMinimumHeight(40)
        self.btn_enter_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_enter_mode.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Text first, then icon
        enter_icon = os.path.join(icons_dir, 'Enter.png')
        if os.path.exists(enter_icon):
            self.btn_enter_mode.setIcon(QIcon(enter_icon))
            self.btn_enter_mode.setIconSize(QSize(24, 24))
        self.btn_enter_mode.clicked.connect(lambda: self.set_send_mode('enter'))
        
        # Mouse button with PNG icon - RTL: text on right, icon on left
        self.btn_mouse_mode = QPushButton("زر الفأرة  ")
        self.btn_mouse_mode.setMinimumHeight(40)
        self.btn_mouse_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mouse_mode.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Text first, then icon
        mouse_icon = os.path.join(icons_dir, 'Mouse.png')
        if os.path.exists(mouse_icon):
            self.btn_mouse_mode.setIcon(QIcon(mouse_icon))
            self.btn_mouse_mode.setIconSize(QSize(24, 24))
        self.btn_mouse_mode.clicked.connect(lambda: self.set_send_mode('mouse'))
        
        send_mode_layout.addWidget(self.btn_enter_mode)
        send_mode_layout.addWidget(self.btn_mouse_mode)
        frame_layout.addWidget(send_mode_container)
        
        self.lbl_send_mode = QLabel("")
        self.lbl_send_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_send_mode.setStyleSheet("color: #888; font-size: 11px;")
        frame_layout.addWidget(self.lbl_send_mode)

        layout.addWidget(self.frame)
        self.update_style()

    def update_color_buttons(self):
        bg = CONFIG.get('bg_color')
        txt = CONFIG.get('text_color')
        
        # Calculate contrasting text color (light or dark based on background)
        def get_text_color(hex_color):
            c = QColor(hex_color)
            brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
            return "#1a1a1a" if brightness > 128 else "#f0f0f0"
        
        # Calculate border color (slightly darker and more visible)
        def get_border_color(hex_color):
            c = QColor(hex_color)
            return f"rgba({max(0,c.red()-30)}, {max(0,c.green()-30)}, {max(0,c.blue()-30)}, 255)"
        
        # Bubble style for bg button - Brighter colors
        c = QColor(bg)
        self.btn_bg.setStyleSheet(f"""
            QPushButton {{
                background: rgba({c.red()}, {c.green()}, {c.blue()}, 220);
                color: {get_text_color(bg)};
                border: 2px solid {get_border_color(bg)};
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: rgba({c.red()}, {c.green()}, {c.blue()}, 180);
            }}
        """)
        
        # Bubble style for txt button - Brighter colors
        c = QColor(txt)
        self.btn_txt.setStyleSheet(f"""
            QPushButton {{
                background: rgba({c.red()}, {c.green()}, {c.blue()}, 220);
                color: {get_text_color(txt)};
                border: 2px solid {get_border_color(txt)};
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: rgba({c.red()}, {c.green()}, {c.blue()}, 180);
            }}
        """)

    def update_style(self):
        op = CONFIG.get('settings_opacity')
        self.frame.setStyleSheet(f"""
            QFrame#SettingsFrame {{
                background-color: rgba(20, 20, 20, {op});
                border: 1px solid #444;
                border-radius: 10px;
            }}
            QLabel {{ color: white; font-family: 'Segoe UI'; font-size: 15px; }}
            QSlider::handle:horizontal {{ background: #3498db; width: 16px; margin: -6px 0; border-radius: 8px; }}
            QSlider::groove:horizontal {{ background: #444; height: 4px; border-radius: 2px; }}
            QPushButton {{ background: rgba(255,255,255,30); color: white; border: none; border-radius: 5px; font-size: 14px; }}
            QPushButton:hover {{ background: rgba(255,255,255,50); }}
        """)

    def load_settings(self):
        self.sl_bg.setValue(CONFIG.get('bg_opacity'))
        self.sl_txt.setValue(CONFIG.get('text_opacity'))
        self.sl_set.setValue(CONFIG.get('settings_opacity'))
        self.sl_font.setValue(CONFIG.get('font_size'))
        self.sl_line_end.setValue(CONFIG.get('first_line_end'))
        self.update_loc_display()
        self.update_send_mode_buttons()

    def pick_color(self, target):
        try:
            # Close existing picker if open
            if hasattr(self, '_color_picker') and self._color_picker:
                self._color_picker.close()
                self._color_picker = None
            
            curr = QColor(CONFIG.get('bg_color' if target == 'bg' else 'text_color'))
            opacity = CONFIG.get('settings_opacity')
            
            # Create picker as Tool (doesn't steal focus like Popup)
            picker = QFrame(self)
            picker.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
            picker.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self._color_picker = picker
            
            # Container with visible border (parent is transparent)
            container = QFrame(picker)
            container.setObjectName("ColorContainer")
            container.setStyleSheet(f"""
                QFrame#ColorContainer {{
                    background-color: rgba(30, 30, 30, {opacity});
                    border-radius: 8px;
                    border: 2px solid #888;
                }}
            """)
            
            picker_layout = QVBoxLayout(picker)
            picker_layout.setContentsMargins(0, 0, 0, 0)
            picker_layout.addWidget(container)
            
            main_layout = QVBoxLayout(container)
            main_layout.setContentsMargins(8, 8, 8, 8)
            main_layout.setSpacing(4)
            
            def on_color_click(color):
                picker.close()
                self._color_picker = None
                CONFIG.set('bg_color' if target == 'bg' else 'text_color', color)
                self.update_color_buttons()
                self.parent().apply_settings()
            
            # Basic colors - Windows style 8x6 grid (48 colors)
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
            
            # Size and position - above the clicked button
            picker.setFixedSize(150, 125)
            
            target_btn = self.btn_txt if target == 'txt' else self.btn_bg
            btn_pos = target_btn.mapToGlobal(QPoint(0, 0))
            # Center above the button
            picker.move(btn_pos.x() + (target_btn.width() // 2) - 75, btn_pos.y() - 130)
            
            picker.show()
            
            # Apply no-activate after show to prevent fullscreen exit
            hwnd = int(picker.winId())
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            WS_EX_TOPMOST = 0x00000008
            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | WS_EX_NOACTIVATE | WS_EX_TOPMOST)
            
            # Timer to check for click outside
            def check_click_outside():
                if not picker.isVisible():
                    return
                # If mouse button pressed and not inside picker
                if win32api.GetAsyncKeyState(0x01) < 0:  # Left mouse button
                    cursor = QCursor.pos()
                    picker_rect = picker.geometry()
                    if not picker_rect.contains(cursor):
                        picker.close()
                        self._color_picker = None
                        return
                QTimer.singleShot(100, check_click_outside)
            
            QTimer.singleShot(200, check_click_outside)
            
        except Exception as e:
            print(f"[COLOR] Error: {e}")

    def update_loc_display(self):
        x, y = CONFIG.get('game_click_x'), CONFIG.get('game_click_y')
        game_name = CONFIG.get('game_name')
        if x != -1:
            if game_name:
                self.lbl_loc.setText(f"✅ {game_name}\nX: {x}, Y: {y}")
            else:
                self.lbl_loc.setText(f"✅ X: {x}, Y: {y}")
            self.lbl_loc.setStyleSheet("border: 1px solid #2ecc71; padding: 10px; border-radius: 5px; color: #2ecc71;")
        else:
            self.lbl_loc.setText("غير محدد")
            self.lbl_loc.setStyleSheet("border: 1px dashed #666; padding: 10px; border-radius: 5px; color: #e74c3c;")
    
    def reset_location(self):
        """Reset saved location so user can set a new one"""
        CONFIG.set('game_click_x', -1)
        CONFIG.set('game_click_y', -1)
        self.update_loc_display()
        print("=" * 60)
        print("✓ Location reset!")
        print("✓ Close settings and press Insert to set new location")
        print("=" * 60)
    
    def set_send_mode(self, mode):
        """Set the send mode (enter or mouse)"""
        CONFIG.set('send_mode', mode)
        self.update_send_mode_buttons()
        print(f"[SETTINGS] Send mode changed to: {mode}")
    
    def update_send_mode_buttons(self):
        """Update send mode button styles based on current selection"""
        current_mode = CONFIG.get('send_mode')
        
        # Active button style - Bright Blue bubble with visible border
        active_style = """
            QPushButton {
                background: rgba(52, 120, 220, 0.85);
                color: #ffffff;
                border: 2px solid #60a0e0;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 15px;
            }
            QPushButton:hover {
                background: rgba(52, 120, 220, 0.65);
            }
        """
        # Inactive button style - Dim Blue bubble with visible border
        inactive_style = """
            QPushButton {
                background: rgba(52, 120, 220, 0.35);
                color: #d0e8ff;
                border: 2px solid #5090c0;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 15px;
            }
            QPushButton:hover {
                background: rgba(52, 120, 220, 0.50);
            }
        """
        
        if current_mode == 'enter':
            self.btn_enter_mode.setStyleSheet(active_style)
            self.btn_mouse_mode.setStyleSheet(inactive_style)
            self.lbl_send_mode.setText("سريع + ذكي - للألعاب التي تستجيب لـ Enter")
        else:
            self.btn_enter_mode.setStyleSheet(inactive_style)
            self.btn_mouse_mode.setStyleSheet(active_style)
            self.lbl_send_mode.setText("يضغط على موقع الشات - للألعاب التي تحتاج ماوس")

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(e.globalPosition().toPoint() - self.drag_pos)
    
    def mouseReleaseEvent(self, e):
        if self.drag_pos:
            # Save position after dragging
            CONFIG.set('settings_x', self.x())
            CONFIG.set('settings_y', self.y())
            self.drag_pos = None
    
    def closeEvent(self, e):
        # Close color picker if open
        if hasattr(self, '_color_picker') and self._color_picker:
            self._color_picker.close()
            self._color_picker = None
        # Save position when closing
        CONFIG.set('settings_x', self.x())
        CONFIG.set('settings_y', self.y())
        super().closeEvent(e)

# =====================================
# MenuItemWidget - عنصر واحد في القائمة المنبثقة
# =====================================
# 🎨 للتخصيص: غيّر الألوان والخطوط هنا
# =====================================
class MenuItemWidget(QWidget):
    def __init__(self, arabic, english, shortcut, callback, menu, text_color, font_size):
        super().__init__()
        self.callback = callback
        self.menu = menu
        self.text_color = text_color
        self.font_size = font_size  # حفظ حجم الخط للاستخدام لاحقاً
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        # ┌─────────────────────────────────────────────────────┐
        # │ 📐 المسافات الداخلية: (يسار, أعلى, يمين, أسفل)      │
        # │ غيّر الأرقام لتعديل المسافات                        │
        # └─────────────────────────────────────────────────────┘
        layout.setContentsMargins(15, 8, 15, 8)  # المسافات الداخلية
        layout.setSpacing(15)  # المسافة بين العناصر
        
        # ┌─────────────────────────────────────────────────────┐
        # │ 🔤 النص الإنجليزي + الاختصار (يسار)                 │
        # │ ──────────────────────────────────────────────────  │
        # │ color: لون النص (rgba أو hex)                       │
        # │ font-family: نوع الخط                               │
        # │ font-size: حجم الخط                                 │
        # │ font-weight: سمك الخط (400=عادي, 600=سميك, 700=bold)│
        # └─────────────────────────────────────────────────────┘
        eng_text = f"{english} {shortcut}" if shortcut else english
        self.lbl_eng = QLabel(eng_text)
        self.lbl_eng.setStyleSheet(f"""
            color: rgba(180, 180, 180, 200);  /* 🎨 لون النص الإنجليزي - رمادي فاتح */
            font-family: 'Segoe UI';          /* ✏️ نوع الخط */
            font-size: {max(11, font_size-3)}px;  /* 📏 حجم الخط */
            font-weight: 400;                 /* ⚖️ سمك الخط */
        """)
        self.lbl_eng.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # ┌─────────────────────────────────────────────────────┐
        # │ 🔤 النص العربي (يمين) - اللون الذهبي                │
        # │ ──────────────────────────────────────────────────  │
        # │ #e6a84a = ذهبي/برتقالي                             │
        # │ غيّره لأي لون تريد (مثل #FFFF00 للأصفر)            │
        # └─────────────────────────────────────────────────────┘
        self.lbl_ar = QLabel(arabic)
        self.lbl_ar.setStyleSheet(f"""
            color: #e6a84a;                   /* 🎨 لون النص العربي - ذهبي */
            font-family: 'Segoe UI';          /* ✏️ نوع الخط */
            font-size: {font_size-3}px;         /* 📏 حجم الخط */
            font-weight: 400;                 /* ⚖️ سمك الخط - سميك */
        """)
        self.lbl_ar.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        layout.addWidget(self.lbl_eng)
        layout.addStretch()
        layout.addWidget(self.lbl_ar)
        
        # التصميم الافتراضي (بدون hover)
        self.setStyleSheet("background-color: transparent; border-radius: 8px;")
        
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.menu.close()
            if self.callback: self.callback()
            
    def enterEvent(self, e):
        # ┌─────────────────────────────────────────────────────┐
        # │ 🌈 تأثير Hover - عند تمرير الماوس فوق العنصر       │
        # │ ──────────────────────────────────────────────────  │
        # │ rgba(70, 130, 200, 80) = اللون الأزرق الشفاف       │
        # │ border-left: شريط جانبي ملون                       │
        # │ #4a90d9 = لون الشريط الأزرق                        │
        # └─────────────────────────────────────────────────────┘
        # تغيير لون النص العربي عند hover
        self.lbl_ar.setStyleSheet(f"""
            color: #fcb953;                       /* 🎨 لون النص العربي عند Hover */
            font-family: 'Segoe UI';
            font-size: {self.font_size-3}px;
            font-weight: 600;
        """)
        
        # ┌─────────────────────────────────────────────────────┐
        # │ 🔤 تغيير لون النص الإنجليزي عند Hover              │
        # │ ──────────────────────────────────────────────────  │
        # │ color: لون النص (hex أو rgba)                      │
        # │ font-size: حجم الخط                                │
        # │ font-weight: سمك الخط                              │
        # └─────────────────────────────────────────────────────┘
        self.lbl_eng.setStyleSheet(f"""
            color: rgba(220, 220, 220, 255);     /* 🎨 لون النص الإنجليزي عند Hover - رمادي فاتح */
            font-family: 'Segoe UI';              /* ✏️ نوع الخط */
            font-size: {max(11, self.font_size-3)}px;  /* 📏 حجم الخط */
            font-weight: 600;                     /* ⚖️ سمك الخط */
        """)
        
    def leaveEvent(self, e):
        # عند خروج الماوس - إعادة الألوان الأصلية
        self.setStyleSheet("background-color: transparent; border-radius: 8px;")
        
        # إعادة اللون الذهبي للنص العربي
        self.lbl_ar.setStyleSheet(f"""
            color: #e6a84a;                       /* 🎨 إعادة اللون الذهبي */
            font-family: 'Segoe UI';
            font-size: {self.font_size-3}px;
            font-weight: 400;
        """)
        
        # ┌─────────────────────────────────────────────────────┐
        # │ 🔤 إعادة لون النص الإنجليزي الأصلي                 │
        # └─────────────────────────────────────────────────────┘
        self.lbl_eng.setStyleSheet(f"""
            color: rgba(180, 180, 180, 200);     /* 🎨 لون النص الإنجليزي - رمادي */
            font-family: 'Segoe UI';              /* ✏️ نوع الخط */
            font-size: {max(11, self.font_size-3)}px;  /* 📏 حجم الخط */
            font-weight: 400;                     /* ⚖️ سمك الخط */
        """)

# =====================================
# CustomContextMenu - القائمة المنبثقة (كلك يمين)
# =====================================
# 🎨 للتخصيص: غيّر ألوان الخلفية والحدود هنا
# =====================================
class CustomContextMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Read Config
        self.text_color = CONFIG.get('text_color') # Hex string
        self.font_size = CONFIG.get('font_size')
        bg_opacity = CONFIG.get('bg_opacity')  # قراءة الشفافية فقط
        
        # ┌─────────────────────────────────────────────────────┐
        # │ 🎨 استايل القائمة المنبثقة                         │
        # │ ──────────────────────────────────────────────────  │
        # │ غيّر الألوان هنا لتخصيص مظهر القائمة               │
        # └─────────────────────────────────────────────────────┘
        self.setStyleSheet(f"""
            QMenu {{
                /* ┌─────────────────────────────────────────┐
                   │ 🌈 تدرج خلفية القائمة                   │
                   │ rgba(35, 40, 55, 245) = اللون الداكن    │
                   │ غيّر الأرقام الثلاثة الأولى للون       │
                   │ الرقم الرابع = الشفافية (0-255)         │
                   └─────────────────────────────────────────┘ */
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 36, 54, {bg_opacity}),   /* 🎨 لون البداية (أعلى) */
                    stop:1 rgba(20, 26, 44, {bg_opacity})    /* 🎨 لون النهاية (أسفل) */
                );
                
                /* ┌─────────────────────────────────────────┐
                   │ 📐 الحدود والاستدارة                     │
                   │ rgba(100, 150, 220, 0.3) = أزرق فاتح شفاف│
                   │ border-radius: استدارة الحواف           │
                   └─────────────────────────────────────────┘ */
                border: 1px solid rgba(100, 150, 220, 0.3);  /* 🎨 لون الحدود */
                border-radius: 12px;                          /* 📐 استدارة */
                padding: 8px 5px;                             /* 📐 المسافات */
            }}
            
            /* ┌─────────────────────────────────────────────────────┐
               │ 🔲 الفاصل بين عناصر القائمة                        │
               │ rgba(100, 150, 220, 0.4) = لون الفاصل الأزرق       │
               └─────────────────────────────────────────────────────┘ */
            QMenu::separator {{
                height: 1px;                                  /* سمك الفاصل */
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent,
                    stop:0.5 rgba(100, 150, 220, 0.4),        /* 🎨 لون الفاصل */
                    stop:1 transparent
                );
                margin: 6px 15px;                             /* المسافات حول الفاصل */
            }}
        """)
        
        # Apply WS_EX_NOACTIVATE
        QTimer.singleShot(0, self.apply_no_activate)
        
        # Timer for global click detection (to close menu when clicking outside)
        self.click_timer = QTimer(self)
        self.click_timer.timeout.connect(self.check_global_click)
        self.ignore_initial_click = True

    def add_custom_action(self, arabic, english, shortcut, callback):
        action = QWidgetAction(self)
        widget = MenuItemWidget(arabic, english, shortcut, callback, self, self.text_color, self.font_size)
        action.setDefaultWidget(widget)
        self.addAction(action)

    def apply_no_activate(self):
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | WS_EX_NOACTIVATE)

    def showEvent(self, event):
        super().showEvent(event)
        self.apply_no_activate()
        self.ignore_initial_click = True
        self.click_timer.start(100)
        
    def hideEvent(self, event):
        super().hideEvent(event)
        self.click_timer.stop()

    def check_global_click(self):
        # Check Left or Right mouse button
        l_down = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000
        r_down = win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000
        
        if not l_down and not r_down:
            self.ignore_initial_click = False
            return

        if self.ignore_initial_click:
            return

        # Mouse is down, check if it's inside the menu
        pt = win32api.GetCursorPos()
        rect = self.geometry()
        # rect is QRect, pt is (x,y)
        # Check if pt is inside rect
        if not (rect.x() <= pt[0] <= rect.x() + rect.width() and 
                rect.y() <= pt[1] <= rect.y() + rect.height()):
            self.close()

class NativeTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.context_menu = None
        
        # Custom Caret (Cursor)
        self.caret_timer = QTimer(self)
        self.caret_timer.timeout.connect(self.blink_caret)
        self.caret_visible = True
        self.caret_timer.start(500)  # Blink every 500ms
        
        # Arabic mode flag
        self.is_arabic_mode = True  # Default to Arabic

    def show_context_menu(self, pos):
        if self.context_menu:
            self.context_menu.close()
            self.context_menu = None
            
        menu = CustomContextMenu(self)
        self.context_menu = menu
        
        # Add actions with custom widget
        menu.add_custom_action("تراجع", "Undo", "Ctrl+Z", self.undo)
        menu.add_custom_action("إعادة", "Redo", "Ctrl+Y", self.redo)
        
        # Separator
        sep = QAction(self)
        sep.setSeparator(True)
        menu.addAction(sep)
        
        menu.add_custom_action("قص", "Cut", "Ctrl+X", self.cut)
        menu.add_custom_action("نسخ", "Copy", "Ctrl+C", self.copy)
        menu.add_custom_action("لصق", "Paste", "Ctrl+V", self.custom_paste)
        
        sep2 = QAction(self)
        sep2.setSeparator(True)
        menu.addAction(sep2)
        
        menu.add_custom_action("تحديد الكل", "Select All", "Ctrl+A", self.selectAll)
        
        # Smart positioning - avoid screen edges
        global_pos = self.mapToGlobal(pos)
        
        # Get screen geometry
        screen = QApplication.primaryScreen().geometry()
        
        # Get menu size (estimate if not shown yet)
        menu.adjustSize()
        menu_width = menu.width()
        menu_height = menu.height()
        
        # Calculate adjusted position
        adjusted_x = global_pos.x()
        adjusted_y = global_pos.y()
        
        # Check if menu goes off right edge
        if adjusted_x + menu_width > screen.right():
            adjusted_x = screen.right() - menu_width - 10
        
        # Check if menu goes off bottom edge - OPEN UPWARD
        if adjusted_y + menu_height > screen.bottom():
            adjusted_y = global_pos.y() - menu_height
        
        # Check if menu goes off top edge
        if adjusted_y < screen.top():
            adjusted_y = screen.top() + 10
        
        # Check if menu goes off left edge
        if adjusted_x < screen.left():
            adjusted_x = screen.left() + 10
        
        menu.move(adjusted_x, adjusted_y)
        menu.show()

    def blink_caret(self):
        self.caret_visible = not self.caret_visible
        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.caret_visible and not self.hasFocus():
            painter = QPainter(self.viewport())
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            rect = self.cursorRect()
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

    def set_arabic_mode(self, enabled):
        """Set Arabic input mode"""
        self.is_arabic_mode = enabled
    
    def custom_paste(self):
        """لصق مخصص - يفضل Windows clipboard دائماً"""
        try:
            import pyperclip
            parent = self.parent_window
            win_clip = pyperclip.paste()
            
            if win_clip:
                # إذا المحتوى مختلف عن آخر رسالة مُرسلة، استخدمه
                if parent and hasattr(parent, '_last_sent_message'):
                    if win_clip != parent._last_sent_message:
                        self.insertPlainText(win_clip)
                        print(f"[PASTE] Windows clipboard: {win_clip[:30]}...")
                        return
                else:
                    # لا يوجد parent أو لا توجد رسالة سابقة
                    self.insertPlainText(win_clip)
                    print(f"[PASTE] Windows (no parent): {win_clip[:30]}...")
                    return
            
            # Fallback: استخدم internal_clipboard إذا كان Windows clipboard فارغ أو مطابق للرسالة المُرسلة
            if parent and hasattr(parent, '_internal_clipboard') and parent._internal_clipboard:
                self.insertPlainText(parent._internal_clipboard)
                print(f"[PASTE] Internal fallback: {parent._internal_clipboard[:30]}...")
                
        except Exception as e:
            print(f"[PASTE] Error: {e}")
            super().paste()
    
    def get_arabic_char(self, char, shift_pressed):
        """Map English character to Arabic with correct keyboard layout"""
        
        # Standard Arabic keyboard layout (no shift)
        arabic_map = {
            # Numbers row (Arabic-Indic numerals when typing in Arabic)
            '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
            '6': '6', '7': '7', '8': '8', '9': '9', '0': '0',
            '-': '-', '=': '=',
            
            # Top row (QWERTY -> Arabic)
            'q': 'ض', 'w': 'ص', 'e': 'ث', 'r': 'ق', 't': 'ف',
            'y': 'غ', 'u': 'ع', 'i': 'ه', 'o': 'خ', 'p': 'ح',
            '[': 'ج', ']': 'د',
            
            # Middle row (ASDF -> Arabic)
            'a': 'ش', 's': 'س', 'd': 'ي', 'f': 'ب', 'g': 'ل',
            'h': 'ا', 'j': 'ت', 'k': 'ن', 'l': 'م', ';': 'ك', "'": 'ط',
            
            # Bottom row (ZXCV -> Arabic)
            'z': 'ئ', 'x': 'ء', 'c': 'ؤ', 'v': 'ر', 'b': 'لا',
            'n': 'ى', 'm': 'ة', ',': 'و', '.': 'ز', '/': 'ظ',
            
            # Special keys
            '`': 'ذ', '\\': '\\'  # Backslash stays as is
        }
        
        # Shifted Arabic (Shift + key)
        arabic_shift_map = {
            # Numbers row with shift -> symbols
            '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
            '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
            '-': '_', '=': '+',
            
            # Top row shifted (Arabic diacritics and symbols)
            'q': 'َ',   # Fatha
            'w': 'ً',   # Tanween Fath
            'e': 'ُ',   # Damma
            'r': 'ٌ',   # Tanween Damm
            't': 'لإ',  # Lam with Hamza below
            'y': 'إ',   # Hamza on alif below
            'u': "'",   # APOSTROPHE (ASCII 39)
            'i': '÷',   # Division
            'o': '×',   # Multiplication
            'p': '؛',   # Arabic semicolon
            '[': '<',
            ']': '>',
            
            # Middle row shifted
            'a': 'ِ',   # Kasra
            's': 'ٍ',   # Tanween Kasr
            'd': ']',   # Right bracket
            'f': '[',   # Left bracket
            'g': 'لأ',  # Lam with Hamza above
            'h': 'أ',   # Hamza on alif
            'j': 'ـ',   # Tatweel (Arabic Tatweel U+0640)
            'k': '،',   # Arabic comma
            'l': '/',   # Forward slash
            ';': ':',   # Colon
            "'": '"',   # Double quote
            
            # Bottom row shifted
            'z': '~',   # Tilde
            'x': 'ْ',   # Sukun
            'c': '}',   # Right brace
            'v': '{',   # Left brace
            'b': 'لآ',  # Lam with Mad
            'n': 'آ',   # Alif with Mad
            'm': "'",   # APOSTROPHE (ASCII 39)
            ',': '<',   # Less than
            '.': '>',   # Greater than
            '/': '؟',   # Arabic question mark
            
            # Special shifted
            '`': 'ّ',   # Shadda
            '\\': '|'   # Pipe
        }
        
        # Convert to lowercase for lookup
        char_lower = char.lower()
        
        # If shift is pressed, check shift map first
        if shift_pressed:
            if char_lower in arabic_shift_map:
                return arabic_shift_map[char_lower]
            # If not in shift map, fallback to normal map
            elif char_lower in arabic_map:
                return arabic_map[char_lower]
        else:
            # No shift, use normal map
            if char_lower in arabic_map:
                return arabic_map[char_lower]
        
        # Return None for unmapped keys (will be handled as English)
        return None
    
    def keyPressEvent(self, event):
        # Handle Enter key for sending
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Shift+Enter = new line
                super().keyPressEvent(event)
            else:
                # Enter = send message
                self.parent_window.send_text()
            return
        
        # Get the text from the event
        text = event.text()
        modifiers = event.modifiers()
        
        # Let Qt handle special keys naturally (arrows, function keys, Delete, Home, etc.)
        if not text or len(text) != 1:
            super().keyPressEvent(event)
            return
        
        # Check if this is a printable ASCII character
        char = text[0]
        if not (32 <= ord(char) <= 126):  # Not printable ASCII
            super().keyPressEvent(event)
            return
        
        # If in Arabic mode, convert to Arabic
        if self.is_arabic_mode:
            shift_pressed = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
            arabic_char = self.get_arabic_char(char, shift_pressed)
            if arabic_char:
                self.insertPlainText(arabic_char)
                return
        
        # Default: let Qt handle it naturally (English mode or unmapped keys)
        super().keyPressEvent(event)

class OverlayWindow(QMainWindow):
    lang_changed = pyqtSignal(bool)  # Signal for language mode change
    # Thread-safe signals for keyboard events
    insert_text_signal = pyqtSignal(str)
    backspace_signal = pyqtSignal()
    send_text_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.processor = ArabicProcessor()
        self.is_arabic_mode = True  # True = Arabic, False = English
        self.last_toggle_time = 0  # Debounce language toggle
        self._buttons_visible = False  # Auto-hide button state
        self._buttons_locked = False  # True when dragging/resizing/hovering on buttons
        self._internal_clipboard = ""  # Internal clipboard (user's copied content)
        self._last_sent_message = ""   # Track last message WE sent (to distinguish from user copies)
        
        # Connect thread-safe signals
        self.insert_text_signal.connect(self.on_insert_text)
        self.backspace_signal.connect(self.on_backspace)
        self.send_text_signal.connect(self.send_text)
        
        # Window Flags - Allow focus for typing, fullscreen protection via WS_EX_NOACTIVATE
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Geometry
        self.setGeometry(CONFIG.get('x'), CONFIG.get('y'), CONFIG.get('w'), CONFIG.get('h'))
        
        # Central Widget
        self.central_widget = QWidget()
        
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Absolute zero margins
        self.layout.setSpacing(0)  # No spacing between items
        
        # Text Editor (full height)
        self.text_edit = NativeTextEdit(self)
        self.text_edit.setFrameStyle(QFrame.Shape.NoFrame)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Enable word wrap - prefer word boundaries, break long words if needed
        self.text_edit.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        # Style scrollbar to be on the RIGHT side
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Force scrollbar to RIGHT by using style sheet
        self.text_edit.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                min-height: 20px;
                border-radius: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.layout.addWidget(self.text_edit)
        
        # Install event filter on text edit to capture mouse events at edges
        self.text_edit.installEventFilter(self)
        self.text_edit.viewport().installEventFilter(self)
        
        # Connect language mode to text edit
        self.lang_changed.connect(self.text_edit.set_arabic_mode)
        self.text_edit.set_arabic_mode(self.is_arabic_mode)
        
        self.apply_settings()
        
        # Hotkey
        self.loc_mode = False
        self.reload_hotkey()
        
        # Register language toggle hotkey (Alt+Shift)
        try:
            keyboard.add_hotkey('alt+shift', self.toggle_language)
        except:
            pass
        
        # Resize/Drag State
        self.resize_mode = None
        self.drag_pos = None
        self.resize_start_pos = None
        self.resize_start_geo = None
        
        # Timer to keep window on top in fullscreen games
        self._topmost_timer = QTimer(self)
        self._topmost_timer.timeout.connect(self._ensure_topmost)
        self._topmost_timer.start(100)  # Check every 100ms
        
        # Timer to detect fullscreen and auto-toggle
        self._fullscreen_check_timer = QTimer(self)
        self._fullscreen_check_timer.timeout.connect(self._check_fullscreen_toggle)
        self._fullscreen_check_timer.start(500)  # Check every 500ms
        self._last_foreground = 0
        
        # Initialize Ctrl+V fix (polling timer)
        self._init_ctrl_v_fix()
        
        # ========================================================================
        # INPUT STATE MACHINE - Pre-arm + Gate + Buffer System
        # ========================================================================
        # States: IDLE → ARMING → READY → SENDING → READY
        self._input_state = "IDLE"  # Current state
        self._keystroke_buffer = []  # Buffer for keys during ARMING (max 5)
        self._click_through_enabled = False  # For pin mode WS_EX_TRANSPARENT
        
        # تمييز التبديل التلقائي (ملء شاشة) عن التبديل بواسطة المستخدم
        self._auto_toggle_flag = False
        
        # Hook health timer - auto-recover if hooks break
        self._hook_health_timer = QTimer(self)
        self._hook_health_timer.setSingleShot(True)
        self._hook_health_timer.timeout.connect(self._ensure_hooks_ready)
        
        # Ready timer (fallback if no event arrives quickly)
        self._ready_timer = QTimer(self)
        self._ready_timer.setSingleShot(True)
        self._ready_timer.timeout.connect(self._mark_ready)
        
        # ========================================================================
        # SMART CHAT FOCUS - Detect mouse activity to know when Enter is needed
        # ========================================================================
        self._mouse_clicked_since_send = True  # Start true (need Enter for first message)
        self._init_mouse_tracker()
    
    def _init_mouse_tracker(self):
        """Poll mouse buttons to detect when user clicked (game interaction)"""
        self._mouse_tracker_timer = QTimer(self)
        self._mouse_tracker_timer.timeout.connect(self._check_mouse_click)
        self._mouse_tracker_timer.start(50)  # Check every 50ms
    
    def _check_mouse_click(self):
        """Check if mouse was clicked - ONLY when on target game (NOT on our app)"""
        # Initialize tracking variables
        if not hasattr(self, '_target_game_hwnd'):
            self._target_game_hwnd = 0
            self._was_on_target_game = True
        
        # Get current foreground window
        current_fg = ctypes.windll.user32.GetForegroundWindow()
        our_hwnd = int(self.winId()) if self.isVisible() else 0
        
        # Check game_click_x to know if location is set (target is saved in save_location)
        gx = CONFIG.get('game_click_x')
        if gx == -1:
            return  # Location not set yet, don't track
        
        # =====================================================
        # CHECK IF CURSOR IS ON OUR APP WINDOWS
        # This works even when our windows don't steal focus!
        # =====================================================
        cursor_on_our_app = False
        
        # Get cursor position
        cursor_pos = QCursor.pos()
        
        # Check if cursor is on our overlay
        if self.isVisible():
            our_rect = self.geometry()
            if our_rect.contains(cursor_pos):
                cursor_on_our_app = True
        
        # Check if cursor is on settings dialog
        if hasattr(self, 'settings_dlg') and self.settings_dlg and self.settings_dlg.isVisible():
            settings_rect = self.settings_dlg.geometry()
            if settings_rect.contains(cursor_pos):
                cursor_on_our_app = True
        
        # Check if cursor is on context menu (right-click menu)
        if hasattr(self, 'text_edit') and hasattr(self.text_edit, 'context_menu') and self.text_edit.context_menu:
            if self.text_edit.context_menu.isVisible():
                menu_rect = self.text_edit.context_menu.geometry()
                if menu_rect.contains(cursor_pos):
                    cursor_on_our_app = True
        
        # Check if cursor is on any of our buttons
        for btn_name in ['drag_handle', 'btn_settings', 'btn_pin']:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                if btn.isVisible():
                    btn_rect = btn.geometry()
                    if btn_rect.contains(cursor_pos):
                        cursor_on_our_app = True
                        break
        
        # Check if on target game (foreground is game and cursor NOT on our windows)
        on_target_game = (current_fg == self._target_game_hwnd and not cursor_on_our_app)
        
        # For focus logging - consider both game and our app as "on target"
        on_target = (current_fg == self._target_game_hwnd or current_fg == our_hwnd)
        if hasattr(self, '_was_on_target_game') and self._was_on_target_game != on_target:
            if on_target:
                print(f"[FOCUS] Returned to game (needs_enter={getattr(self, '_mouse_clicked_since_send', True)})")
            else:
                print(f"[FOCUS] Left game (needs_enter={getattr(self, '_mouse_clicked_since_send', True)})")
        
        # =====================================================
        # ONLY track mouse clicks when ON THE TARGET GAME
        # AND cursor is NOT on any of our windows!
        # =====================================================
        if on_target_game:
            VK_LBUTTON = 0x01   # كلك يسار
            VK_RBUTTON = 0x02   # كلك يمين
            VK_MBUTTON = 0x04   # ضغط عجلة الماوس
            left = ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000
            right = ctypes.windll.user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000
            middle = ctypes.windll.user32.GetAsyncKeyState(VK_MBUTTON) & 0x8000
            if left or right or middle:
                if not getattr(self, '_mouse_clicked_since_send', True):
                    print("[FOCUS] Mouse clicked on GAME (cursor not on our app) - needs_enter=True")
                self._mouse_clicked_since_send = True
        
        self._was_on_target_game = on_target
    
    def _init_ctrl_v_fix(self):
        """Initialize Ctrl+V polling timer for first-paste fix"""
        print("[STARTUP] Initializing Ctrl+V fix...")
        self._ctrl_v_timer = QTimer(self)
        self._ctrl_v_timer.timeout.connect(self._on_ctrl_v_poll)
        self._ctrl_v_timer.start(20)  # Poll every 20ms
        print("[STARTUP] Ctrl+V polling timer started")
    
    def _on_ctrl_v_poll(self):
        """Poll DLL for Ctrl+V flag"""
        # Use existing media_filter if available
        if hasattr(self, 'media_filter') and self.media_filter:
            # Always check to clear stale flags
            ctrl_v_pressed = self.media_filter.check_ctrl_v()
            # Only process if visible AND not during SENDING state
            if ctrl_v_pressed and self.isVisible() and self._input_state != "SENDING":
                print("[POLL] Ctrl+V detected!")
                self._do_paste()
    
    def _do_paste(self):
        """Do the actual paste from polling - user explicitly pressed Ctrl+V"""
        try:
            win_clip = pyperclip.paste()
            
            # Smart paste logic:
            # If Windows clipboard = what WE sent, use internal clipboard (user's original)
            # If Windows clipboard = something NEW, paste it
            
            if win_clip and win_clip != self._last_sent_message:
                # New content from Windows - paste it
                self.text_edit.insertPlainText(win_clip)
                self._internal_clipboard = win_clip
                print(f"[PASTE] Pasted NEW: {win_clip[:20]}...")
            elif self._internal_clipboard:
                # Windows has our sent message, use internal (user's original content)
                self.text_edit.insertPlainText(self._internal_clipboard)
                print(f"[PASTE] Pasted INTERNAL: {self._internal_clipboard[:20]}...")
            elif win_clip:
                # No internal, but Windows has something (even if we sent it)
                self.text_edit.insertPlainText(win_clip)
                print(f"[PASTE] Pasted: {win_clip[:20]}...")
            else:
                print("[PASTE] Nothing to paste (clipboard empty)")
            
            self.text_edit.ensureCursorVisible()
        except Exception as e:
            print(f"[PASTE] Error: {e}")
    
    # ========================================================================
    # PRE-ARM + GATE + BUFFER SYSTEM
    # ========================================================================
    
    def _arm_input(self):
        """تسليح الـ hook قبل الإظهار مع بوابة جاهزية."""
        self._input_state = "ARMING"
        self._keystroke_buffer.clear()
        
        # أوقف أي hook سابق
        self.stop_keyboard_hooks()
        
        # ابدأ hook جديد مع wrapper
        print("[INPUT] State: ARMING")
        
        # Media letter scan codes - handled by DLL
        self.media_letter_scans = {32, 46, 48, 16, 34, 25}
        
        # STRICT WHITELIST - typing scan codes
        self.typing_scan_codes = {
            17: 'w', 18: 'e', 19: 'r', 20: 't', 21: 'y', 22: 'u', 23: 'i', 24: 'o',
            30: 'a', 31: 's', 33: 'f', 35: 'h', 36: 'j', 37: 'k', 38: 'l',
            44: 'z', 45: 'x', 47: 'v', 49: 'n', 50: 'm',
            2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
            12: '-', 13: '=', 26: '[', 27: ']', 43: '\\', 39: ';', 40: "'", 51: ',', 52: '.', 53: '/',
            41: '`', 57: 'space', 14: 'backspace', 28: 'enter'
        }
        
        self.dll_scan_to_name = {32: 'd', 46: 'c', 48: 'b', 16: 'q', 34: 'g', 25: 'p'}
        
        self.nav_scan_codes = {
            75: 'left', 77: 'right', 72: 'up', 80: 'down',
            83: 'delete', 71: 'home', 79: 'end'
        }
        
        # Start DLL filter
        try:
            self.media_filter = get_filter()
            self.media_filter.load()
            self.media_filter.set_callback(self.on_dll_key_event)
            self.media_filter.start()
            self.media_filter.enable(True)
            print("[HOOK] DLL filter active (handles D,C,B,Q,G,P)")
        except Exception as e:
            print(f"[HOOK] DLL failed: {e}")
            self.typing_scan_codes.update({16: 'q', 25: 'p', 32: 'd', 34: 'g', 46: 'c', 48: 'b'})
        
        # Hook keyboard with wrapper
        try:
            self.keyboard_hook = keyboard.hook(self._hook_wrapper, suppress=True)
            print(f"[HOOK] Keyboard hook installed")
        except Exception as e:
            print(f"[HOOK] Failed: {e}")
        
        # مهلة أمان كـ fallback (300ms for lag tolerance)
        if not self._ready_timer.isActive():
            self._ready_timer.start(300)
    
    def _hook_wrapper(self, event):
        """Wrapper للـ hook - يعلن الجاهزية على أول حدث down أثناء ARMING."""
        # إعلان الجاهزية على أول حدث down أثناء ARMING
        if event.event_type == 'down' and self._input_state == "ARMING":
            if self._ready_timer.isActive():
                self._ready_timer.stop()
            self._mark_ready()
        return self.on_keyboard_event(event)
    
    def _mark_ready(self):
        """إعلان جاهزية الـ hook وإدخال أي أحرف مخزنة."""
        if self._input_state != "ARMING":
            return
        self._input_state = "READY"
        print(f"[INPUT] State: READY (buffered {len(self._keystroke_buffer)} keys)")
        
        # حقن الأحرف المخزنة بنفس الترتيب
        for char in self._keystroke_buffer:
            self.insert_text_signal.emit(char)
        self._keystroke_buffer.clear()
    
    def _atomic_show_focus(self):
        """إظهار + رفع + تركيز كعملية ذرية عند الجاهزية."""
        self.showNormal()
        # NOTE: Don't call activateWindow() - it steals focus from fullscreen games
        self.raise_()
        
        # Re-apply TOPMOST
        hwnd = int(self.winId())
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
        
        # تركيز عند الجاهزية فقط
        def focus_when_ready():
            if self._input_state == "READY":
                self.text_edit.setFocus()
            else:
                QTimer.singleShot(30, focus_when_ready)
        focus_when_ready()
    
    def _get_char_for_key(self, key_name):
        """تحويل اسم المفتاح إلى حرف حسب وضع اللغة."""
        if key_name in ['space', 'backspace', 'enter']:
            return None  # لا نخزن هذه في buffer
        
        shift = keyboard.is_pressed('shift')
        
        if self.is_arabic_mode:
            return self.text_edit.get_arabic_char(key_name, shift)
        else:
            # English mode
            if shift:
                shift_map = {
                    '1':'!', '2':'@', '3':'#', '4':'$', '5':'%', '6':'^',
                    '7':'&', '8':'*', '9':'(', '0':')', '-':'_', '=':'+',
                    '[':'{', ']':'}', '\\':'|', ';':':', "'":'"',
                    ',':'<', '.':'>', '/':'?'
                }
                if key_name in shift_map:
                    return shift_map[key_name]
                caps_lock = bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
                return key_name.lower() if caps_lock else key_name.upper()
            else:
                caps_lock = bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
                return key_name.upper() if caps_lock else key_name.lower()
    
    def _set_click_through(self, enabled: bool):
        """تفعيل/تعطيل نقر-شفاف للنافذة (WS_EX_TRANSPARENT)."""
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_TRANSPARENT = 0x00000020
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if enabled and not self._click_through_enabled:
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TRANSPARENT)
            self._click_through_enabled = True
            print("[PIN] Click-through enabled")
        elif not enabled and self._click_through_enabled:
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style & ~WS_EX_TRANSPARENT)
            self._click_through_enabled = False
            print("[PIN] Click-through disabled")
    
    
    def _ensure_topmost(self):
        """Re-apply TOPMOST flag periodically to handle fullscreen mode changes"""
        if self.isVisible():
            hwnd = int(self.winId())
            
            # Check if our window is NOT at the top of the z-order
            # Get the topmost window
            foreground = ctypes.windll.user32.GetForegroundWindow()
            
            # Add required extended styles (NOT WS_EX_LAYERED - PyQt6 handles this)
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            WS_EX_TOPMOST = 0x00000008
            # NOTE: WS_EX_LAYERED removed - PyQt6's WA_TranslucentBackground manages this
            required_style = WS_EX_NOACTIVATE | WS_EX_TOPMOST
            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            
            # If missing styles, re-apply
            if (current_style & required_style) != required_style:
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | required_style)
            
            # Force window position to topmost
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040
            SWP_FRAMECHANGED = 0x0020
            
            # More aggressive: use FRAMECHANGED to force refresh
            ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, 
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW | SWP_FRAMECHANGED)
    
    def _check_fullscreen_toggle(self):
        """Detect when fullscreen app takes over and auto-toggle to bring window back on top"""
        if not self.isVisible():
            return
        
        # Skip if toggle is already in progress OR if we're sending (avoid interference)
        if hasattr(self, '_fullscreen_toggling') and self._fullscreen_toggling:
            return
        if hasattr(self, '_input_state') and self._input_state == "SENDING":
            return
        
        # Get current foreground window
        foreground = ctypes.windll.user32.GetForegroundWindow()
        
        # If foreground changed to something else (not our window)
        hwnd = int(self.winId())
        if foreground != hwnd and foreground != self._last_foreground and self._last_foreground != 0:
            # DEBOUNCE: Prevent rapid toggling in busy games
            current_time = time.time()
            if not hasattr(self, '_last_toggle_time'):
                self._last_toggle_time = 0
            
            # Skip if acted less than 300ms ago (prevents rapid-fire in crowded rooms)
            if current_time - self._last_toggle_time < 0.3:
                self._last_foreground = foreground
                return
            
            self._last_toggle_time = current_time
            self._fullscreen_toggling = True
            
            # Foreground changed! Do auto-toggle (hide/show) to bring window on top
            print("[FULLSCREEN] Detected foreground change - auto-toggle!")
            self.hide()
            QTimer.singleShot(50, self._auto_show_topmost)
        
        self._last_foreground = foreground
    
    def _auto_show_topmost(self):
        """Auto-show with topmost after hide + restart hooks"""
        self.showNormal()
        self.raise_()
        # Re-apply all topmost settings
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        WS_EX_TOPMOST = 0x00000008
        WS_EX_LAYERED = 0x00080000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOPMOST | WS_EX_LAYERED)
        HWND_TOPMOST = -1
        ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0010 | 0x0040)
        
        # RESTART HOOKS: This was in showEvent() in backup, now we do it here
        print("[FULLSCREEN] Restarting hooks after show")
        self._arm_input()
        
        # Mark toggle as complete
        self._fullscreen_toggling = False
        
        # DON'T reset _mouse_clicked_since_send here!
        # The state should be preserved from before leaving the game
        print(f"[FULLSCREEN] State preserved: needs_enter={getattr(self, '_mouse_clicked_since_send', True)}")
        
        # Focus text edit when ready
        def focus_when_ready():
            if self._input_state == "READY":
                self.text_edit.setFocus()
            else:
                QTimer.singleShot(30, focus_when_ready)
        QTimer.singleShot(50, focus_when_ready)
    
    def _ensure_hooks_ready(self):
        """ضمان جاهزية الـ hooks - إعادة التسليح إذا كُسرت الحالة."""
        # إذا أُوقفت hooks أو كنا في IDLE بسبب الإخفاء، أعد التسلّح
        if self._input_state == "IDLE" and self.isVisible():
            print("[HEALTH] Hooks broken - restarting via _arm_input()")
            self._arm_input()
        elif self._input_state == "ARMING":
            # انتظر قليلاً ثم تحقق مجدداً
            self._hook_health_timer.start(50)
        # في READY أو SENDING: لا شيء
    
    def showEvent(self, event):
        super().showEvent(event)
        # Position buttons above the window after it's shown
        self.position_buttons()
        self.setMouseTracking(True)
        self.text_edit.setMouseTracking(True)
        self.text_edit.viewport().setMouseTracking(True)
        
        # Apply window styles for staying on top of fullscreen
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        WS_EX_TOPMOST = 0x00000008
        # NOTE: Don't add WS_EX_LAYERED - PyQt6's WA_TranslucentBackground handles this
        current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | WS_EX_NOACTIVATE | WS_EX_TOPMOST)
        
        # Force TOPMOST using SetWindowPos with SHOWWINDOW
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        SWP_SHOWWINDOW = 0x0040
        ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW)
        
        # NOTE: Keyboard hooks are now started by toggle() -> _arm_input() BEFORE showing
        # This prevents the race condition that caused keystroke leaks
    
    def eventFilter(self, obj, event):
        # Intercept mouse events from text_edit to handle resizing
        if obj == self.text_edit or obj == self.text_edit.viewport():
            if event.type() == QEvent.Type.MouseMove:
                # Check if we should handle resize cursor
                pos = self.text_edit.mapTo(self, event.position().toPoint())
                self.handle_mouse_move_for_resize(pos, event.globalPosition().toPoint())
                if self.resize_mode:
                    return True  # Consume event during resize
                    
            elif event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    pos = self.text_edit.mapTo(self, event.position().toPoint())
                    if self.start_resize_if_at_edge(pos, event.globalPosition().toPoint()):
                        return True  # Consume event if starting resize
                        
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if self.resize_mode:
                    self.end_resize()
                    return True
                    
        return super().eventFilter(obj, event)
    
    def start_resize_if_at_edge(self, pos, global_pos):
        """Check if click is at edge and start resize. Returns True if resize started."""
        rect = self.rect()
        m = 15  # Resize margin
        
        left = pos.x() < m
        right = pos.x() > rect.width() - m
        top = pos.y() < m
        bottom = pos.y() > rect.height() - m
        
        self.resize_mode = ''
        if top and left: self.resize_mode = 'tl'
        elif top and right: self.resize_mode = 'tr'
        elif bottom and left: self.resize_mode = 'bl'
        elif bottom and right: self.resize_mode = 'br'
        elif top: self.resize_mode = 't'
        elif bottom: self.resize_mode = 'b'
        elif left: self.resize_mode = 'l'
        elif right: self.resize_mode = 'r'
        
        if self.resize_mode:
            self.resize_start_pos = global_pos
            self.resize_start_geo = self.geometry()
            self._lock_buttons()  # Lock buttons during resize
            return True
        return False
    
    def handle_mouse_move_for_resize(self, pos, global_pos):
        """Update cursor and handle resizing."""
        rect = self.rect()
        m = 15
        
        # Determine cursor shape based on position
        left = pos.x() < m
        right = pos.x() > rect.width() - m
        top = pos.y() < m
        bottom = pos.y() > rect.height() - m
        
        cursor_shape = Qt.CursorShape.ArrowCursor
        if (top and left) or (bottom and right): 
            cursor_shape = Qt.CursorShape.SizeFDiagCursor
        elif (top and right) or (bottom and left): 
            cursor_shape = Qt.CursorShape.SizeBDiagCursor
        elif top or bottom: 
            cursor_shape = Qt.CursorShape.SizeVerCursor
        elif left or right: 
            cursor_shape = Qt.CursorShape.SizeHorCursor
        
        # Update cursor
        if cursor_shape != Qt.CursorShape.ArrowCursor:
            self.setCursor(cursor_shape)
            self.text_edit.viewport().setCursor(cursor_shape)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.text_edit.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        
        # Handle active resize
        if self.resize_mode and self.resize_start_pos:
            delta = global_pos - self.resize_start_pos
            geo = self.resize_start_geo
            x, y, w, h = geo.x(), geo.y(), geo.width(), geo.height()
            
            # Apply resize based on mode with minimum constraints
            min_width = 15
            min_height = 15  # Reduced to 20px to allow true single line
            
            if 'r' in self.resize_mode: 
                w = max(min_width, geo.width() + delta.x())
            
            if 'l' in self.resize_mode: 
                new_w = max(min_width, geo.width() - delta.x())
                # Only update x if width actually changed (not at minimum)
                if new_w > min_width:
                    x = geo.x() + delta.x()
                else:
                    x = geo.x() + geo.width() - min_width
                w = new_w
            
            if 'b' in self.resize_mode: 
                h = max(min_height, geo.height() + delta.y())
            
            if 't' in self.resize_mode: 
                new_h = max(min_height, geo.height() - delta.y())
                # Only update y if height actually changed (not at minimum)
                if new_h > min_height:
                    y = geo.y() + delta.y()
                else:
                    y = geo.y() + geo.height() - min_height
                h = new_h
            
            # Batch updates to reduce jitter
            self.setUpdatesEnabled(False)
            self.setGeometry(x, y, w, h)
            self.position_buttons()
            self.setUpdatesEnabled(True)
    
    def end_resize(self):
        """End resize operation and save config."""
        if self.resize_mode:
            CONFIG.set('x', self.x())
            CONFIG.set('y', self.y())
            CONFIG.set('w', self.width())
            CONFIG.set('h', self.height())
            self.resize_mode = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.text_edit.viewport().setCursor(Qt.CursorShape.IBeamCursor)
            self._unlock_buttons()  # Unlock and restart timer
    
    def _setup_hover_effect(self, button, normal_icon, hover_icon, size, tooltip_text="", tooltip_color="gray"):
        """Add hover effect with custom tooltip - bypasses Windows tooltip"""
        # Store on button for reference
        button._normal_icon = normal_icon
        button._hover_icon = hover_icon
        button._icon_size = size
        button._tooltip_text = tooltip_text
        button._tooltip_color = tooltip_color
        
        # Remove Windows tooltip
        button.setToolTip("")
        
        def on_enter(event):
            button.setIcon(QIcon(button._hover_icon))
            button.setIconSize(QSize(button._icon_size, button._icon_size))
            # Manually set background (CSS :hover broken by mouse event overrides)
            button.setStyleSheet("""
                QPushButton { background: rgba(255,255,255,15); border: none; border-radius: 8px; }
            """)
            # Lock buttons while hovering
            self._lock_buttons()
            # Show custom tooltip
            if button._tooltip_text:
                self._show_custom_tooltip(button, button._tooltip_text, button._tooltip_color)
        
        def on_leave(event):
            button.setIcon(QIcon(button._normal_icon))
            button.setIconSize(QSize(button._icon_size, button._icon_size))
            # Restore transparent background
            button.setStyleSheet("""
                QPushButton { background: rgba(0,0,0,0); border: none; }
            """)
            # Hide custom tooltip
            self._hide_custom_tooltip()
            # Unlock buttons and restart timer
            self._unlock_buttons()
        
        button.enterEvent = on_enter
        button.leaveEvent = on_leave
    
    def _show_custom_tooltip(self, button, text, color="gray"):
        """Show custom tooltip bubble with color"""
        if not hasattr(self, '_custom_tooltip'):
            self._custom_tooltip = QWidget()
            self._custom_tooltip.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
            self._custom_tooltip.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            
            # Create label inside
            self._tooltip_label = QLabel(self._custom_tooltip)
            self._tooltip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Colors - نص فاتح جداً، إطار أغمق، خلفية شفافة (نفس أسلوب olive)
        colors = {
            "gray": {"text": "#d4d8dc", "border": "#4a5058", "bg": "rgba(74, 80, 88, 0.35)"},
            "olive": {"text": "#d4e8c0", "border": "#4a5f35", "bg": "rgba(74, 95, 53, 0.35)"},
            "blue": {"text": "#c4daf8", "border": "#2a5a9f", "bg": "rgba(42, 90, 159, 0.35)"},
            "red": {"text": "#f8c4c4", "border": "#8f2a2a", "bg": "rgba(143, 42, 42, 0.35)"},
            "green": {"text": "#c4f8d4", "border": "#2a8f4a", "bg": "rgba(42, 143, 74, 0.35)"},
        }
        c = colors.get(color, colors["gray"])
        
        self._tooltip_label.setText(text)
        self._tooltip_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text']};
                background-color: {c['bg']};
                border: 1px solid {c['border']};
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
            }}
        """)
        self._tooltip_label.adjustSize()
        
        # Size the container
        self._custom_tooltip.setFixedSize(self._tooltip_label.width(), self._tooltip_label.height())
        self._tooltip_label.move(0, 0)
        
        # Position ABOVE button (centered)
        btn_pos = button.mapToGlobal(QPoint(button.width() // 2, 0))
        tooltip_x = btn_pos.x() - self._tooltip_label.width() // 2
        tooltip_y = btn_pos.y() - self._tooltip_label.height() - 5
        self._custom_tooltip.move(tooltip_x, tooltip_y)
        self._custom_tooltip.show()
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB values string"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    
    def _hide_custom_tooltip(self):
        """Hide custom tooltip"""
        if hasattr(self, '_custom_tooltip'):
            self._custom_tooltip.hide()

    def position_buttons(self):
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(script_dir, 'Icons')
        
        # === ICON SIZE - غيّر هذا الرقم للتحكم بحجم الأيقونات ===
        ICON_SIZE = 16  # حجم الأيقونة (بكسل)
        BTN_SIZE = 32   # حجم منطقة الضغط الشفافة (أكبر للسهولة)
        
        # Create buttons if they don't exist
        if not hasattr(self, 'drag_handle'):
            # Drag Handle
            self.drag_handle = QPushButton(self.parent() if self.parent() else self)
            self.drag_handle.setFixedSize(BTN_SIZE, BTN_SIZE)
            # Same semi-transparent style as other buttons
            self.drag_handle.setStyleSheet("""
                QPushButton { background: rgba(0,0,0,0); border: none; }
                QPushButton:hover { background: rgba(255,255,255,15); border-radius: 8px; }
            """)
            self.drag_handle.setCursor(Qt.CursorShape.SizeAllCursor)
            self.drag_handle.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
            self.drag_handle.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            move_icon = os.path.join(icons_dir, 'move.png')
            move_icon_light = os.path.join(icons_dir, 'move_light.png')
            if os.path.exists(move_icon):
                self.drag_handle.setIcon(QIcon(move_icon))
                self.drag_handle.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
            self.drag_handle.mousePressEvent = self.start_drag
            self.drag_handle.mouseMoveEvent = self.do_drag
            self.drag_handle.mouseReleaseEvent = self.end_drag
            self._setup_hover_effect(self.drag_handle, move_icon, move_icon_light, ICON_SIZE, "تحريك", "olive")
            
            # Settings Button
            self.btn_settings = QPushButton(self.parent() if self.parent() else self)
            self.btn_settings.setFixedSize(BTN_SIZE, BTN_SIZE)
            # Semi-transparent background so the entire area is clickable
            self.btn_settings.setStyleSheet("""
                QPushButton { background: rgba(0,0,0,0); border: none; }
                QPushButton:hover { background: rgba(255,255,255,15); border-radius: 8px; }
            """)
            settings_icon = os.path.join(icons_dir, 'settings.png')
            settings_icon_light = os.path.join(icons_dir, 'settings_light.png')
            if os.path.exists(settings_icon):
                self.btn_settings.setIcon(QIcon(settings_icon))
                self.btn_settings.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
            self.btn_settings.clicked.connect(self.toggle_settings)
            self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_settings.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
            self.btn_settings.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self._setup_hover_effect(self.btn_settings, settings_icon, settings_icon_light, ICON_SIZE, "الإعدادات", "blue")
            
            # Pin Button
            self.btn_pin = QPushButton(self.parent() if self.parent() else self)
            self.btn_pin.setFixedSize(BTN_SIZE, BTN_SIZE)
            self.btn_pin.clicked.connect(self.toggle_pin_mode)
            self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_pin.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
            self.btn_pin.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            # Semi-transparent background so the entire area is clickable
            self.btn_pin.setStyleSheet("""
                QPushButton { background: rgba(0,0,0,0); border: none; }
                QPushButton:hover { background: rgba(255,255,255,15); border-radius: 8px; }
            """)
            
            # Store icons dir and size for pin hover effect
            self._icons_dir = icons_dir
            self._icon_size = ICON_SIZE
        
        # Update pin button style every time (in case config changed)
        self.update_pin_button_style()
        
        # Position buttons above the chat window - all same size and level
        btn_y = self.y() - 32  # Buttons touch the chat edge
        self.drag_handle.setGeometry(self.x() + 2, btn_y, 32, 32)
        self.btn_settings.setGeometry(self.x() + 34, btn_y, 32, 32)
        self.btn_pin.setGeometry(self.x() + 66, btn_y, 32, 32)
        self.drag_handle.show()
        self.btn_settings.show()
        self.btn_pin.show()
    
        # Apply WS_EX_NOACTIVATE to buttons
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        
        hwnd_drag = int(self.drag_handle.winId())
        style_drag = ctypes.windll.user32.GetWindowLongW(hwnd_drag, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd_drag, GWL_EXSTYLE, style_drag | WS_EX_NOACTIVATE)
        
        hwnd_settings = int(self.btn_settings.winId())
        style_settings = ctypes.windll.user32.GetWindowLongW(hwnd_settings, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd_settings, GWL_EXSTYLE, style_settings | WS_EX_NOACTIVATE)
        
        hwnd_pin = int(self.btn_pin.winId())
        style_pin = ctypes.windll.user32.GetWindowLongW(hwnd_pin, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd_pin, GWL_EXSTYLE, style_pin | WS_EX_NOACTIVATE)
        
        # Hide buttons initially (auto-hide feature)
        if not self._buttons_visible:
            self.drag_handle.hide()
            self.btn_settings.hide()
            self.btn_pin.hide()
    
    def _show_buttons_with_timer(self):
        """Show buttons and start 5-second auto-hide timer"""
        if not hasattr(self, 'drag_handle'):
            return
        
        # Show buttons
        self._buttons_visible = True
        btn_y = self.y() - 32  # Buttons touch the chat edge
        self.drag_handle.setGeometry(self.x() + 2, btn_y, 32, 32)
        self.btn_settings.setGeometry(self.x() + 34, btn_y, 32, 32)
        self.btn_pin.setGeometry(self.x() + 66, btn_y, 32, 32)
        self.drag_handle.show()
        self.btn_settings.show()
        self.btn_pin.show()
        
        # Start auto-hide timer (5 seconds)
        if not hasattr(self, '_auto_hide_timer'):
            from PyQt6.QtCore import QTimer
            self._auto_hide_timer = QTimer()
            self._auto_hide_timer.setSingleShot(True)
            self._auto_hide_timer.timeout.connect(self._on_auto_hide_timer)
        self._auto_hide_timer.start(5000)  # 5 ثواني
    
    def _on_auto_hide_timer(self):
        """Called when auto-hide timer expires"""
        # Don't hide if buttons are locked (dragging/resizing/hovering)
        if self._buttons_locked:
            return
        self._hide_buttons()
    
    def _hide_buttons(self):
        """Hide buttons"""
        if not self._buttons_visible:
            return
        self._buttons_visible = False
        self._hide_custom_tooltip()
        
        if hasattr(self, 'drag_handle'):
            self.drag_handle.hide()
        if hasattr(self, 'btn_settings'):
            self.btn_settings.hide()
        if hasattr(self, 'btn_pin'):
            self.btn_pin.hide()
    
    def _lock_buttons(self):
        """Lock buttons visible (during drag/resize/hover)"""
        self._buttons_locked = True
        # Stop auto-hide timer
        if hasattr(self, '_auto_hide_timer'):
            self._auto_hide_timer.stop()
    
    def _unlock_buttons(self):
        """Unlock buttons and restart timer"""
        self._buttons_locked = False
        # Restart auto-hide timer
        if self._buttons_visible:
            if hasattr(self, '_auto_hide_timer'):
                self._auto_hide_timer.start(5000)
    
    def hideEvent(self, event):
        super().hideEvent(event)
        self._buttons_visible = False
        if hasattr(self, 'drag_handle'):
            self.drag_handle.hide()
        if hasattr(self, 'btn_settings'):
            self.btn_settings.hide()
        if hasattr(self, 'btn_pin'):
            self.btn_pin.hide()
        # Stop keyboard hooks when hidden
        self.stop_keyboard_hooks()
    
    def toggle_pin_mode(self):
        """Toggle pin mode on/off"""
        current = CONFIG.get('pinned_mode')
        CONFIG.set('pinned_mode', not current)
        self.update_pin_button_style()
        if not current:
            print("[PIN] مفعّل - الشات سيختفي لحظة عند الإرسال")
        else:
            print("[PIN] معطّل - الوضع العادي")
    
    def update_pin_button_style(self):
        """Update pin button icon based on state with hover effect"""
        import os
        icons_dir = getattr(self, '_icons_dir', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Icons'))
        icon_size = getattr(self, '_icon_size', 16)
        
        if CONFIG.get('pinned_mode'):
            icon_path = os.path.join(icons_dir, 'pin_green.png')
            icon_path_light = os.path.join(icons_dir, 'pin_green_light.png')
            tooltip_text = "مثبت فوق الشات ✓"
            tooltip_color = "green"
        else:
            icon_path = os.path.join(icons_dir, 'pin_gray.png')
            icon_path_light = os.path.join(icons_dir, 'pin_gray_light.png')
            tooltip_text = "غير مثبت فوق الشات ✗"
            tooltip_color = "red"
        
        if os.path.exists(icon_path):
            self.btn_pin.setIcon(QIcon(icon_path))
            self.btn_pin.setIconSize(QSize(icon_size, icon_size))
        
        # Update hover effect
        self._setup_hover_effect(self.btn_pin, icon_path, icon_path_light, icon_size, tooltip_text, tooltip_color)
        
        # If tooltip is visible, update it live with new color/text
        if hasattr(self, '_custom_tooltip') and self._custom_tooltip.isVisible():
            self._show_custom_tooltip(self.btn_pin, tooltip_text, tooltip_color)
    
    # ========================================================================
    # KEYBOARD HOOKS - TYPING ONLY
    # ========================================================================
    
    def start_keyboard_hooks(self):
        """Hook keyboard with DLL for media keys + keyboard lib for rest"""
        self.stop_keyboard_hooks()
        
        print("[HOOK] Starting keyboard hooks (DLL + keyboard lib)...")
        
        # Media letter scan codes - handled by DLL (D, C, B, Q, G, P)
        self.media_letter_scans = {32, 46, 48, 16, 34, 25}
        
        # STRICT WHITELIST - Only basic typing scan codes (EXCLUDING media letters)
        self.typing_scan_codes = {
            # QWERTY Row (Q and P removed - handled by DLL)
            17: 'w', 18: 'e', 19: 'r', 20: 't', 21: 'y', 22: 'u', 23: 'i', 24: 'o',
            # ASDF Row (D and G removed - handled by DLL)
            30: 'a', 31: 's', 33: 'f', 35: 'h', 36: 'j', 37: 'k', 38: 'l',
            # ZXCV Row (C and B removed - handled by DLL)
            44: 'z', 45: 'x', 47: 'v', 49: 'n', 50: 'm',
            # Number Row
            2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
            # Symbols
            12: '-', 13: '=', 26: '[', 27: ']', 43: '\\', 39: ';', 40: "'", 51: ',', 52: '.', 53: '/',
            41: '`',
            # Space, Backspace, Enter
            57: 'space', 14: 'backspace', 28: 'enter'
        }
        
        # Scan code to key name mapping for DLL callback (media letters)
        self.dll_scan_to_name = {32: 'd', 46: 'c', 48: 'b', 16: 'q', 34: 'g', 25: 'p'}
        
        # Navigation keys
        self.nav_scan_codes = {
            75: 'left', 77: 'right', 72: 'up', 80: 'down',
            83: 'delete', 71: 'home', 79: 'end'
        }
        
        # Initialize and start the DLL filter
        try:
            self.media_filter = get_filter()
            self.media_filter.load()
            self.media_filter.set_callback(self.on_dll_key_event)
            self.media_filter.start()
            self.media_filter.enable(True)
            print("[HOOK] DLL filter active (handles D,C,B,Q,G,P)")
        except Exception as e:
            print(f"[HOOK] DLL failed: {e} - falling back to keyboard lib")
            # Add media letters back to typing_scan_codes as fallback
            self.typing_scan_codes.update({16: 'q', 25: 'p', 32: 'd', 34: 'g', 46: 'c', 48: 'b'})
        
        # Hook keyboard globally WITH SUPPRESSION (for non-media-letter keys)
        try:
            self.keyboard_hook = keyboard.hook(self.on_keyboard_event, suppress=True)
            print(f"[HOOK] Keyboard hook installed ({len(self.typing_scan_codes)} typing + {len(self.nav_scan_codes)} nav keys)")
        except Exception as e:
            print(f"[HOOK] Failed: {e}")
    
    def stop_keyboard_hooks(self):
        """Remove keyboard hook and DLL filter while preserving Insert hotkey"""
        # Stop DLL filter
        if hasattr(self, 'media_filter') and self.media_filter:
            try:
                self.media_filter.enable(False)
            except:
                pass
        
        # Stop keyboard hook
        if hasattr(self, 'keyboard_hook'):
            print("[HOOK] Stopping keyboard hook...")
            try:
                keyboard.unhook(self.keyboard_hook)
                delattr(self, 'keyboard_hook')
                print("[HOOK] Keyboard hook stopped (Insert preserved)")
            except Exception as e:
                print(f"[HOOK] Error stopping hook: {e}")
    
    def on_dll_key_event(self, vk_code, scan_code, flags):
        """Callback from DLL when a media letter key is blocked (D,C,B,Q,G,P)"""
        # Get key name from scan code
        key_name = self.dll_scan_to_name.get(scan_code, None)
        if not key_name:
            return
        
        print(f"[DLL] Key: {key_name}")
        
        # ==========================================
        # STATE MACHINE CHECK - DLL keys also respect states
        # ==========================================
        
        # أثناء ARMING: خزّن الحرف في buffer
        if self._input_state == "ARMING":
            shift = keyboard.is_pressed('shift')
            if self.is_arabic_mode:
                char = self.text_edit.get_arabic_char(key_name, shift)
            else:
                caps_lock = bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
                uppercase = caps_lock != shift
                char = key_name.upper() if uppercase else key_name.lower()
            if char and len(self._keystroke_buffer) < 5:
                self._keystroke_buffer.append(char)
                print(f"[BUFFER-DLL] Stored: {char}")
            return  # لا تُدخل - خزّن فقط
        
        # أثناء SENDING: امنع الإدخال
        if self._input_state == "SENDING":
            return
        
        # ==========================================
        # READY STATE - معالجة عادية
        # ==========================================
        
        # Process as typing
        shift = keyboard.is_pressed('shift')
        
        # Check Caps Lock state (bit 0 indicates toggle state)
        caps_lock = bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
        
        if self.is_arabic_mode:
            char = self.text_edit.get_arabic_char(key_name, shift)
        else:
            # Caps Lock XOR Shift = uppercase
            uppercase = caps_lock != shift  # XOR logic
            char = key_name.upper() if uppercase else key_name.lower()
        
        if char:
            self.insert_text_signal.emit(char)
    
    def on_keyboard_event(self, event):
        """Smart keyboard handler with proper suppression and State Machine."""
        if event.event_type != 'down':
            return True  # Let key-up through
        
        scan_code = event.scan_code
        
        # ==========================================
        # SYSTEM KEY EXCEPTIONS - لا تعطل تجربة المستخدم
        # ==========================================
        try:
            win_pressed = keyboard.is_pressed('win') or keyboard.is_pressed('left windows') or keyboard.is_pressed('right windows')
            alt_tab = keyboard.is_pressed('alt') and keyboard.is_pressed('tab')
            if win_pressed or alt_tab:
                return True  # اسمح بمفاتيح النظام
        except:
            pass
        
        # ==========================================
        # STATE MACHINE HANDLING
        # ==========================================
        
        # أثناء ARMING: خزّن الأحرف في buffer ومنع التسرب تماماً
        if self._input_state == "ARMING":
            if scan_code in self.typing_scan_codes:
                key_name = self.typing_scan_codes[scan_code]
                # لا نخزن space/backspace/enter في buffer
                if key_name not in ['space', 'backspace', 'enter']:
                    char = self._get_char_for_key(key_name)
                    if char and len(char) >= 1 and len(self._keystroke_buffer) < 5:
                        self._keystroke_buffer.append(char)
                        print(f"[BUFFER] Stored: {char}")
            return False  # منع تام أثناء ARMING
        
        # أثناء SENDING: امنع أي إدخال جديد
        if self._input_state == "SENDING":
            return False
        
        # ==========================================
        # READY STATE - معالجة عادية
        # ==========================================
        
        # ==========================================
        # NUMPAD HANDLING - معالجة لوحة الأرقام
        # ==========================================
        
        # Numpad symbols that ALWAYS work (regardless of Num Lock)
        NUMPAD_ALWAYS_SYMBOLS = {
            78: '+',  # Numpad +
            74: '-',  # Numpad -
            55: '*',  # Numpad *
            309: '/',  # Numpad / (extended key, scan_code may vary)
        }
        
        # Numpad keys that depend on Num Lock state
        # When ON = number/symbol, when OFF = navigation
        NUMPAD_NUMBERS = {
            82: '0',  # Numpad 0 / Ins
            79: '1',  # Numpad 1 / End
            80: '2',  # Numpad 2 / Down
            81: '3',  # Numpad 3 / PgDn
            75: '4',  # Numpad 4 / Left
            76: '5',  # Numpad 5
            77: '6',  # Numpad 6 / Right
            71: '7',  # Numpad 7 / Home
            72: '8',  # Numpad 8 / Up
            73: '9',  # Numpad 9 / PgUp
            83: '.',  # Numpad . / Del
        }
        
        # Check if Numpad key (must have is_keypad=True)
        is_numpad = hasattr(event, 'is_keypad') and event.is_keypad
        
        if is_numpad:
            # ========== ALWAYS WORKING SYMBOLS (/, *, -, +) ==========
            if scan_code in NUMPAD_ALWAYS_SYMBOLS:
                char = NUMPAD_ALWAYS_SYMBOLS[scan_code]
                print(f"[NUMPAD] Symbol (always): {char}")
                self.insert_text_signal.emit(char)
                return False  # Suppress
            
            # Also check for / with different scan codes (some keyboards use 53 or 309)
            if event.name in ['/', 'divide'] or scan_code == 53:
                print("[NUMPAD] Symbol (always): /")
                self.insert_text_signal.emit('/')
                return False  # Suppress
            
            # ========== NUM LOCK DEPENDENT KEYS (0-9 and .) ==========
            if scan_code in NUMPAD_NUMBERS:
                VK_NUMLOCK = 0x90
                num_lock_on = bool(ctypes.windll.user32.GetKeyState(VK_NUMLOCK) & 1)
                
                if num_lock_on:
                    # Num Lock ON - type the number/symbol
                    char = NUMPAD_NUMBERS[scan_code]
                    print(f"[NUMPAD] Num Lock ON - typing: {char}")
                    self.insert_text_signal.emit(char)
                    return False  # Suppress
                else:
                    # Num Lock OFF - navigation mode
                    # Special case for Del key (scan_code 83)
                    if scan_code == 83:
                        print("[NUMPAD] Num Lock OFF - Delete")
                        cursor = self.text_edit.textCursor()
                        cursor.deleteChar()
                        return False  # Suppress - handled delete in chat
                    else:
                        # Let arrows/navigation work (fall through to nav_scan_codes)
                        print(f"[NUMPAD] Num Lock OFF - passing as navigation")
                        # Fall through to nav_scan_codes handling below
        
        # Handle Numpad Enter (scan_code 28 with is_keypad=True)
        if scan_code == 28 and hasattr(event, 'is_keypad') and event.is_keypad:
            print("[NUMPAD] Numpad Enter - sending message")
            if keyboard.is_pressed('shift'):
                self.insert_text_signal.emit('\n')
            else:
                self.send_text_signal.emit()
            return False  # Suppress
        
        # فحص Ctrl الفعلي من Windows API (لحل مشكلة Ctrl "العالقة")
        VK_CONTROL = 0x11
        ctrl_actually_pressed = bool(ctypes.windll.user32.GetAsyncKeyState(VK_CONTROL) & 0x8000)
        
        # Handle typing keys (SUPPRESS these)
        if scan_code in self.typing_scan_codes:
            key_name = self.typing_scan_codes[scan_code]
            print(f"[KEY] Type: {key_name}")
            
            # Handle Ctrl shortcuts - use ACTUAL Ctrl state from Windows API
            if ctrl_actually_pressed:
                print(f"[KEY] Ctrl+{key_name}")
                if key_name == 'a':  # Select All
                    self.text_edit.selectAll()
                elif key_name == 'v':  # Paste - check Windows clipboard for NEW content first
                    try:
                        win_clip = pyperclip.paste()
                        # If Windows has new user-copied content (not our sent message)
                        if win_clip and win_clip != self._last_sent_message and win_clip != self._internal_clipboard:
                            self.text_edit.insertPlainText(win_clip)
                            self._internal_clipboard = win_clip  # Update internal
                            print(f"[KEY] Ctrl+V NEW from Windows: {win_clip[:20]}...")
                        elif self._internal_clipboard:
                            # Use internal clipboard
                            self.text_edit.insertPlainText(self._internal_clipboard)
                            print(f"[KEY] Ctrl+V from internal: {self._internal_clipboard[:20]}...")
                        elif win_clip and win_clip != self._last_sent_message:
                            # Windows has content that's not our sent message
                            self.text_edit.insertPlainText(win_clip)
                            self._internal_clipboard = win_clip
                            print(f"[KEY] Ctrl+V from Windows: {win_clip[:20]}...")
                    except: pass
                elif key_name == 'x':  # Cut - save to INTERNAL clipboard + delete
                    cursor = self.text_edit.textCursor()
                    selected = cursor.selectedText()
                    if selected:
                        self._internal_clipboard = selected  # Save to internal
                        cursor.removeSelectedText()
                        print(f"[KEY] Ctrl+X cut to internal: {selected[:20]}...")
                elif key_name == 'z':  # Undo
                    self.text_edit.undo()
                elif key_name == 'y':  # Redo
                    self.text_edit.redo()
                # Note: Ctrl+C is handled separately (since C is a DLL media letter)
                return False  # Suppress - we handled it
            
            # Let Windows key combinations pass through (Win+. emoji, Win+= magnifier)
            if keyboard.is_pressed('win') or keyboard.is_pressed('left windows') or keyboard.is_pressed('right windows'):
                print("[KEY] Windows key - let through")
                return True
            
            # Handle special keys
            if key_name == 'enter':
                if keyboard.is_pressed('shift'):
                    self.insert_text_signal.emit('\n')
                else:
                    self.send_text_signal.emit()
                return False  # SUPPRESS (don't send to game)
            
            if key_name == 'backspace':
                self.backspace_signal.emit()
                return False  # SUPPRESS
            
            if key_name == 'space':
                self.insert_text_signal.emit(' ')
                return False  # SUPPRESS
            
            # Regular typing
            if len(key_name) == 1:
                shift = keyboard.is_pressed('shift')
                
                if self.is_arabic_mode:
                    char = self.text_edit.get_arabic_char(key_name, shift)
                else:
                    if shift:
                        shift_map = {
                            '1':'!', '2':'@', '3':'#', '4':'$', '5':'%', '6':'^',
                            '7':'&', '8':'*', '9':'(', '0':')', '-':'_', '=':'+',
                            '[':'{', ']':'}', '\\':'|', ';':':', "'":'"',
                            ',':'<', '.':'>', '/':'?'
                        }
                        if key_name in shift_map:
                            char = shift_map[key_name]
                        else:
                            caps_lock = bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
                            char = key_name.lower() if caps_lock else key_name.upper()
                    else:
                        caps_lock = bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
                        char = key_name.upper() if caps_lock else key_name.lower()
                
                if char:
                    self.insert_text_signal.emit(char)
                return False  # SUPPRESS
        
        # Check if navigation key (for chat editing)
        elif scan_code in self.nav_scan_codes:
            key_name = self.nav_scan_codes[scan_code]
            print(f"[KEY] Nav: {key_name}")
            
            # Send to text_edit for navigation
            if key_name == 'left':
                cursor = self.text_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Left)
                self.text_edit.setTextCursor(cursor)
            elif key_name == 'right':
                cursor = self.text_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Right)
                self.text_edit.setTextCursor(cursor)
            elif key_name == 'up':
                cursor = self.text_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Up)
                self.text_edit.setTextCursor(cursor)
            elif key_name == 'down':
                cursor = self.text_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Down)
                self.text_edit.setTextCursor(cursor)
            elif key_name == 'delete':
                cursor = self.text_edit.textCursor()
                cursor.deleteChar()
            elif key_name == 'home':
                cursor = self.text_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                self.text_edit.setTextCursor(cursor)
            elif key_name == 'end':
                cursor = self.text_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
                self.text_edit.setTextCursor(cursor)
            
            return True  # DON'T suppress nav keys (let them work in game too)
        
        # Handle Ctrl+C specially (C is handled by DLL, but Ctrl+C is let through)
        elif scan_code == 46 and keyboard.is_pressed('ctrl'):
            selected = self.text_edit.textCursor().selectedText()
            if selected:
                self._internal_clipboard = selected  # Save to INTERNAL clipboard
                print(f"[KEY] Ctrl+C copied to internal: {selected[:20]}...")
            else:
                print("[KEY] Ctrl+C - nothing selected")
            return False  # Suppress - we handled it
        
        # All other keys
        return True
    
    @pyqtSlot(str)
    def on_insert_text(self, text):
        """Thread-safe text insertion with auto-scroll"""
        self.text_edit.insertPlainText(text)
        # Auto-scroll to show new text
        self.text_edit.ensureCursorVisible()
    
    @pyqtSlot()
    def on_backspace(self):
        """Thread-safe backspace"""
        cursor = self.text_edit.textCursor()
        cursor.deletePreviousChar()
    
    def moveEvent(self, event):
        super().moveEvent(event)
        # Update button positions when window moves
        if hasattr(self, 'drag_handle') and self._buttons_visible:
            btn_y = self.y() - 32
            self.drag_handle.setGeometry(self.x() + 2, btn_y, 32, 32)
            self.btn_settings.setGeometry(self.x() + 34, btn_y, 32, 32)
            self.btn_pin.setGeometry(self.x() + 66, btn_y, 32, 32)
    
    def enterEvent(self, event):
        """Show buttons when mouse enters chat area"""
        super().enterEvent(event)
        self._show_buttons_with_timer()
    
    def leaveEvent(self, event):
        """When mouse leaves chat, buttons stay visible for 5 seconds"""
        super().leaveEvent(event)
        # Buttons will hide after timer expires (unless locked)

    @pyqtSlot()
    def apply_settings(self):
        bg = QColor(CONFIG.get('bg_color'))
        txt = QColor(CONFIG.get('text_color'))
        bg_a = CONFIG.get('bg_opacity')
        txt_a = CONFIG.get('text_opacity')
        fs = CONFIG.get('font_size')

        self.central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgba({bg.red()}, {bg.green()}, {bg.blue()}, {bg_a});
                border-radius: 8px;
            }}
        """)
        
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                color: rgba({txt.red()}, {txt.green()}, {txt.blue()}, {txt_a});
                font-family: 'Segoe UI';
                font-size: {fs}px;
                border: none;
            }}
        """)
        
        # Apply first line end setting (only in Arabic mode, makes first line wrap earlier)
        try:
            line_end = CONFIG.get('first_line_end')
            from PyQt6.QtGui import QTextBlockFormat, QTextCursor
            cursor = self.text_edit.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            block_format = QTextBlockFormat()
            
            # Only apply indent in Arabic mode and if value > 0
            if line_end > 0 and self.is_arabic_mode:
                block_format.setTextIndent(line_end)
            else:
                block_format.setTextIndent(0)  # Reset to 0
            
            cursor.mergeBlockFormat(block_format)
            cursor.clearSelection()  # Clear selection BEFORE setting cursor
            cursor.movePosition(QTextCursor.MoveOperation.End)  # Move to end of text
            self.text_edit.setTextCursor(cursor)
        except Exception as e:
            print(f"[WARN] Error applying text format: {e}")

    def start_drag(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._hide_custom_tooltip()
            self._lock_buttons()  # Lock buttons while dragging
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def do_drag(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
    
    def end_drag(self, event):
        if self.drag_pos:
            CONFIG.set('x', self.x())
            CONFIG.set('y', self.y())
            self.drag_pos = None
            self._unlock_buttons()  # Unlock and restart timer

    def toggle_settings(self):
        """Toggle settings dialog visibility"""
        if hasattr(self, 'settings_dlg') and self.settings_dlg.isVisible():
            self.settings_dlg.hide()
        else:
            self.open_settings()
    
    def open_settings(self):
        if not hasattr(self, 'settings_dlg') or not self.settings_dlg.isVisible():
            self.settings_dlg = NewSettingsDialog(parent=self, config=CONFIG, overlay=self)
            # Restore saved position or use default
            saved_x = CONFIG.get('settings_x')
            saved_y = CONFIG.get('settings_y')
            if saved_x != -1 and saved_y != -1:
                self.settings_dlg.move(saved_x, saved_y)
            else:
                self.settings_dlg.move(self.x() + self.width() + 20, self.y())
            self.settings_dlg.show()

    def reload_hotkey(self):
        try:
            keyboard.remove_hotkey(CONFIG.get('hotkey'))
        except: pass
        keyboard.add_hotkey(CONFIG.get('hotkey'), self.handle_hotkey)

    def handle_hotkey(self):
        if self.loc_mode:
            QMetaObject.invokeMethod(self, "save_location", Qt.ConnectionType.QueuedConnection)
        else:
            QMetaObject.invokeMethod(self, "toggle", Qt.ConnectionType.QueuedConnection)

    @pyqtSlot()
    def save_location(self):
        x, y = win32api.GetCursorPos()
        CONFIG.set('game_click_x', x)
        CONFIG.set('game_click_y', y)
        
        # Save target game window and name
        self._target_game_hwnd = ctypes.windll.user32.GetForegroundWindow()
        title = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetWindowTextW(self._target_game_hwnd, title, 256)
        game_name = title.value
        CONFIG.set('game_name', game_name)
        
        if hasattr(self, 'settings_dlg'): self.settings_dlg.update_loc_display()
        self.loc_mode = False
        print("="*60)
        print(f"✓ Chat location saved: ({x}, {y})")
        print(f"✓ Target game: {game_name}")
        print("✓ Insert is now active!")
        print("✓ Press Insert to open the chat overlay")
        print("="*60)
        print(f"[FOCUS] Target game saved: {self._target_game_hwnd} - '{game_name}'")
        
        # Auto-open chat after location is saved
        self.showNormal()

    def toggle_language(self):
        """Toggle between Arabic and English input modes"""
        self.is_arabic_mode = not self.is_arabic_mode
        self.lang_changed.emit(self.is_arabic_mode)
        mode = "العربية" if self.is_arabic_mode else "English"
        print(f"Language mode: {mode}")
        
        # Apply/reset indent when chat is empty
        if not self.text_edit.toPlainText().strip():
            try:
                from PyQt6.QtGui import QTextBlockFormat
                block_format = QTextBlockFormat()
                
                if self.is_arabic_mode:
                    # Arabic mode: apply indent
                    line_end = CONFIG.get('first_line_end')
                    block_format.setTextIndent(line_end if line_end > 0 else 0)
                else:
                    # English mode: reset to 0
                    block_format.setTextIndent(0)
                
                cursor = self.text_edit.textCursor()
                cursor.mergeBlockFormat(block_format)
                self.text_edit.setTextCursor(cursor)
            except:
                pass
    
    @pyqtSlot()
    def toggle(self):
        if self.isVisible():
            # عند الإغلاق: أوقف hooks وعد لـ IDLE
            self.hide()
            self._input_state = "IDLE"
            self.stop_keyboard_hooks()
        else:
            # Check if location is set
            if CONFIG.get('game_click_x') == -1:
                # First time - save current mouse position as chat location
                x, y = win32api.GetCursorPos()
                CONFIG.set('game_click_x', x)
                CONFIG.set('game_click_y', y)
                # Save game name
                fg = ctypes.windll.user32.GetForegroundWindow()
                title = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetWindowTextW(fg, title, 256)
                CONFIG.set('game_name', title.value)
                self._target_game_hwnd = fg
                # Update settings dialog if open
                if hasattr(self, 'settings_dlg') and self.settings_dlg.isVisible():
                    self.settings_dlg.update_loc_display()
                print("=" * 60)
                print(f"✓ Chat location saved: ({x}, {y})")
                print(f"✓ Target game: {title.value}")
                print("✓ Opening chat...")
                print("=" * 60)
            
            # Save target game if not already set (when location was loaded from config)
            if not hasattr(self, '_target_game_hwnd') or self._target_game_hwnd == 0:
                fg = ctypes.windll.user32.GetForegroundWindow()
                our_hwnd = int(self.winId()) if self.isVisible() else 0
                if fg != our_hwnd and fg != 0:
                    self._target_game_hwnd = fg
                    title = ctypes.create_unicode_buffer(256)
                    ctypes.windll.user32.GetWindowTextW(fg, title, 256)
                    # Also update game_name if not set
                    if not CONFIG.get('game_name'):
                        CONFIG.set('game_name', title.value)
                    print(f"[FOCUS] Target game saved: {fg} - '{title.value}'")
            
            # ==========================================
            # PRE-ARM SYSTEM: Hook first, then show
            # ==========================================
            # 1) تسليح الإدخال قبل الإظهار
            self._arm_input()
            
            # 2) اعرض النافذة بعد تسليح hook (30ms delay)
            QTimer.singleShot(30, self._atomic_show_focus)

    def send_text(self):
        """Send text to game chat - OPTIMIZED for speed"""
        
        # Get raw text first to check content
        raw_text = self.text_edit.toPlainText().strip()
        if not raw_text:
            return
        
        # Check if text contains ANY Arabic characters
        arabic_chars = "ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوىيًٌٍَُِّْ"
        has_arabic = any(c in arabic_chars for c in raw_text)
        
        # If pure English (no Arabic), send as-is with natural wrapping
        if not has_arabic:
            processed = raw_text
        else:
            # Has Arabic: use line layout for proper visual line ordering
            doc = self.text_edit.document()
            
            lines = []
            block = doc.begin()
            while block.isValid():
                layout = block.layout()
                if layout:
                    for i in range(layout.lineCount()):
                        line = layout.lineAt(i)
                        start = line.textStart()
                        length = line.textLength()
                        text = block.text()[start:start+length]
                        if text.strip():
                            lines.append(text)
                block = block.next()
            
            text = '\n'.join(lines).strip()
            if not text:
                return
            
            processed = self.processor.process_text(text)
        
        # ==========================================
        # SENDING STATE - منع الإدخال أثناء الإرسال
        # ==========================================
        self._input_state = "SENDING"
        
        # If pinned mode - use click-through (smoother than hide)
        is_pinned = CONFIG.get('pinned_mode')
        if is_pinned:
            self._set_click_through(True)
        
        # Save Windows clipboard to internal IF user-copied content
        try:
            current_clipboard = pyperclip.paste()
            if current_clipboard and current_clipboard != self._last_sent_message:
                self._internal_clipboard = current_clipboard
                print(f"[CLIPBOARD] Saved user content: {current_clipboard[:30]}...")
        except:
            pass
        
        # Fix BiDi number direction issues (reverse numbers so game shows them correctly)
        # Only apply to Arabic text
        if has_arabic:
            processed = self.processor.fix_bidi_numbers(processed)
        
        # Copy text to clipboard
        pyperclip.copy(processed)
        
        # Disable DLL filter to prevent our keys from triggering
        if hasattr(self, 'media_filter') and self.media_filter:
            self.media_filter.enable(False)
        
        # ==========================================
        # DUAL SEND MODE - Enter or Mouse
        # ==========================================
        send_mode = CONFIG.get('send_mode')
        
        if send_mode == 'enter':
            # ========== ENTER MODE (Fast + Smart) ==========
            
            # ══════════════════════════════════════════════════════════════
            # SMART CHAT DETECTION: كشف حالة الشات بالألوان
            # ══════════════════════════════════════════════════════════════
            open_color = CONFIG.get('chat_open_color')
            closed_color = CONFIG.get('chat_closed_color')
            detect_x = CONFIG.get('chat_detect_x')
            detect_y = CONFIG.get('chat_detect_y')
            
            # إذا تم تحديد ألوان الشات = استخدم الكشف الذكي
            if open_color and closed_color and detect_x != -1 and detect_y != -1:
                # ════════ SMART MODE: كشف اللون ════════
                try:
                    # ══════════════════════════════════════════════════════════
                    # GetPixel المباشر على نافذة اللعبة - أسرع طريقة ممكنة!
                    # يقرأ من DC النافذة مباشرة (يتجاهل overlay)
                    # ══════════════════════════════════════════════════════════
                    from ctypes import wintypes
                    
                    game_hwnd = self._target_game_hwnd if hasattr(self, '_target_game_hwnd') else None
                    detection_method = "UNKNOWN"  # لتتبع المشاكل
                    
                    if game_hwnd and ctypes.windll.user32.IsWindow(game_hwnd):
                        rect = wintypes.RECT()
                        ctypes.windll.user32.GetWindowRect(game_hwnd, ctypes.byref(rect))
                        
                        local_x = detect_x - rect.left
                        local_y = detect_y - rect.top
                        
                        if 0 <= local_x < (rect.right - rect.left) and 0 <= local_y < (rect.bottom - rect.top):
                            # GetPixel المباشر من نافذة اللعبة - بدون bitmap أو نسخ!
                            hdc_window = ctypes.windll.user32.GetDC(game_hwnd)
                            pixel = ctypes.windll.gdi32.GetPixel(hdc_window, local_x, local_y)
                            ctypes.windll.user32.ReleaseDC(game_hwnd, hdc_window)
                            detection_method = "GAME_HWND"
                            
                            # تحقق من فشل GetPixel (يرجع 0xFFFFFFFF عند الفشل)
                            if pixel == 0xFFFFFFFF:
                                print("[SMART] WARNING: GetPixel on game window returned CLR_INVALID - falling back to screen")
                                hdc = ctypes.windll.user32.GetDC(0)
                                pixel = ctypes.windll.gdi32.GetPixel(hdc, detect_x, detect_y)
                                ctypes.windll.user32.ReleaseDC(0, hdc)
                                detection_method = "SCREEN_FALLBACK"
                        else:
                            print(f"[SMART] WARNING: Coordinates outside window - using screen DC")
                            hdc = ctypes.windll.user32.GetDC(0)
                            pixel = ctypes.windll.gdi32.GetPixel(hdc, detect_x, detect_y)
                            ctypes.windll.user32.ReleaseDC(0, hdc)
                            detection_method = "SCREEN_COORDS"
                    else:
                        print(f"[SMART] WARNING: No game hwnd - using screen DC (hwnd={game_hwnd})")
                        hdc = ctypes.windll.user32.GetDC(0)
                        pixel = ctypes.windll.gdi32.GetPixel(hdc, detect_x, detect_y)
                        ctypes.windll.user32.ReleaseDC(0, hdc)
                        detection_method = "SCREEN_NO_HWND"
                    
                    # تحويل للـ RGB
                    current_r = pixel & 0xFF
                    current_g = (pixel >> 8) & 0xFF
                    current_b = (pixel >> 16) & 0xFF
                    
                    # تحويل ألوان الشات للـ RGB
                    from PyQt6.QtGui import QColor
                    open_qcolor = QColor(open_color)
                    closed_qcolor = QColor(closed_color)
                    
                    # مقارنة مع تسامح 25
                    tolerance = 25
                    
                    def colors_match(r1, g1, b1, r2, g2, b2):
                        return (abs(r1 - r2) <= tolerance and 
                                abs(g1 - g2) <= tolerance and 
                                abs(b1 - b2) <= tolerance)
                    
                    is_open = colors_match(current_r, current_g, current_b, 
                                          open_qcolor.red(), open_qcolor.green(), open_qcolor.blue())
                    is_closed = colors_match(current_r, current_g, current_b, 
                                            closed_qcolor.red(), closed_qcolor.green(), closed_qcolor.blue())
                    
                    print(f"[SMART] [{detection_method}] Detected: R={current_r} G={current_g} B={current_b} | Open={is_open} Closed={is_closed}")
                    
                    if is_closed:
                        # الشات مغلق = اضغط Enter لفتحه
                        enters_count = CONFIG.get('chat_closed_enters')
                        print(f"[SMART] Chat CLOSED - pressing {enters_count} Enter(s)")
                        for _ in range(enters_count):
                            keyboard.send('enter')
                            time.sleep(0.05)  # انتظار أطول بين كل Enter
                        time.sleep(0.08)  # انتظار إضافي لفتح الشات كاملاً
                    elif is_open:
                        # الشات مفتوح = لا تضغط Enter
                        print("[SMART] Chat OPEN - no Enter needed")
                    else:
                        # لون غير معروف = استخدم النظام القديم
                        print("[SMART] Unknown color - using fallback")
                        if self._mouse_clicked_since_send:
                            keyboard.send('enter')
                            time.sleep(0.05)
                            
                except Exception as e:
                    print(f"[SMART] Error: {e} - using fallback")
                    if self._mouse_clicked_since_send:
                        keyboard.send('enter')
                        time.sleep(0.05)
            else:
                # ════════ LEGACY MODE: النظام القديم ════════
                # SMART CHAT FOCUS: Only send Enter if mouse was clicked
                if self._mouse_clicked_since_send:
                    print("[SEND-ENTER] Using Enter (mouse was clicked or first message)")
                    keyboard.send('enter')      # فتح الشات
                    time.sleep(0.05)            # انتظار لفتح الشات
                else:
                    print("[SEND-ENTER] No Enter needed (chat should be open)")
            
            keyboard.send('ctrl+v')     # لصق النص
            time.sleep(0.03)            # انتظار للصق
            keyboard.send('enter')      # إرسال
            
            # Reset flag - next send without mouse click won't need opening Enter
            self._mouse_clicked_since_send = False
            
        else:
            # ========== MOUSE MODE (Click on chat) ==========
            print("[SEND-MOUSE] Using mouse click mode")
            
            # Get game chat location
            gx, gy = CONFIG.get('game_click_x'), CONFIG.get('game_click_y')
            if gx == -1 or gy == -1:
                print("[SEND-MOUSE] ERROR: Chat location not set!")
                if hasattr(self, 'media_filter') and self.media_filter:
                    self.media_filter.enable(True)
                return
            
            # ══════════════════════════════════════════════════════════
            # SMART MOUSE MODE: كشف حالة الشات قبل تحريك الماوس
            # ══════════════════════════════════════════════════════════
            need_mouse_click = True  # افتراضياً نحتاج click
            
            # التحقق إذا تم تحديد ألوان الشات
            open_color = CONFIG.get('chat_open_color')
            closed_color = CONFIG.get('chat_closed_color')
            detect_x = CONFIG.get('chat_detect_x')
            detect_y = CONFIG.get('chat_detect_y')
            
            if open_color and closed_color and detect_x != -1 and detect_y != -1:
                try:
                    # GetPixel المباشر على نافذة اللعبة (نفس طريقة Enter mode)
                    from ctypes import wintypes
                    
                    game_hwnd = self._target_game_hwnd if hasattr(self, '_target_game_hwnd') else None
                    
                    if game_hwnd and ctypes.windll.user32.IsWindow(game_hwnd):
                        rect = wintypes.RECT()
                        ctypes.windll.user32.GetWindowRect(game_hwnd, ctypes.byref(rect))
                        
                        local_x = detect_x - rect.left
                        local_y = detect_y - rect.top
                        
                        if 0 <= local_x < (rect.right - rect.left) and 0 <= local_y < (rect.bottom - rect.top):
                            # GetPixel المباشر - بدون bitmap!
                            hdc_window = ctypes.windll.user32.GetDC(game_hwnd)
                            pixel = ctypes.windll.gdi32.GetPixel(hdc_window, local_x, local_y)
                            ctypes.windll.user32.ReleaseDC(game_hwnd, hdc_window)
                            
                            # مقارنة الألوان
                            current_r = pixel & 0xFF
                            current_g = (pixel >> 8) & 0xFF
                            current_b = (pixel >> 16) & 0xFF
                            
                            from PyQt6.QtGui import QColor
                            open_qcolor = QColor(open_color)
                            
                            tolerance = 25
                            is_open = (abs(current_r - open_qcolor.red()) <= tolerance and 
                                      abs(current_g - open_qcolor.green()) <= tolerance and 
                                      abs(current_b - open_qcolor.blue()) <= tolerance)
                            
                            if is_open:
                                need_mouse_click = False
                                print("[SMART-MOUSE] Chat OPEN - skipping mouse click!")
                            else:
                                print("[SMART-MOUSE] Chat CLOSED - using mouse click")
                except Exception as e:
                    print(f"[SMART-MOUSE] Detection error: {e} - using mouse click")
            
            if need_mouse_click:
                # Save current mouse position
                original_pos = win32api.GetCursorPos()
                
                # Move to game chat and click
                win32api.SetCursorPos((gx, gy))
                time.sleep(0.02)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                time.sleep(0.05)
                
                # Paste and send
                keyboard.send('ctrl+v')
                time.sleep(0.03)
                keyboard.send('enter')
                time.sleep(0.02)
                
                # Return mouse to original position
                win32api.SetCursorPos(original_pos)
            else:
                # الشات مفتوح - لصق وإرسال مباشرة بدون تحريك الماوس
                keyboard.send('ctrl+v')
                time.sleep(0.03)
                keyboard.send('enter')
        
        # Re-enable filter after sending
        if hasattr(self, 'media_filter') and self.media_filter:
            self.media_filter.enable(True)
        
        # Remember what WE sent
        self._last_sent_message = processed
        
        self.text_edit.clear()
        
        # Re-apply first line end setting after clear (Arabic mode only)
        line_end = CONFIG.get('first_line_end')
        if line_end > 0 and self.is_arabic_mode:
            from PyQt6.QtGui import QTextBlockFormat
            block_format = QTextBlockFormat()
            block_format.setTextIndent(line_end)
            cursor = self.text_edit.textCursor()
            cursor.mergeBlockFormat(block_format)
            self.text_edit.setTextCursor(cursor)
        
        # If pinned - disable click-through (restore normal)
        if is_pinned:
            self._set_click_through(False)
            self.raise_()
            self.text_edit.setFocus()
        
        # عودة لـ READY
        self._input_state = "READY"

# =====================================
# TrayPopup - نافذة مخصصة للـ System Tray
# =====================================
# 🎨 تصميم glassmorphism مطابق لقائمة الشات
# =====================================
class TrayPopup(QWidget):
    def __init__(self, win, app):
        super().__init__()
        self.win = win
        self.app = app
        
        # إعدادات النافذة
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.Popup
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(200)
        
        # التصميم الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # الحاوية بتصميم glassmorphism
        container = QFrame(self)
        container.setObjectName("TrayContainer")
        container.setStyleSheet("""
            QFrame#TrayContainer {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 40, 55, 250),
                    stop:1 rgba(25, 30, 45, 255)
                );
                border: 1px solid rgba(100, 150, 220, 0.3);
                border-radius: 12px;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(5)
        
        # العنوان
        title = QLabel(f"Smart Keyboard v{VERSION}")
        title.setStyleSheet("""
            color: #fcb953;
            font-family: 'Segoe UI';
            font-size: 18px;
            font-weight: 400;
            padding: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)
        
        # فاصل
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent,
                stop:0.5 rgba(100, 150, 220, 0.4),
                stop:1 transparent
            );
        """)
        container_layout.addWidget(separator)
        
        # زر Show (Insert)
        btn_show = self._create_button("insert تشغيل", "Run", self._on_show)
        container_layout.addWidget(btn_show)
        
        # زر Exit
        btn_exit = self._create_button("خروج", "Exit", self._on_exit)
        container_layout.addWidget(btn_exit)
        
        main_layout.addWidget(container)
        self.adjustSize()
        
        # إغلاق عند النقر خارج النافذة
        self._setup_click_outside()
    
    def _create_button(self, arabic, english, callback):
        """إنشاء زر بنفس تصميم قائمة الشات"""
        btn = QWidget()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.callback = callback
        
        layout = QHBoxLayout(btn)
        layout.setContentsMargins(10, 8, 10, 8)
        
        lbl_eng = QLabel(english)
        lbl_eng.setStyleSheet("""
            color: rgba(180, 180, 180, 200);
            font-family: 'Segoe UI';
            font-size: 18px;
        """)
        
        lbl_ar = QLabel(arabic)
        lbl_ar.setStyleSheet("""
            color: #e6a84a;
            font-family: 'Segoe UI';
            font-size: 18px;
            font-weight: 400;
        """)
        
        layout.addWidget(lbl_eng)
        layout.addStretch()
        layout.addWidget(lbl_ar)
        
        btn.lbl_eng = lbl_eng
        btn.lbl_ar = lbl_ar
        
        # Hover effects
        def enter(e):
            
            btn.lbl_ar.setStyleSheet("color: #fcb953; font-family: 'Segoe UI'; font-size: 18px; font-weight: 600;")
            btn.lbl_eng.setStyleSheet("color: rgba(220, 220, 220, 255); font-family: 'Segoe UI'; font-size: 18px;")
        
        def leave(e):
            btn.setStyleSheet("background: transparent; border-radius: 8px;")
            btn.lbl_ar.setStyleSheet("color: #e6a84a; font-family: 'Segoe UI'; font-size: 18px; font-weight: 400;")
            btn.lbl_eng.setStyleSheet("color: rgba(180, 180, 180, 200); font-family: 'Segoe UI'; font-size: 18px;")
        
        def click(e):
            if e.button() == Qt.MouseButton.LeftButton:
                self.hide()
                btn.callback()
        
        btn.enterEvent = enter
        btn.leaveEvent = leave
        btn.mouseReleaseEvent = click
        
        return btn
    
    def _setup_click_outside(self):
        """إغلاق النافذة عند النقر خارجها"""
        self.click_timer = QTimer(self)
        self.click_timer.timeout.connect(self._check_click)
        self.ignore_initial = True
        
    def showEvent(self, e):
        super().showEvent(e)
        self.ignore_initial = True
        self.click_timer.start(100)
        
    def hideEvent(self, e):
        super().hideEvent(e)
        self.click_timer.stop()
    
    def _check_click(self):
        left_down = win32api.GetAsyncKeyState(0x01) & 0x8000  # كلك يسار
        
        if not left_down:
            # عند رفع الزر، إعادة تعيين
            self.ignore_initial = False
            return
            
        if self.ignore_initial:
            # تجاهل النقرة الأولى (التي فتحت القائمة)
            return
            
        cursor = QCursor.pos()
        if not self.geometry().contains(cursor):
            self.hide()
    
    def _on_show(self):
        self.win.toggle()
    
    def _on_exit(self):
        self.app.quit()
    
    def show_at_cursor(self):
        """إظهار النافذة في طرف الأيقونة (يمين وفوق)"""
        cursor = QCursor.pos()
        screen = QApplication.primaryScreen().geometry()
        
        # الموقع: يمين وفوق المؤشر
        x = cursor.x()  # يبدأ من موقع المؤشر (ليس في الوسط)
        y = cursor.y() - self.height()  # فوق المؤشر
        
        # منع الخروج من الشاشة
        if x + self.width() > screen.width():
            x = cursor.x() - self.width()  # عكس للشمال
        if y < 0:
            y = cursor.y()  # أسفل المؤشر
            
        self.move(x, y)
        self.show()
        self.raise_()

if __name__ == '__main__':
    # Disable high DPI scaling - PyQt6 enables this by default, making everything bigger
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Single Instance Check - منع تشغيل أكثر من نسخة
    # ═══════════════════════════════════════════════════════════════════════════
    MUTEX_NAME = "SmartKeyboard_SingleInstance_Mutex"
    
    try:
        # محاولة إنشاء mutex
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        last_error = ctypes.windll.kernel32.GetLastError()
        
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            print("[STARTUP] Another instance is already running. Exiting...")
            sys.exit(0)
        
        print("[STARTUP] Single instance check passed.")
    except Exception as e:
        print(f"[STARTUP] Mutex check failed: {e}")
    
    app = QApplication(sys.argv)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # فحص إذا كان التشغيل بعد تحديث ناجح
    # ═══════════════════════════════════════════════════════════════════════════
    update_flag_file = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), ".update_success")
    if os.path.exists(update_flag_file):
        try:
            # قراءة الإصدار الجديد من الملف
            with open(update_flag_file, 'r') as f:
                new_version = f.read().strip() or VERSION
            os.remove(update_flag_file)
            
            # عرض نافذة نجاح التحديث الجميلة
            show_update_success(new_version)
            print(f"[STARTUP] Update success message shown for version {new_version}")
        except Exception as e:
            print(f"[STARTUP] Error showing update message: {e}")
    
    win = OverlayWindow()
    win.show()
    win.hide()
    
    # إنشاء أيقونة System Tray
    tray = QSystemTrayIcon(app)
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Icons')
    ico_path = os.path.join(icons_dir, 'app.ico')
    if os.path.exists(ico_path):
        tray.setIcon(QIcon(ico_path))
    else:
        tray_pixmap = QPixmap(16, 16)
        tray_pixmap.fill(QColor(0, 120, 215))
        tray.setIcon(QIcon(tray_pixmap))
    tray.setToolTip(f"Smart Keyboard v{VERSION}")
    
    # إنشاء النافذة المخصصة بدلاً من القائمة
    tray_popup = TrayPopup(win, app)
    
    # ربط الضغط على الأيقونة
    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # كلك يسار
            win.toggle()
        elif reason == QSystemTrayIcon.ActivationReason.Context:  # كلك يمين
            tray_popup.show_at_cursor()
    
    tray.activated.connect(on_tray_activated)
    tray.show()
    
    print(f"Smart Keyboard v{VERSION} Ready. Press Insert.")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # التحقق من التحديثات (بعد 3 ثواني من البدء)
    # ═══════════════════════════════════════════════════════════════════════════
    # متغير global لحفظ نافذة التحديث (منع حذفها)
    global update_dialog
    update_dialog = None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # حفظ مسار exe للتحديث التلقائي
    # ═══════════════════════════════════════════════════════════════════════════
    def save_exe_path():
        """حفظ مسار exe الحالي في الإعدادات"""
        current_path = os.path.abspath(sys.argv[0])
        
        # تجاهل المسارات المؤقتة (Nuitka onefile temp)
        if 'Temp' not in current_path and 'temp' not in current_path:
            saved_path = CONFIG.get('exe_path')
            if saved_path != current_path:
                CONFIG.set('exe_path', current_path)
                CONFIG.save_config()
                print(f"[STARTUP] Saved exe path: {current_path}")
            else:
                print(f"[STARTUP] Exe path already saved: {current_path}")
        else:
            # نحن في مجلد مؤقت - استخدام المسار المحفوظ
            saved_path = CONFIG.get('exe_path')
            if saved_path:
                print(f"[STARTUP] Using saved exe path: {saved_path}")
            else:
                print("[STARTUP] Warning: Running from temp, no saved path!")
    
    save_exe_path()
    
    def check_updates_delayed():
        global update_dialog
        update_dialog = check_for_updates(parent=None, config=CONFIG, silent=True)
        if update_dialog:
            print("[UPDATE] Update dialog created and shown")
    
    QTimer.singleShot(3000, check_updates_delayed)  # 3 ثواني تأخير
    
    sys.exit(app.exec())

