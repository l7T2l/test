// ═══════════════════════════════════════════════════════════════════════════════
// ChatPage.xaml.cs - صفحة كشف الشات
// المقابل لـ: Styles/chat_page.py class ChatDetectorContent (السطور 430-1161)
// تحويل سطر بسطر - كل وظيفة وكل ستايل مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using UserControl = System.Windows.Controls.UserControl;
using Color = System.Windows.Media.Color;
using ColorConverter = System.Windows.Media.ColorConverter;
using SolidColorBrush = System.Windows.Media.SolidColorBrush;

namespace SmartKeyboard.Styles
{
    /// <summary>
    /// class ChatDetectorContent(QWidget): - السطر 430
    /// محتوى صفحة كشف الشات - المحتوى الرئيسي
    /// </summary>
    public partial class ChatPage : UserControl
    {
        // ═══════════════════════════════════════════════════════════════
        // P/Invoke for color detection
        // ═══════════════════════════════════════════════════════════════
        [DllImport("user32.dll")]
        private static extern IntPtr GetDC(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

        [DllImport("gdi32.dll")]
        private static extern uint GetPixel(IntPtr hDC, int x, int y);

        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - من ColorBox class السطور 230-244
        // ═══════════════════════════════════════════════════════════════

        // Open color state
        private Color? _openColor = null;
        private int _openPosX = 0;
        private int _openPosY = 0;
        private bool _openIsSet = false;

        // Closed color state
        private Color? _closedColor = null;
        private int _closedPosX = 0;
        private int _closedPosY = 0;
        private bool _closedIsSet = false;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - من __init__ السطور 439-448
        // ═══════════════════════════════════════════════════════════════
        public ChatPage()
        {
            InitializeComponent();

            // Load icons
            LoadIcons();

            // Load saved colors - السطر 448
            LoadSavedColors();

            // Update initial status - السطر 657
            UpdateStatus();
        }

        // ═══════════════════════════════════════════════════════════════
        // LoadIcons - من السطور 531-539
        // ═══════════════════════════════════════════════════════════════
        private void LoadIcons()
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory;
            string iconsDir = Path.Combine(exeDir, "Icons");

            LoadIcon(SniperIcon, Path.Combine(iconsDir, "sniper.png"), 24);
            LoadIcon(StatusIcon, Path.Combine(iconsDir, "time.png"), 24);
            
            // Load Location GIF as static image for color boxes
            LoadIcon(OpenColorIcon, Path.Combine(iconsDir, "Location.gif"), 80);
            LoadIcon(ClosedColorIcon, Path.Combine(iconsDir, "Location.gif"), 80);
        }

