// ═══════════════════════════════════════════════════════════════════════════════
// FloatingButtonsWindow.cs - الأزرار العائمة فوق الشات
// المقابل لـ: main.py position_buttons (1842-1940), _show_buttons_with_timer (1944-1965),
//             _on_auto_hide_timer (1967-1972), _hide_buttons (1974-1986),
//             _lock_buttons (1988-1993), _unlock_buttons (1995-2001)
// تحويل سطر بسطر - كل ستايل وكل سلوك مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Window = System.Windows.Window;
using Button = System.Windows.Controls.Button;
using Point = System.Windows.Point;
using Image = System.Windows.Controls.Image;
using Color = System.Windows.Media.Color;
using Brushes = System.Windows.Media.Brushes;
using MouseEventArgs = System.Windows.Input.MouseEventArgs;
using Cursors = System.Windows.Input.Cursors;
using Size = System.Windows.Size;
using ColorConverter = System.Windows.Media.ColorConverter;
using Control = System.Windows.Controls.Control;
using HorizontalAlignment = System.Windows.HorizontalAlignment;
using VerticalAlignment = System.Windows.VerticalAlignment;

namespace SmartKeyboard
{
    // ═══════════════════════════════════════════════════════════════
    // FloatingButton - زر عائم واحد فوق الشات
    // مطابق لـ QPushButton مع WS_EX_NOACTIVATE
    // ═══════════════════════════════════════════════════════════════
    public class FloatingButton : Window
    {
        // P/Invoke for WS_EX_NOACTIVATE
        private const int GWL_EXSTYLE = -20;
        private const uint WS_EX_NOACTIVATE = 0x08000000;

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);

        private readonly Button _button;
        private readonly Image _iconImage;
        private string _normalIconPath = "";
        private string _hoverIconPath = "";
        private readonly int _iconSize;

        // Custom tooltip - السطور 1786-1840
        private CustomTooltip? _tooltip;
        private string _tooltipText = "";
        private string _tooltipColor = "gray";

        // Events
        public event EventHandler? ButtonClicked;
        public event EventHandler? HoverEnter;
        public event EventHandler? HoverLeave;

        // السطور 1848-1849
        private const int ICON_SIZE = 16;
        private const int BTN_SIZE = 32;

        public FloatingButton()
        {
            _iconSize = ICON_SIZE;

            // السطور 1862-1863: WindowFlags
            WindowStyle = WindowStyle.None;
            AllowsTransparency = true;
            Topmost = true;
            ShowInTaskbar = false;
            ShowActivated = false;
            ResizeMode = ResizeMode.NoResize;

            // السطر 1855: setFixedSize(32, 32)
            Width = BTN_SIZE;
            Height = BTN_SIZE;

            // السطر 1863: WA_TranslucentBackground
            Background = Brushes.Transparent;

            // Create button
            _iconImage = new Image
            {
                Width = _iconSize,
                Height = _iconSize,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center
            };

            _button = new Button
            {
                Content = _iconImage,
                Width = BTN_SIZE,
                Height = BTN_SIZE,
                Cursor = Cursors.Hand,
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0)
            };

            // السطور 1857-1860, 1878-1881: Styling
            _button.Style = CreateButtonStyle();

            _button.Click += (s, e) => ButtonClicked?.Invoke(this, EventArgs.Empty);
            _button.MouseEnter += OnButtonMouseEnter;
            _button.MouseLeave += OnButtonMouseLeave;

            Content = _button;

