// ═══════════════════════════════════════════════════════════════════════════════
// CustomContextMenu.cs - القائمة المنبثقة (كليك يمين)
// المقابل لـ: main.py class MenuItemWidget (574-686) + CustomContextMenu (693-799)
// تحويل سطر بسطر - كل ستايل وكل تأثير مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using Window = System.Windows.Window;
using Color = System.Windows.Media.Color;
using Point = System.Windows.Point;
using Brushes = System.Windows.Media.Brushes;
using MouseEventArgs = System.Windows.Input.MouseEventArgs;
using ColorConverter = System.Windows.Media.ColorConverter;
using Cursors = System.Windows.Input.Cursors;
using Size = System.Windows.Size;
using FontFamily = System.Windows.Media.FontFamily;
using HorizontalAlignment = System.Windows.HorizontalAlignment;
using VerticalAlignment = System.Windows.VerticalAlignment;

namespace SmartKeyboard
{
    // ═══════════════════════════════════════════════════════════════
    // MenuItemWidget - السطور 574-686
    // عنصر واحد في القائمة المنبثقة مع hover effects
    // ═══════════════════════════════════════════════════════════════
    public class MenuItemWidget : Border
    {
        private readonly TextBlock _lblArabic;
        private readonly TextBlock _lblEnglish;
        private readonly Action? _callback;
        private readonly CustomContextMenu _menu;
        private readonly int _fontSize;

        // ألوان من السطور 601-606, 616-621
        private static readonly SolidColorBrush EnglishNormalColor = new SolidColorBrush(Color.FromArgb(200, 180, 180, 180));
        private static readonly SolidColorBrush EnglishHoverColor = new SolidColorBrush(Color.FromArgb(255, 220, 220, 220));
        private static readonly SolidColorBrush ArabicNormalColor = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#e6a84a"));
        private static readonly SolidColorBrush ArabicHoverColor = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#fcb953"));

        public MenuItemWidget(string arabic, string english, string shortcut, Action? callback, CustomContextMenu menu, int fontSize)
        {
            _callback = callback;
            _menu = menu;
            _fontSize = fontSize;

            // السطر 581: setCursor(PointingHandCursor)
            Cursor = Cursors.Hand;

            // السطور 588-589: margins and spacing
            Padding = new Thickness(15, 8, 15, 8);
            Background = Brushes.Transparent;
            CornerRadius = new CornerRadius(8);

            // Grid layout for left/right text
            var grid = new Grid();
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });

            // السطور 599-607: النص الإنجليزي + الاختصار (يسار)
            string engText = !string.IsNullOrEmpty(shortcut) ? $"{english} {shortcut}" : english;
            _lblEnglish = new TextBlock
            {
                Text = engText,
                Foreground = EnglishNormalColor,
                FontFamily = new FontFamily("Segoe UI"),
                FontSize = Math.Max(11, fontSize - 3),
                FontWeight = FontWeights.Normal,
                VerticalAlignment = VerticalAlignment.Center,
                HorizontalAlignment = HorizontalAlignment.Left
            };
            Grid.SetColumn(_lblEnglish, 0);
            grid.Children.Add(_lblEnglish);

            // السطور 615-622: النص العربي (يمين) - اللون الذهبي
            _lblArabic = new TextBlock
            {
                Text = arabic,
                Foreground = ArabicNormalColor,
                FontFamily = new FontFamily("Segoe UI"),
                FontSize = fontSize - 3,
                FontWeight = FontWeights.Normal,
                VerticalAlignment = VerticalAlignment.Center,
                HorizontalAlignment = HorizontalAlignment.Right
            };
            Grid.SetColumn(_lblArabic, 2);
            grid.Children.Add(_lblArabic);

            Child = grid;

