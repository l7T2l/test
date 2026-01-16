// ═══════════════════════════════════════════════════════════════════════════════
// SettingsWindow.xaml.cs - نافذة الإعدادات الرئيسية
// المقابل لـ: Styles/main_styles.py class SidebarTest (السطور 51-757)
// تحويل سطر بسطر - كل وظيفة وكل ستايل مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media.Imaging;
using System.Collections.Generic;
using Window = System.Windows.Window;
using Color = System.Windows.Media.Color;
using ColorConverter = System.Windows.Media.ColorConverter;
using SolidColorBrush = System.Windows.Media.SolidColorBrush;
using LinearGradientBrush = System.Windows.Media.LinearGradientBrush;
using Button = System.Windows.Controls.Button;

namespace SmartKeyboard.Styles
{
    /// <summary>
    /// class SidebarTest(QDialog): - السطر 51
    /// نافذة الإعدادات الجديدة مع Sidebar
    /// </summary>
    public partial class SettingsWindow : Window
    {
        // ═══════════════════════════════════════════════════════════════
        // P/Invoke
        // ═══════════════════════════════════════════════════════════════
        [DllImport("user32.dll")]
        private static extern int GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll")]
        private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

        private const int GWL_EXSTYLE = -20;
        private const int WS_EX_NOACTIVATE = 0x08000000;

        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - من __init__ السطور 58-101
        // ═══════════════════════════════════════════════════════════════

        // السطر 66: self.nav_buttons = []
        private readonly List<Button> _navButtons = new();

        // السطر 133: drag_pos
        private System.Windows.Point _dragPos;

        // Current active page index
        private int _currentPageIndex = 0;

        // Page instances - السطور 216, 232, 250, 266
        private ControlPage? _controlPage;
        private SettingsPage? _settingsPage;
        private ChatPage? _chatPage;
        private AboutPage? _aboutPage;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - من __init__ السطور 58-101
        // ═══════════════════════════════════════════════════════════════
        public SettingsWindow()
        {
            InitializeComponent();

            // السطر 83: self.resize(500, 500)
            this.Width = 500;
            this.Height = 500;

            // السطور 86-90: استعادة موقع النافذة من CONFIG
            int savedX = CONFIG.Instance.SettingsX;
            int savedY = CONFIG.Instance.SettingsY;
            if (savedX != -1 && savedY != -1)
            {
                this.Left = savedX;
                this.Top = savedY;
            }

            // Store nav buttons
            _navButtons.Add(BtnControl);
            _navButtons.Add(BtnSettings);
            _navButtons.Add(BtnDetect);
            _navButtons.Add(BtnAbout);

            // Update version label - السطر 416
            VersionLabel.Text = $"v{Version.VERSION}";
        }

        // ═══════════════════════════════════════════════════════════════
        // Window_Loaded - من setup_ui + apply_no_activate
        // ═══════════════════════════════════════════════════════════════
        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            // السطور 103-110: apply_no_activate()
            ApplyNoActivate();

            // Load logo - السطور 327-349
            LoadLogo();

            // Apply opacity from settings - السطور 447-449
            ApplyOpacity();

            // Initialize pages
            InitializePages();

            // السطر 433: _set_active_button(0) - التحكم نشط افتراضياً
            SetActiveButton(0);
        }