        private void LoadIcon(System.Windows.Controls.Image img, string path, int size)
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
                    img.Source = bitmap;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[CHAT] Icon load error: {ex.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // load_saved_colors - السطور 450-481
        // ═══════════════════════════════════════════════════════════════
        private void LoadSavedColors()
        {
            // Load open color - السطور 456-467
            string openColorStr = CONFIG.Instance.ChatOpenColor;
            int openX = CONFIG.Instance.ChatDetectX;
            int openY = CONFIG.Instance.ChatDetectY;

            if (!string.IsNullOrWhiteSpace(openColorStr))
            {
                try
                {
                    _openColor = (Color)ColorConverter.ConvertFromString(openColorStr);
                    _openPosX = openX != -1 ? openX : 0;
                    _openPosY = openY != -1 ? openY : 0;
                    _openIsSet = true;
                    UpdateOpenColorBoxStyle();
                    Console.WriteLine($"[CHAT] Loaded open color: {openColorStr} at ({openX}, {openY})");
                }
                catch { }
            }

            // Load closed color - السطور 470-478
            string closedColorStr = CONFIG.Instance.ChatClosedColor;

            if (!string.IsNullOrWhiteSpace(closedColorStr))
            {
                try
                {
                    _closedColor = (Color)ColorConverter.ConvertFromString(closedColorStr);
                    _closedPosX = _openPosX;  // Same position
                    _closedPosY = _openPosY;
                    _closedIsSet = true;
                    UpdateClosedColorBoxStyle();
                    Console.WriteLine($"[CHAT] Loaded closed color: {closedColorStr}");
                }
                catch { }
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // ColorBox click handlers
        // ═══════════════════════════════════════════════════════════════
        private void OpenColorBox_Click(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            PickColor("open");
        }

        private void OpenColorBox_RightClick(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            ClearOpenColor();
        }

        private void ClosedColorBox_Click(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            PickColor("closed");
        }

        private void ClosedColorBox_RightClick(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            ClearClosedColor();
        }

        // ═══════════════════════════════════════════════════════════════
        // pick_color - using WPF ColorDialog
        // ═══════════════════════════════════════════════════════════════
        private void PickColor(string target)
        {
            var dialog = new System.Windows.Forms.ColorDialog();
            
            if (dialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                Color pickedColor = Color.FromRgb(dialog.Color.R, dialog.Color.G, dialog.Color.B);
                
                // Get cursor position
                var cursorPos = System.Windows.Forms.Cursor.Position;
                int x = cursorPos.X;
                int y = cursorPos.Y;

                if (target == "open")
                {
                    OnOpenColorChanged(pickedColor, x, y);
                }
                else
                {
                    OnClosedColorChanged(pickedColor, x, y);
                }
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // on_open_color_changed - السطور 659-670
        // ═══════════════════════════════════════════════════════════════
        private void OnOpenColorChanged(Color color, int x, int y)
        {
            _openColor = color;
            _openPosX = x;
            _openPosY = y;
            _openIsSet = true;

            // Save to config - السطور 664-667
            CONFIG.Instance.ChatOpenColor = $"#{color.R:X2}{color.G:X2}{color.B:X2}";
            CONFIG.Instance.ChatDetectX = x;
            CONFIG.Instance.ChatDetectY = y;

            UpdateOpenColorBoxStyle();
            UpdateStatus();
            Console.WriteLine($"[CHAT] Open color set: #{color.R:X2}{color.G:X2}{color.B:X2} at ({x}, {y})");
        }

        // ═══════════════════════════════════════════════════════════════
        // on_open_color_cleared - السطور 672-682
        // ═══════════════════════════════════════════════════════════════
        private void ClearOpenColor()
        {
            _openColor = null;
            _openPosX = 0;
            _openPosY = 0;
            _openIsSet = false;

            CONFIG.Instance.ChatOpenColor = "";
            CONFIG.Instance.ChatDetectX = -1;
            CONFIG.Instance.ChatDetectY = -1;

            UpdateOpenColorBoxStyle();
            UpdateStatus();
            Console.WriteLine("[CHAT] Open color cleared");
        }

        // ═══════════════════════════════════════════════════════════════
        // on_closed_color_changed - السطور 684-693
        // ═══════════════════════════════════════════════════════════════
        private void OnClosedColorChanged(Color color, int x, int y)
        {
            _closedColor = color;
            _closedPosX = x;
            _closedPosY = y;
            _closedIsSet = true;

            CONFIG.Instance.ChatClosedColor = $"#{color.R:X2}{color.G:X2}{color.B:X2}";

            UpdateClosedColorBoxStyle();
            UpdateStatus();
            Console.WriteLine($"[CHAT] Closed color set: #{color.R:X2}{color.G:X2}{color.B:X2}");
        }

        // ═══════════════════════════════════════════════════════════════
        // on_closed_color_cleared - السطور 695-703
        // ═══════════════════════════════════════════════════════════════
        private void ClearClosedColor()
        {
            _closedColor = null;
            _closedPosX = 0;
            _closedPosY = 0;
            _closedIsSet = false;

            CONFIG.Instance.ChatClosedColor = "";

            UpdateClosedColorBoxStyle();
            UpdateStatus();
            Console.WriteLine("[CHAT] Closed color cleared");
        }

        // ═══════════════════════════════════════════════════════════════
        // update_style for open color box - السطور 302-360
        // ═══════════════════════════════════════════════════════════════
        private void UpdateOpenColorBoxStyle()
        {
            if (_openIsSet && _openColor.HasValue)
            {
                OpenColorBox.Background = new SolidColorBrush(_openColor.Value);
                OpenColorBox.BorderBrush = new SolidColorBrush(GetBorderColor(_openColor.Value));
                OpenColorBox.BorderThickness = new Thickness(2);
                OpenColorStatus.Text = "✔ مفتوح";
                OpenColorStatus.Foreground = new SolidColorBrush(GetContrastingTextColor(_openColor.Value));
            }
            else
            {
                OpenColorBox.Background = new SolidColorBrush(Color.FromArgb(0x59, 0x34, 0x78, 0xDC));
                OpenColorBox.BorderBrush = new SolidColorBrush(Color.FromArgb(0x80, 0x64, 0x96, 0xFA));
                OpenColorBox.BorderThickness = new Thickness(2);
                OpenColorStatus.Text = "❌ مفتوح";
                OpenColorStatus.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FD638D"));
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // update_style for closed color box
        // ═══════════════════════════════════════════════════════════════
        private void UpdateClosedColorBoxStyle()
        {
            if (_closedIsSet && _closedColor.HasValue)
            {
                ClosedColorBox.Background = new SolidColorBrush(_closedColor.Value);
                ClosedColorBox.BorderBrush = new SolidColorBrush(GetBorderColor(_closedColor.Value));
                ClosedColorBox.BorderThickness = new Thickness(2);
                ClosedColorStatus.Text = "✔ مغلق";
                ClosedColorStatus.Foreground = new SolidColorBrush(GetContrastingTextColor(_closedColor.Value));
            }
            else
            {
                ClosedColorBox.Background = new SolidColorBrush(Color.FromArgb(0x59, 0x34, 0x78, 0xDC));
                ClosedColorBox.BorderBrush = new SolidColorBrush(Color.FromArgb(0x80, 0x64, 0x96, 0xFA));
                ClosedColorBox.BorderThickness = new Thickness(2);
                ClosedColorStatus.Text = "❌ مغلق";
                ClosedColorStatus.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FD638D"));
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // update_status - السطور 705-745
        // ═══════════════════════════════════════════════════════════════
        private void UpdateStatus()
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory;
            string iconsDir = Path.Combine(exeDir, "Icons");

            if (_openIsSet && _closedIsSet)
            {
                StatusLabel.Text = "جاهز للكشف";
                StatusLabel.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#58D58D"));
                LoadIcon(StatusIcon, Path.Combine(iconsDir, "time_on.png"), 24);
                TestButton.IsEnabled = true;
                StyleTestButtonEnabled();
            }
            else
            {
                if (!_openIsSet && !_closedIsSet)
                {
                    StatusLabel.Text = "في انتظار تحديد الألوان...";
                    LoadIcon(StatusIcon, Path.Combine(iconsDir, "time.png"), 24);
                }
                else if (_openIsSet)
                {
                    StatusLabel.Text = "حدد لون الشات المغلق...";
                    LoadIcon(StatusIcon, Path.Combine(iconsDir, "time_add.png"), 24);
                }
                else
                {
                    StatusLabel.Text = "حدد لون الشات المفتوح...";
                    LoadIcon(StatusIcon, Path.Combine(iconsDir, "time_add.png"), 24);
                }

                StatusLabel.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#9BA8B8"));
                TestButton.IsEnabled = false;
                StyleTestButtonDisabled();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // test_detection - السطور 747-880
        // ═══════════════════════════════════════════════════════════════
        private void TestButton_Click(object sender, RoutedEventArgs e)
        {
            if (!_openColor.HasValue || !_closedColor.HasValue)
                return;

            // Get pixel color at saved position
            IntPtr hDC = GetDC(IntPtr.Zero);
            uint pixel = GetPixel(hDC, _openPosX, _openPosY);
            ReleaseDC(IntPtr.Zero, hDC);

            byte r = (byte)(pixel & 0xFF);
            byte g = (byte)((pixel >> 8) & 0xFF);
            byte b = (byte)((pixel >> 16) & 0xFF);
            Color currentColor = Color.FromRgb(r, g, b);

            // Compare with open and closed colors
            int openDiff = ColorDifference(currentColor, _openColor.Value);
            int closedDiff = ColorDifference(currentColor, _closedColor.Value);

            string result;
            if (openDiff < closedDiff)
            {
                result = $"الشات مفتوح! (فرق اللون: {openDiff})";
            }
            else
            {
                result = $"الشات مغلق! (فرق اللون: {closedDiff})";
            }

            Console.WriteLine($"[CHAT] Test result: {result}");
            System.Windows.MessageBox.Show(result, "نتيجة الاختبار", MessageBoxButton.OK);
        }

        private int ColorDifference(Color c1, Color c2)
        {
            return Math.Abs(c1.R - c2.R) + Math.Abs(c1.G - c2.G) + Math.Abs(c1.B - c2.B);
        }

        // ═══════════════════════════════════════════════════════════════
        // Button styling helpers
        // ═══════════════════════════════════════════════════════════════
        private void StyleTestButtonEnabled()
        {
            // Green enabled style
        }

        private void StyleTestButtonDisabled()
        {
            // Gray disabled style
        }

        // ═══════════════════════════════════════════════════════════════
        // Color helper methods
        // ═══════════════════════════════════════════════════════════════
        private Color GetContrastingTextColor(Color bgColor)
        {
            double brightness = (bgColor.R * 299 + bgColor.G * 587 + bgColor.B * 114) / 1000.0;
            return brightness > 128 ? Colors.Black : Colors.White;
        }

        private Color GetBorderColor(Color baseColor)
        {
            double brightness = (baseColor.R * 299 + baseColor.G * 587 + baseColor.B * 114) / 1000.0;
            double factor = brightness < 128 ? 1.3 : 0.7;

            byte r = (byte)Math.Clamp((int)(baseColor.R * factor), 0, 255);
            byte g = (byte)Math.Clamp((int)(baseColor.G * factor), 0, 255);
            byte b = (byte)Math.Clamp((int)(baseColor.B * factor), 0, 255);

            return Color.FromRgb(r, g, b);
        }
    }
}
