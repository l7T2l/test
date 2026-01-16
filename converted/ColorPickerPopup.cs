// ═══════════════════════════════════════════════════════════════════════════════
// ColorPickerPopup.cs - Color Picker المخصص (48 لون)
// المقابل لـ: Styles/settings_page.py pick_color() (السطور 582-765)
// تحويل سطر بسطر - كل وظيفة وكل ستايل مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Threading;
using Color = System.Windows.Media.Color;
using Window = System.Windows.Window;
using Brushes = System.Windows.Media.Brushes;
using Button = System.Windows.Controls.Button;
using ColorConverter = System.Windows.Media.ColorConverter;
using Point = System.Windows.Point;

namespace SmartKeyboard.Styles
{
    /// <summary>
    /// Color Picker مخصص - شبكة 48 لون (6×8) كما في الأصل
    /// السطور 582-765 من settings_page.py
    /// </summary>
    public class ColorPickerPopup : Window
    {
        // ═══════════════════════════════════════════════════════════════
        // P/Invoke for WS_EX_NOACTIVATE - السطور 758-764
        // ═══════════════════════════════════════════════════════════════
        private const int GWL_EXSTYLE = -20;
        private const uint WS_EX_NOACTIVATE = 0x08000000;

        [DllImport("user32.dll")]
        private static extern uint GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll")]
        private static extern uint SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);

        [DllImport("user32.dll")]
        private static extern short GetAsyncKeyState(int vKey);

        private const int VK_LBUTTON = 0x01;

        // ═══════════════════════════════════════════════════════════════
        // المتغيرات
        // ═══════════════════════════════════════════════════════════════
        private DispatcherTimer _outsideClickTimer;

        // ═══════════════════════════════════════════════════════════════
        // Events
        // ═══════════════════════════════════════════════════════════════
        public event Action<string>? ColorSelected;

        // ═══════════════════════════════════════════════════════════════
        // شبكة 48 لون (6 صفوف × 8 أعمدة) - السطور 713-727
        // ═══════════════════════════════════════════════════════════════
        private static readonly string[] BasicColors = new string[]
        {
            // Row 1: Reds/Pinks - السطر 716
            "#FF8080", "#FF0000", "#803333", "#FF0066", "#FF00FF", "#FF80FF", "#CC00CC", "#800080",
            // Row 2: Oranges/Yellows - السطر 718
            "#FFCC80", "#FF8000", "#804000", "#FF6600", "#FFFF00", "#FFFF80", "#CCCC00", "#808000",
            // Row 3: Greens - السطر 720
            "#80FF80", "#00FF00", "#008000", "#00FF66", "#00FFCC", "#80FFCC", "#00CC66", "#006633",
            // Row 4: Cyans/Blues - السطر 722
            "#80FFFF", "#00FFFF", "#008080", "#0066FF", "#0000FF", "#8080FF", "#0000CC", "#000080",
            // Row 5: Purples/Magentas - السطر 724
            "#CC80FF", "#9900FF", "#660099", "#CC00FF", "#FF00CC", "#FF80CC", "#990066", "#660033",
            // Row 6: Grays/Black/White - السطر 726
            "#FFFFFF", "#E0E0E0", "#C0C0C0", "#A0A0A0", "#808080", "#606060", "#404040", "#000000",
        };

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - السطور 594-602
        // ═══════════════════════════════════════════════════════════════
        public ColorPickerPopup()
        {
            // إعدادات النافذة - السطور 596-602
            WindowStyle = WindowStyle.None;
            AllowsTransparency = true;
            Background = Brushes.Transparent;
            Topmost = true;
            ShowInTaskbar = false;
            ResizeMode = ResizeMode.NoResize;

            // الحجم الثابت - السطر 749
            Width = 150;
            Height = 125;

            // إنشاء المحتوى
            CreateUI();

            // تطبيق WS_EX_NOACTIVATE - السطور 758-764
            SourceInitialized += (s, e) => ApplyNoActivate();

            // مؤقت فحص النقر خارج الـ picker - السطور 620-622
            _outsideClickTimer = new DispatcherTimer();
            _outsideClickTimer.Interval = TimeSpan.FromMilliseconds(100);
            _outsideClickTimer.Tick += OutsideClickTimer_Tick;
            _outsideClickTimer.Start();
        }