        // ═══════════════════════════════════════════════════════════════
        // apply_no_activate - السطور 103-110
        // ═══════════════════════════════════════════════════════════════
        private void ApplyNoActivate()
        {
            IntPtr hwnd = new WindowInteropHelper(this).Handle;
            int style = GetWindowLong(hwnd, GWL_EXSTYLE);
            SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE);
        }

        // ═══════════════════════════════════════════════════════════════
        // LoadLogo - السطور 324-349
        // ═══════════════════════════════════════════════════════════════
        private void LoadLogo()
        {
            try
            {
                string exeDir = AppDomain.CurrentDomain.BaseDirectory;
                string logoPath = Path.Combine(exeDir, "Icons", "app_256.png");

                if (File.Exists(logoPath))
                {
                    BitmapImage bitmap = new BitmapImage();
                    bitmap.BeginInit();
                    bitmap.UriSource = new Uri(logoPath, UriKind.Absolute);
                    bitmap.DecodePixelWidth = 60;  // السطر 333: logo_size = 60
                    bitmap.DecodePixelHeight = 60;
                    bitmap.EndInit();
                    LogoImage.Source = bitmap;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[SETTINGS] Logo load error: {ex.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // ApplyOpacity - السطور 446-449
        // ═══════════════════════════════════════════════════════════════
        private void ApplyOpacity()
        {
            int opacity = CONFIG.Instance.SettingsOpacity;
            byte alpha = (byte)Math.Clamp(opacity, 0, 255);

            // Update ContentFrame gradient - السطور 467-468
            ContentBgTop.Color = Color.FromArgb(alpha, 30, 36, 54);
            ContentBgBottom.Color = Color.FromArgb(alpha, 20, 26, 44);

            // Update Sidebar gradient - السطور 488-489
            SidebarBgTop.Color = Color.FromArgb(alpha, 22, 29, 51);
            SidebarBgBottom.Color = Color.FromArgb(alpha, 11, 16, 40);
        }

        // ═══════════════════════════════════════════════════════════════
        // InitializePages
        // ═══════════════════════════════════════════════════════════════
        private void InitializePages()
        {
            // Create page instances - السطور 208-269
            _controlPage = new ControlPage();
            _settingsPage = new SettingsPage();
            _chatPage = new ChatPage();
            _aboutPage = new AboutPage();
        }

        // ═══════════════════════════════════════════════════════════════
        // NavButton_Click - من _set_active_button السطور 684-713
        // ═══════════════════════════════════════════════════════════════
        private void NavButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button btn && btn.Tag is string indexStr && int.TryParse(indexStr, out int index))
            {
                SetActiveButton(index);
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // _set_active_button - السطور 684-713
        // ═══════════════════════════════════════════════════════════════
        private void SetActiveButton(int index)
        {
            _currentPageIndex = index;

            // السطور 698-708: Update button states
            for (int i = 0; i < _navButtons.Count; i++)
            {
                var btn = _navButtons[i];
                if (i == index)
                {
                    // Active button styling
                    btn.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#48B4FF"));
                    btn.BorderThickness = new Thickness(0, 0, 3, 0);
                    btn.BorderBrush = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#ff9a3c"));
                    btn.Background = new LinearGradientBrush(
                        (Color)ColorConverter.ConvertFromString("#664A90E2"),
                        (Color)ColorConverter.ConvertFromString("#004A90E2"),
                        new System.Windows.Point(1, 0),
                        new System.Windows.Point(0, 0));
                }
                else
                {
                    // Inactive button styling
                    btn.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#A0D8FF"));
                    btn.BorderThickness = new Thickness(0);
                    btn.Background = System.Windows.Media.Brushes.Transparent;
                }
            }

            // السطر 711: Switch page
            switch (index)
            {
                case 0: // التحكم
                    ContentFrame_Page.Content = _controlPage;
                    break;
                case 1: // الإعدادات
                    ContentFrame_Page.Content = _settingsPage;
                    break;
                case 2: // تحديد (كشف الشات)
                    ContentFrame_Page.Content = _chatPage;
                    break;
                case 3: // حول
                    ContentFrame_Page.Content = _aboutPage;
                    break;
            }

            Console.WriteLine($"[NAV] Active button switched to: {index}");
        }

        // ═══════════════════════════════════════════════════════════════
        // CloseButton_Click - من btn_close.clicked.connect(self.close)
        // ═══════════════════════════════════════════════════════════════
        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }

        // ═══════════════════════════════════════════════════════════════
        // Mouse Events - من mousePressEvent/mouseMoveEvent/mouseReleaseEvent
        // السطور 728-750
        // ═══════════════════════════════════════════════════════════════
        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            // السطور 732-733
            _dragPos = e.GetPosition(this);
            this.DragMove();
        }

        private void Window_MouseMove(object sender, System.Windows.Input.MouseEventArgs e)
        {
            // Drag is handled by DragMove()
        }

        private void Window_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            // السطور 746-750: Save position to CONFIG
            CONFIG.Instance.SettingsX = (int)this.Left;
            CONFIG.Instance.SettingsY = (int)this.Top;
        }

        // ═══════════════════════════════════════════════════════════════
        // keyPressEvent - السطور 752-757
        // ═══════════════════════════════════════════════════════════════
        private void Window_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            // السطور 756-757
            if (e.Key == Key.Escape)
            {
                this.Close();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // update_loc_display - السطور 719-722
        // ═══════════════════════════════════════════════════════════════
        public void UpdateLocDisplay()
        {
            _controlPage?.UpdateLocDisplay();
        }
    }
}
