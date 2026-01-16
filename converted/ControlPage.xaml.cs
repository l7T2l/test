// ═══════════════════════════════════════════════════════════════════════════════
// ControlPage.xaml.cs - صفحة التحكم
// المقابل لـ: Styles/control_page.py class ControlPageContent (السطور 18-447)
// تحويل سطر بسطر - كل وظيفة وكل ستايل مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using UserControl = System.Windows.Controls.UserControl;
using Color = System.Windows.Media.Color;
using ColorConverter = System.Windows.Media.ColorConverter;
using SolidColorBrush = System.Windows.Media.SolidColorBrush;
using Colors = System.Windows.Media.Colors;

namespace SmartKeyboard.Styles
{
    /// <summary>
    /// class ControlPageContent(QWidget): - السطر 18
    /// محتوى صفحة التحكم - للربط مع الإطار الرئيسي
    /// </summary>
    public partial class ControlPage : UserControl
    {
        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - من __init__ السطور 21-30
        // ═══════════════════════════════════════════════════════════════

        // السطر 29: self.current_send_mode = config.get('send_mode') if config else 'enter'
        private string _currentSendMode = "enter";

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - من __init__ السطور 21-36
        // ═══════════════════════════════════════════════════════════════
        public ControlPage()
        {
            InitializeComponent();

            // السطر 29: تهيئة وضع الإرسال من CONFIG
            _currentSendMode = CONFIG.Instance.SendMode;

            // السطور 31-36: setup_ui + apply_style + update displays
            LoadIcons();
            UpdateLocDisplay();
            UpdateSendModeButtons();
        }

        // ═══════════════════════════════════════════════════════════════
        // LoadIcons - تحميل الأيقونات
        // من السطور 77-88, 100-104, 131-135, 143-161
        // ═══════════════════════════════════════════════════════════════
        private void LoadIcons()
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory;
            string iconsDir = Path.Combine(exeDir, "Icons");

            // السطور 77-78: أيقونة التحكم للهيدر
            LoadIcon(HeaderIcon, Path.Combine(iconsDir, "control.png"), 24);

            // السطور 100: أيقونة موقع الكتابة
            LoadIcon(MouseSiteIcon, Path.Combine(iconsDir, "mouse_site.png"), 24);

            // السطر 131: أيقونة لوحة المفاتيح
            LoadIcon(KeyboardIcon, Path.Combine(iconsDir, "keyboard.png"), 24);
        }

        private void LoadIcon(System.Windows.Controls.Image imageElement, string path, int size)
        {
            try
            {
                if (File.Exists(path))
                {
                    BitmapImage bitmap = new BitmapImage();
                    bitmap.BeginInit();
                    bitmap.UriSource = new Uri(path, UriKind.Absolute);
                    bitmap.DecodePixelWidth = size;
                    bitmap.DecodePixelHeight = size;
                    bitmap.EndInit();
                    imageElement.Source = bitmap;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[CONTROL] Icon load error: {ex.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // update_loc_display - السطور 233-252
        // تحديث عرض الموقع من CONFIG
        // ═══════════════════════════════════════════════════════════════
        public void UpdateLocDisplay()
        {
            // السطور 236-238: الحصول على إحداثيات اللعبة
            int x = CONFIG.Instance.GameClickX;
            int y = CONFIG.Instance.GameClickY;
            string gameName = CONFIG.Instance.GameName;

            // السطور 239-252: تحديث النص
            if (x != -1)
            {
                if (!string.IsNullOrEmpty(gameName))
                {
                    // السطور 242-246: استخراج اسم البرنامج فقط
                    string displayName = gameName;
                    if (gameName.Contains(" - "))
                    {
                        displayName = gameName.Split(" - ")[^1].Trim();
                    }
                    LocationLabel.Text = $"✔ {displayName}\nX: {x}, Y: {y}";
                    LocationLabel.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#00ff00"));
                }
                else
                {
                    LocationLabel.Text = $"✔ X: {x}, Y: {y}";
                    LocationLabel.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#00ff00"));
                }
            }
            else
            {
                LocationLabel.Text = "❌ غير محدد موقع الكتابة";
                LocationLabel.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#b8e6c3"));
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // reset_location - السطور 254-261
        // إعادة تعيين الموقع المحفوظ
        // ═══════════════════════════════════════════════════════════════
        private void ResetLocationButton_Click(object sender, RoutedEventArgs e)
        {
            // السطور 257-259
            CONFIG.Instance.GameClickX = -1;
            CONFIG.Instance.GameClickY = -1;
            CONFIG.Instance.GameName = "";

            // السطور 260-261
            UpdateLocDisplay();
            Console.WriteLine("✓ Location reset!");
        }

        // ═══════════════════════════════════════════════════════════════
        // set_send_mode - السطور 263-269
        // تغيير وضع الإرسال
        // ═══════════════════════════════════════════════════════════════
        private void EnterModeButton_Click(object sender, RoutedEventArgs e)
        {
            SetSendMode("enter");
        }

        private void MouseModeButton_Click(object sender, RoutedEventArgs e)
        {
            SetSendMode("mouse");
        }

        private void SetSendMode(string mode)
        {
            // السطور 265-267
            CONFIG.Instance.SendMode = mode;
            _currentSendMode = mode;

            // السطور 268-269
            UpdateSendModeButtons();
            Console.WriteLine($"[SETTINGS] Send mode changed to: {mode}");
        }

        // ═══════════════════════════════════════════════════════════════
        // update_send_mode_buttons - السطور 271-324
        // تحديث ستايل أزرار الإرسال
        // ═══════════════════════════════════════════════════════════════
        private void UpdateSendModeButtons()
        {
            if (_currentSendMode == "enter")
            {
                // السطور 273-298: Enter نشط - أزرق قوي
                EnterModeButton.Foreground = new SolidColorBrush(Colors.White);
                // السطر 298: تحديث التلميح
                SendModeHintLabel.Text = "إرسال النص عن طريق الـ Enter";
            }
            else
            {
                // السطور 299-324: Mouse نشط - أزرق قوي
                MouseModeButton.Foreground = new SolidColorBrush(Colors.White);
                // السطر 324: تحديث التلميح
                SendModeHintLabel.Text = "إرسال النص عن طريق الـ Mouse";
            }
        }
    }
}