        // ═══════════════════════════════════════════════════════════════
        // إنشاء واجهة المستخدم - السطور 624-746
        // ═══════════════════════════════════════════════════════════════
        private void CreateUI()
        {
            // الحاوية الرئيسية - السطور 625-633
            Border container = new Border
            {
                Background = new SolidColorBrush(Color.FromRgb(30, 30, 30)),
                CornerRadius = new CornerRadius(8),
                BorderBrush = new SolidColorBrush(Color.FromRgb(136, 136, 136)),
                BorderThickness = new Thickness(2),
                Padding = new Thickness(8)
            };

            // الشبكة - السطور 729-730
            UniformGrid grid = new UniformGrid
            {
                Columns = 8,  // 8 أعمدة
                Rows = 6      // 6 صفوف
            };

            // إنشاء أزرار الألوان - السطور 732-744
            for (int i = 0; i < BasicColors.Length; i++)
            {
                string colorHex = BasicColors[i];
                Color color = (Color)ColorConverter.ConvertFromString(colorHex);

                Button btn = new Button
                {
                    Width = 15,   // السطر 734: setFixedSize(15, 15)
                    Height = 15,
                    Margin = new Thickness(1),
                    Cursor = System.Windows.Input.Cursors.Hand,
                    Tag = colorHex
                };

                // ستايل الزر - السطور 735-741
                btn.Template = CreateColorButtonTemplate(color);

                // ربط حدث النقر - السطر 743
                btn.Click += ColorButton_Click;

                grid.Children.Add(btn);
            }

            container.Child = grid;
            Content = container;
        }

        // ═══════════════════════════════════════════════════════════════
        // إنشاء قالب زر اللون - السطور 735-741
        // ═══════════════════════════════════════════════════════════════
        private ControlTemplate CreateColorButtonTemplate(Color color)
        {
            ControlTemplate template = new ControlTemplate(typeof(Button));

            // Border للزر
            FrameworkElementFactory borderFactory = new FrameworkElementFactory(typeof(Border));
            borderFactory.Name = "border";
            borderFactory.SetValue(Border.BackgroundProperty, new SolidColorBrush(color));
            borderFactory.SetValue(Border.BorderBrushProperty, new SolidColorBrush(Color.FromArgb(100, 60, 60, 60)));
            borderFactory.SetValue(Border.BorderThicknessProperty, new Thickness(1));

            template.VisualTree = borderFactory;

            // Trigger للـ hover - السطر 740: QPushButton:hover { border: 1px solid white; }
            Trigger hoverTrigger = new Trigger
            {
                Property = Button.IsMouseOverProperty,
                Value = true
            };
            hoverTrigger.Setters.Add(new Setter(Border.BorderBrushProperty, new SolidColorBrush(Colors.White), "border"));

            template.Triggers.Add(hoverTrigger);

            return template;
        }

        // ═══════════════════════════════════════════════════════════════
        // معالجة النقر على زر اللون - السطر 743
        // ═══════════════════════════════════════════════════════════════
        private void ColorButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button btn && btn.Tag is string colorHex)
            {
                _outsideClickTimer?.Stop();
                ColorSelected?.Invoke(colorHex);
                Close();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // فحص النقر خارج الـ picker - السطور 609-622
        // ═══════════════════════════════════════════════════════════════
        private void OutsideClickTimer_Tick(object? sender, EventArgs e)
        {
            // فحص إذا تم الضغط على زر الماوس الأيسر - السطر 613
            if ((GetAsyncKeyState(VK_LBUTTON) & 0x8000) != 0)
            {
                // الحصول على موقع الماوس
                var cursorPos = System.Windows.Forms.Cursor.Position;

                // فحص إذا كان الماوس خارج النافذة - السطر 616
                if (!IsMouseInsideWindow(cursorPos.X, cursorPos.Y))
                {
                    _outsideClickTimer?.Stop();
                    Close();
                }
            }
        }

        private bool IsMouseInsideWindow(int screenX, int screenY)
        {
            // تحويل إحداثيات الشاشة إلى إحداثيات النافذة
            return screenX >= Left && screenX <= Left + Width &&
                   screenY >= Top && screenY <= Top + Height;
        }

        // ═══════════════════════════════════════════════════════════════
        // تطبيق WS_EX_NOACTIVATE - السطور 758-764
        // ═══════════════════════════════════════════════════════════════
        private void ApplyNoActivate()
        {
            try
            {
                var hwnd = new WindowInteropHelper(this).Handle;
                uint style = GetWindowLong(hwnd, GWL_EXSTYLE);
                SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[COLOR_PICKER] Error applying WS_EX_NOACTIVATE: {ex.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // إظهار الـ picker فوق الزر - السطور 751-755
        // ═══════════════════════════════════════════════════════════════
        public void ShowAboveButton(FrameworkElement targetButton)
        {
            // الحصول على موقع الزر على الشاشة - السطر 752
            var btnPos = targetButton.PointToScreen(new Point(0, 0));

            // وسط فوق الزر - السطر 754
            Left = btnPos.X + (targetButton.ActualWidth / 2) - (Width / 2);
            Top = btnPos.Y - Height - 5;

            Show();
        }

        // ═══════════════════════════════════════════════════════════════
        // Cleanup
        // ═══════════════════════════════════════════════════════════════
        protected override void OnClosed(EventArgs e)
        {
            _outsideClickTimer?.Stop();
            base.OnClosed(e);
        }
    }
}