            // Apply WS_EX_NOACTIVATE - السطور 1922-1936
            SourceInitialized += (s, e) => ApplyNoActivate();
            Loaded += (s, e) => ApplyNoActivate();
        }

        private Style CreateButtonStyle()
        {
            var style = new Style(typeof(Button));
            
            var template = new ControlTemplate(typeof(Button));
            var border = new FrameworkElementFactory(typeof(Border));
            border.Name = "PART_Border";
            border.SetValue(Border.BackgroundProperty, Brushes.Transparent);
            border.SetValue(Border.CornerRadiusProperty, new CornerRadius(8));
            
            var contentPresenter = new FrameworkElementFactory(typeof(ContentPresenter));
            contentPresenter.SetValue(ContentPresenter.HorizontalAlignmentProperty, HorizontalAlignment.Center);
            contentPresenter.SetValue(ContentPresenter.VerticalAlignmentProperty, VerticalAlignment.Center);
            border.AppendChild(contentPresenter);
            
            template.VisualTree = border;
            
            // Hover trigger - السطور 1859, 1880, 1903
            var hoverTrigger = new Trigger
            {
                Property = UIElement.IsMouseOverProperty,
                Value = true
            };
            hoverTrigger.Setters.Add(new Setter(
                Border.BackgroundProperty,
                new SolidColorBrush(Color.FromArgb(15, 255, 255, 255)), // rgba(255,255,255,15)
                "PART_Border"));
            template.Triggers.Add(hoverTrigger);
            
            style.Setters.Add(new Setter(Control.TemplateProperty, template));
            return style;
        }

        // السطر 1861: setCursor(SizeAllCursor)
        public void SetSizeAllCursor()
        {
            _button.Cursor = Cursors.SizeAll;
            Cursor = Cursors.SizeAll;
        }

        // تحميل الأيقونات - السطور 1864-1868, 1882-1886
        public void SetIcons(string normalPath, string hoverPath)
        {
            _normalIconPath = normalPath;
            _hoverIconPath = hoverPath;
            LoadIcon(normalPath);
        }

        private void LoadIcon(string path)
        {
            try
            {
                if (File.Exists(path))
                {
                    var bitmap = new BitmapImage();
                    bitmap.BeginInit();
                    bitmap.UriSource = new Uri(path, UriKind.Absolute);
                    bitmap.DecodePixelWidth = _iconSize;
                    bitmap.DecodePixelHeight = _iconSize;
                    bitmap.EndInit();
                    _iconImage.Source = bitmap;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[BUTTON] Icon load error: {ex.Message}");
            }
        }

        // Tooltip setup - السطور 1746-1784
        public void SetupHoverEffect(string tooltipText, string tooltipColor)
        {
            _tooltipText = tooltipText;
            _tooltipColor = tooltipColor;
        }

        // السطور 1758-1769: on_enter
        private void OnButtonMouseEnter(object sender, MouseEventArgs e)
        {
            // Load hover icon
            if (!string.IsNullOrEmpty(_hoverIconPath))
            {
                LoadIcon(_hoverIconPath);
            }

            // Show custom tooltip - السطر 1768-1769
            if (!string.IsNullOrEmpty(_tooltipText))
            {
                ShowCustomTooltip();
            }

            HoverEnter?.Invoke(this, EventArgs.Empty);
        }

        // السطور 1771-1781: on_leave
        private void OnButtonMouseLeave(object sender, MouseEventArgs e)
        {
            // Restore normal icon
            if (!string.IsNullOrEmpty(_normalIconPath))
            {
                LoadIcon(_normalIconPath);
            }

            // Hide tooltip - السطر 1779
            HideCustomTooltip();

            HoverLeave?.Invoke(this, EventArgs.Empty);
        }

        // السطور 1786-1829: _show_custom_tooltip
        private void ShowCustomTooltip()
        {
            if (_tooltip == null)
            {
                _tooltip = new CustomTooltip();
            }

            _tooltip.SetContent(_tooltipText, _tooltipColor);

            // Position ABOVE button (centered) - السطور 1824-1828
            var btnPos = PointToScreen(new Point(Width / 2, 0));
            _tooltip.Left = btnPos.X - (_tooltip.Width / 2);
            _tooltip.Top = btnPos.Y - _tooltip.Height - 5;
            _tooltip.Show();
        }

        // السطور 1837-1840: _hide_custom_tooltip
        private void HideCustomTooltip()
        {
            _tooltip?.Hide();
        }

        // السطور 1922-1936: Apply WS_EX_NOACTIVATE
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
                Console.WriteLine($"[BUTTON] Error applying WS_EX_NOACTIVATE: {ex.Message}");
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // CustomTooltip - Tooltip مخصص بألوان متعددة
    // مطابق للسطور 1786-1840
    // ═══════════════════════════════════════════════════════════════
    public class CustomTooltip : Window
    {
        private readonly Border _border;
        private readonly TextBlock _label;

        // السطور 1798-1804: Colors
        private static readonly System.Collections.Generic.Dictionary<string, (string text, string border, Color bg)> Colors = new()
        {
            { "gray", ("#d4d8dc", "#4a5058", Color.FromArgb(89, 74, 80, 88)) },     // rgba(74,80,88,0.35)
            { "olive", ("#d4e8c0", "#4a5f35", Color.FromArgb(89, 74, 95, 53)) },    // rgba(74,95,53,0.35)
            { "blue", ("#c4daf8", "#2a5a9f", Color.FromArgb(89, 42, 90, 159)) },    // rgba(42,90,159,0.35)
            { "red", ("#f8c4c4", "#8f2a2a", Color.FromArgb(89, 143, 42, 42)) },     // rgba(143,42,42,0.35)
            { "green", ("#c4f8d4", "#2a8f4a", Color.FromArgb(89, 42, 143, 74)) }    // rgba(42,143,74,0.35)
        };

        public CustomTooltip()
        {
            WindowStyle = WindowStyle.None;
            AllowsTransparency = true;
            Topmost = true;
            ShowInTaskbar = false;
            ShowActivated = false;
            ResizeMode = ResizeMode.NoResize;
            Background = Brushes.Transparent;

            _label = new TextBlock
            {
                FontSize = 13,                       // السطر 1815
                Padding = new Thickness(14, 6, 14, 6), // السطر 1814
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center
            };

            _border = new Border
            {
                CornerRadius = new CornerRadius(14),  // السطر 1813
                BorderThickness = new Thickness(1),   // السطر 1812
                Child = _label
            };

            Content = _border;
            SizeToContent = SizeToContent.WidthAndHeight;
        }

        // السطور 1807-1822
        public void SetContent(string text, string colorKey)
        {
            var c = Colors.ContainsKey(colorKey) ? Colors[colorKey] : Colors["gray"];

            _label.Text = text;
            _label.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString(c.text));
            _border.Background = new SolidColorBrush(c.bg);
            _border.BorderBrush = new SolidColorBrush((Color)ColorConverter.ConvertFromString(c.border));

            // السطور 1820-1821: Update size
            Measure(new Size(double.PositiveInfinity, double.PositiveInfinity));
            Arrange(new Rect(DesiredSize));
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // FloatingButtonsManager - إدارة الأزرار الثلاثة مع Auto-Hide
    // مطابق للسطور 1842-2001
    // ═══════════════════════════════════════════════════════════════
    public class FloatingButtonsManager
    {
        private FloatingButton? _dragHandle;
        private FloatingButton? _btnSettings;
        private FloatingButton? _btnPin;

        private readonly MainWindow _mainWindow;
        private readonly string _iconsDir;

        private bool _buttonsVisible = false;        // السطر 1950
        private bool _buttonsLocked = false;         // السطر 1970
        private DispatcherTimer? _autoHideTimer;     // السطور 1960-1964

        public FloatingButtonsManager(MainWindow mainWindow)
        {
            _mainWindow = mainWindow;
            _iconsDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Icons");
        }

        // السطور 1842-1940: position_buttons
        public void PositionButtons()
        {
            // Create buttons if they don't exist - السطور 1852-1911
            CreateButtonsIfNeeded();

            // Update pin button style - السطر 1911
            UpdatePinButtonStyle();

            // Position buttons above the chat window - السطور 1913-1917
            double btnY = _mainWindow.Top - 32;  // Buttons touch the chat edge
            
            if (_dragHandle != null)
            {
                _dragHandle.Left = _mainWindow.Left + 2;
                _dragHandle.Top = btnY;
                _dragHandle.Show();
            }

            if (_btnSettings != null)
            {
                _btnSettings.Left = _mainWindow.Left + 34;
                _btnSettings.Top = btnY;
                _btnSettings.Show();
            }

            if (_btnPin != null)
            {
                _btnPin.Left = _mainWindow.Left + 66;
                _btnPin.Top = btnY;
                _btnPin.Show();
            }

            _buttonsVisible = true;

            // Hide buttons initially if auto-hide - السطور 1938-1942
        }

        // السطور 1852-1908: Create buttons
        private void CreateButtonsIfNeeded()
        {
            if (_dragHandle != null) return;

            // Drag Handle - السطور 1853-1872
            _dragHandle = new FloatingButton();
            _dragHandle.SetSizeAllCursor();
            string moveIcon = Path.Combine(_iconsDir, "move.png");
            string moveIconLight = Path.Combine(_iconsDir, "move_light.png");
            _dragHandle.SetIcons(moveIcon, moveIconLight);
            _dragHandle.SetupHoverEffect("تحريك", "olive");
            _dragHandle.HoverEnter += (s, e) => LockButtons();
            _dragHandle.HoverLeave += (s, e) => UnlockButtons();
            // Drag events will be connected externally

            // Settings Button - السطور 1874-1891
            _btnSettings = new FloatingButton();
            string settingsIcon = Path.Combine(_iconsDir, "settings.png");
            string settingsIconLight = Path.Combine(_iconsDir, "settings_light.png");
            _btnSettings.SetIcons(settingsIcon, settingsIconLight);
            _btnSettings.SetupHoverEffect("الإعدادات", "blue");
            _btnSettings.ButtonClicked += (s, e) => _mainWindow.ToggleSettings();
            _btnSettings.HoverEnter += (s, e) => LockButtons();
            _btnSettings.HoverLeave += (s, e) => UnlockButtons();

            // Pin Button - السطور 1893-1908
            _btnPin = new FloatingButton();
            // Initial icon set in UpdatePinButtonStyle
            _btnPin.ButtonClicked += (s, e) => TogglePinMode();
            _btnPin.HoverEnter += (s, e) => LockButtons();
            _btnPin.HoverLeave += (s, e) => UnlockButtons();
        }

        // السطور 2015-2023: toggle_pin_mode
        private void TogglePinMode()
        {
            bool current = CONFIG.Instance.PinnedMode;
            CONFIG.Instance.PinnedMode = !current;
            UpdatePinButtonStyle();
            Console.WriteLine(current ? "[PIN] معطّل - الوضع العادي" : "[PIN] مفعّل - الشات سيختفي لحظة عند الإرسال");
        }

        // السطور 2025-2051: update_pin_button_style
        private void UpdatePinButtonStyle()
        {
            if (_btnPin == null) return;

            string iconPath, iconPathLight, tooltipText, tooltipColor;

            if (CONFIG.Instance.PinnedMode)
            {
                iconPath = Path.Combine(_iconsDir, "pin_green.png");
                iconPathLight = Path.Combine(_iconsDir, "pin_green_light.png");
                tooltipText = "مثبت فوق الشات ✓";
                tooltipColor = "green";
            }
            else
            {
                iconPath = Path.Combine(_iconsDir, "pin_gray.png");
                iconPathLight = Path.Combine(_iconsDir, "pin_gray_light.png");
                tooltipText = "غير مثبت فوق الشات ✗";
                tooltipColor = "red";
            }

            _btnPin.SetIcons(iconPath, iconPathLight);
            _btnPin.SetupHoverEffect(tooltipText, tooltipColor);
        }

        // السطور 1944-1965: _show_buttons_with_timer
        public void ShowButtonsWithTimer()
        {
            PositionButtons();

            // Start auto-hide timer (5 seconds) - السطور 1959-1965
            if (_autoHideTimer == null)
            {
                _autoHideTimer = new DispatcherTimer
                {
                    Interval = TimeSpan.FromMilliseconds(5000)
                };
                _autoHideTimer.Tick += (s, e) =>
                {
                    _autoHideTimer.Stop();
                    OnAutoHideTimer();
                };
            }
            _autoHideTimer.Stop();
            _autoHideTimer.Start();
        }

        // السطور 1967-1972: _on_auto_hide_timer
        private void OnAutoHideTimer()
        {
            if (_buttonsLocked)
                return;
            HideButtons();
        }

        // السطور 1974-1986: _hide_buttons
        public void HideButtons()
        {
            if (!_buttonsVisible)
                return;

            _buttonsVisible = false;

            _dragHandle?.Hide();
            _btnSettings?.Hide();
            _btnPin?.Hide();
        }

        // السطور 1988-1993: _lock_buttons
        public void LockButtons()
        {
            _buttonsLocked = true;
            _autoHideTimer?.Stop();
        }

        // السطور 1995-2001: _unlock_buttons
        public void UnlockButtons()
        {
            _buttonsLocked = false;
            if (_buttonsVisible)
            {
                _autoHideTimer?.Start();
            }
        }

        // Get drag handle for external drag handling
        public FloatingButton? DragHandle => _dragHandle;
    }
}
