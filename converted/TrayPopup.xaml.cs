// ═══════════════════════════════════════════════════════════════════════════════
// TrayPopup.xaml.cs - نافذة System Tray المنبثقة
// المقابل لـ: main.py class TrayPopup (السطور 2995-3180)
// تحويل سطر بسطر - كل ستايل وكل وظيفة مطابقة للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Input;
using Color = System.Windows.Media.Color;
using ColorConverter = System.Windows.Media.ColorConverter;
using SolidColorBrush = System.Windows.Media.SolidColorBrush;
using Application = System.Windows.Application;

namespace SmartKeyboard
{
    /// <summary>
    /// class TrayPopup(QWidget): - السطر 2995
    /// نافذة القائمة المنبثقة من System Tray
    /// </summary>
    public partial class TrayPopup : Window
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
        // المتغيرات - من __init__ السطور 2996-2999
        // ═══════════════════════════════════════════════════════════════

        // السطر 2998: self.win = win
        private readonly MainWindow _mainWindow;

        // ═══════════════════════════════════════════════════════════════
        // Events
        // ═══════════════════════════════════════════════════════════════
        public event Action? OnShowClicked;
        public event Action? OnExitClicked;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - __init__ السطور 2996-3071
        // ═══════════════════════════════════════════════════════════════
        public TrayPopup(MainWindow mainWindow)
        {
            InitializeComponent();

            _mainWindow = mainWindow;

            // Update title with version - السطر 3035
            TitleText.Text = $"Smart Keyboard v{Version.VERSION}";

            // Apply WS_EX_NOACTIVATE after window is created
            this.Loaded += (s, e) =>
            {
                IntPtr hwnd = new System.Windows.Interop.WindowInteropHelper(this).Handle;
                int style = GetWindowLong(hwnd, GWL_EXSTYLE);
                SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE);
            };
        }

        // ═══════════════════════════════════════════════════════════════
        // Hover Effects - من _create_button السطور 3105-3122
        // ═══════════════════════════════════════════════════════════════

        // Show button hover - السطور 3105-3108
        private void BtnShow_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e)
        {
            // السطر 3107
            ShowAr.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#fcb953"));
            ShowAr.FontWeight = FontWeights.SemiBold;
            // السطر 3108
            ShowEng.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#DCDCDC"));
        }

        // السطور 3110-3113
        private void BtnShow_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e)
        {
            // السطر 3112
            ShowAr.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#e6a84a"));
            ShowAr.FontWeight = FontWeights.Normal;
            // السطر 3113
            ShowEng.Foreground = new SolidColorBrush(Color.FromArgb(200, 180, 180, 180));
        }

        // Exit button hover - same pattern
        private void BtnExit_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e)
        {
            ExitAr.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#fcb953"));
            ExitAr.FontWeight = FontWeights.SemiBold;
            ExitEng.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#DCDCDC"));
        }

        private void BtnExit_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e)
        {
            ExitAr.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#e6a84a"));
            ExitAr.FontWeight = FontWeights.Normal;
            ExitEng.Foreground = new SolidColorBrush(Color.FromArgb(200, 180, 180, 180));
        }

        // ═══════════════════════════════════════════════════════════════
        // Click Handlers - من click السطور 3115-3118
        // ═══════════════════════════════════════════════════════════════

        // السطور 3157-3158: _on_show
        private void BtnShow_Click(object sender, MouseButtonEventArgs e)
        {
            this.Hide();
            OnShowClicked?.Invoke();
            _mainWindow?.Toggle();
        }

        // السطور 3160-3161: _on_exit
        private void BtnExit_Click(object sender, MouseButtonEventArgs e)
        {
            this.Hide();
            OnExitClicked?.Invoke();
            Application.Current.Shutdown();
        }

        // ═══════════════════════════════════════════════════════════════
        // Window_Deactivated - من _check_click السطور 3141-3155
        // إغلاق النافذة عند النقر خارجها
        // ═══════════════════════════════════════════════════════════════
        private void Window_Deactivated(object sender, EventArgs e)
        {
            // السطر 3155
            this.Hide();
        }

        // ═══════════════════════════════════════════════════════════════
        // show_at_cursor - السطور 3163-3180
        // إظهار النافذة في طرف الأيقونة (يمين وفوق)
        // ═══════════════════════════════════════════════════════════════
        public void ShowAtCursor()
        {
            // السطر 3165: cursor = QCursor.pos()
            var cursorPos = System.Windows.Forms.Cursor.Position;

            // السطر 3166: screen = QApplication.primaryScreen().geometry()
            var screen = System.Windows.SystemParameters.WorkArea;

            // السطور 3169-3170: الموقع: يمين وفوق المؤشر
            double x = cursorPos.X;
            double y = cursorPos.Y - this.Height;

            // السطور 3173-3174: منع الخروج من الشاشة - يمين
            if (x + this.Width > screen.Width)
            {
                x = cursorPos.X - this.Width;
            }

            // السطور 3175-3176: منع الخروج من الشاشة - أعلى
            if (y < 0)
            {
                y = cursorPos.Y;
            }

            // السطور 3178-3180
            this.Left = x;
            this.Top = y;
            this.Show();
            this.Activate();
        }
    }
}