            // Event handlers
            MouseLeftButtonUp += OnMouseLeftButtonUp;
            MouseEnter += OnMouseEnter;
            MouseLeave += OnMouseLeave;
        }

        // السطور 631-634: mouseReleaseEvent
        private void OnMouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            _menu.Close();
            _callback?.Invoke();
        }

        // السطور 636-664: enterEvent - تأثير Hover
        private void OnMouseEnter(object sender, MouseEventArgs e)
        {
            // السطور 645-650: تغيير لون النص العربي عند hover
            _lblArabic.Foreground = ArabicHoverColor;
            _lblArabic.FontWeight = FontWeights.SemiBold;

            // السطور 659-664: تغيير لون النص الإنجليزي عند Hover
            _lblEnglish.Foreground = EnglishHoverColor;
            _lblEnglish.FontWeight = FontWeights.SemiBold;
        }

        // السطور 666-686: leaveEvent - إعادة الألوان الأصلية
        private void OnMouseLeave(object sender, MouseEventArgs e)
        {
            // السطور 671-676: إعادة اللون الذهبي للنص العربي
            _lblArabic.Foreground = ArabicNormalColor;
            _lblArabic.FontWeight = FontWeights.Normal;

            // السطور 681-685: إعادة لون النص الإنجليزي الأصلي
            _lblEnglish.Foreground = EnglishNormalColor;
            _lblEnglish.FontWeight = FontWeights.Normal;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // CustomContextMenu - السطور 693-799
    // القائمة المنبثقة الكاملة مع WS_EX_NOACTIVATE
    // ═══════════════════════════════════════════════════════════════
    public class CustomContextMenu : Window
    {
        // P/Invoke for WS_EX_NOACTIVATE - السطور 763-768
        private const int GWL_EXSTYLE = -20;
        private const uint WS_EX_NOACTIVATE = 0x08000000;

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);

        [DllImport("user32.dll")]
        private static extern short GetAsyncKeyState(int vKey);

        [DllImport("user32.dll")]
        private static extern bool GetCursorPos(out POINT lpPoint);

        [StructLayout(LayoutKind.Sequential)]
        private struct POINT { public int X, Y; }

        private const int VK_LBUTTON = 0x01;
        private const int VK_RBUTTON = 0x02;

        private readonly StackPanel _itemsPanel;
        private readonly DispatcherTimer _clickTimer;
        private bool _ignoreInitialClick = true;
        private readonly int _fontSize;

        public CustomContextMenu()
        {
            // السطر 696: WindowFlags
            WindowStyle = WindowStyle.None;
            AllowsTransparency = true;
            Topmost = true;
            ShowInTaskbar = false;
            ShowActivated = false;
            ResizeMode = ResizeMode.NoResize;

            // السطور 700-702: Read Config
            _fontSize = CONFIG.Instance.FontSize;
            int bgOpacity = CONFIG.Instance.BgOpacity;

            // السطور 709-747: استايل القائمة المنبثقة
            // Gradient background matching Python lines 717-721
            byte alpha = (byte)bgOpacity;
            var bgBrush = new LinearGradientBrush
            {
                StartPoint = new Point(0, 0),
                EndPoint = new Point(0, 1)
            };
            bgBrush.GradientStops.Add(new GradientStop(Color.FromArgb(alpha, 30, 36, 54), 0));
            bgBrush.GradientStops.Add(new GradientStop(Color.FromArgb(alpha, 20, 26, 44), 1));

            var mainBorder = new Border
            {
                Background = bgBrush,
                BorderBrush = new SolidColorBrush(Color.FromArgb(77, 100, 150, 220)), // rgba(100,150,220,0.3)
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(12),
                Padding = new Thickness(5, 8, 5, 8)
            };

            _itemsPanel = new StackPanel();
            mainBorder.Child = _itemsPanel;
            Content = mainBorder;

            // السطور 752-755: Timer for global click detection
            _clickTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(100)
            };
            _clickTimer.Tick += CheckGlobalClick;

            // السطر 750: Apply WS_EX_NOACTIVATE
            SourceInitialized += (s, e) => ApplyNoActivate();
            Loaded += (s, e) => ApplyNoActivate();
        }

        // السطور 757-761: add_custom_action
        public void AddCustomAction(string arabic, string english, string shortcut, Action? callback)
        {
            var item = new MenuItemWidget(arabic, english, shortcut, callback, this, _fontSize);
            _itemsPanel.Children.Add(item);
        }

        // السطور 737-746: إضافة فاصل
        public void AddSeparator()
        {
            var separator = new Border
            {
                Height = 1,
                Margin = new Thickness(15, 6, 15, 6),
                Background = new LinearGradientBrush
                {
                    StartPoint = new Point(0, 0),
                    EndPoint = new Point(1, 0),
                    GradientStops =
                    {
                        new GradientStop(Colors.Transparent, 0),
                        new GradientStop(Color.FromArgb(102, 100, 150, 220), 0.5), // rgba(100,150,220,0.4)
                        new GradientStop(Colors.Transparent, 1)
                    }
                }
            };
            _itemsPanel.Children.Add(separator);
        }

        // السطور 763-768: apply_no_activate
        private void ApplyNoActivate()
        {
            try
            {
                var hwnd = new System.Windows.Interop.WindowInteropHelper(this).Handle;
                if (hwnd != IntPtr.Zero)
                {
                    uint style = GetWindowLong(hwnd, GWL_EXSTYLE);
                    SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[CONTEXT_MENU] Error applying WS_EX_NOACTIVATE: {ex.Message}");
            }
        }

        // السطور 770-774: showEvent
        public void ShowAt(double x, double y)
        {
            Left = x;
            Top = y;
            Show();

            ApplyNoActivate();
            _ignoreInitialClick = true;
            _clickTimer.Start();

            // Measure and adjust size
            Measure(new Size(double.PositiveInfinity, double.PositiveInfinity));
            Arrange(new Rect(DesiredSize));
        }

        // السطور 776-778: hideEvent
        protected override void OnClosed(EventArgs e)
        {
            _clickTimer.Stop();
            base.OnClosed(e);
        }

        // السطور 780-799: check_global_click
        private void CheckGlobalClick(object? sender, EventArgs e)
        {
            // Check Left or Right mouse button - السطور 782-783
            bool lDown = (GetAsyncKeyState(VK_LBUTTON) & 0x8000) != 0;
            bool rDown = (GetAsyncKeyState(VK_RBUTTON) & 0x8000) != 0;

            // السطور 785-790
            if (!lDown && !rDown)
            {
                _ignoreInitialClick = false;
                return;
            }

            if (_ignoreInitialClick)
                return;

            // السطور 793-799: Mouse is down, check if it's inside the menu
            GetCursorPos(out POINT pt);
            var rect = new Rect(Left, Top, ActualWidth, ActualHeight);

            if (!rect.Contains(new Point(pt.X, pt.Y)))
            {
                Close();
            }
        }
    }
}
