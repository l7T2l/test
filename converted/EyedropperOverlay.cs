// ═══════════════════════════════════════════════════════════════════════════════
// EyedropperOverlay.xaml.cs - أداة المصاصة لالتقاط الألوان
// المقابل لـ: Styles/chat_page.py class EyedropperOverlay (السطور 1-120)
// تحويل سطر بسطر - كل وظيفة وكل ستايل مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Color = System.Windows.Media.Color;
using Point = System.Windows.Point;
using Window = System.Windows.Window;

namespace SmartKeyboard.Styles
{
    /// <summary>
    /// class EyedropperOverlay(QWidget): - السطر 28
    /// طبقة شفافة تغطي الشاشة بالكامل لالتقاط لون بكسل معين
    /// </summary>
    public class EyedropperOverlay : Window
    {
        // ═══════════════════════════════════════════════════════════════
        // P/Invoke for WS_EX_NOACTIVATE - السطور 43-54
        // ═══════════════════════════════════════════════════════════════
        private const int GWL_EXSTYLE = -20;
        private const uint WS_EX_NOACTIVATE = 0x08000000;
        private const uint WS_EX_TOPMOST = 0x00000008;
        private const uint WS_EX_TOOLWINDOW = 0x00000080;

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);

        [DllImport("user32.dll")]
        private static extern bool GetCursorPos(out POINT lpPoint);

        [StructLayout(LayoutKind.Sequential)]
        private struct POINT
        {
            public int X;
            public int Y;
        }

        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - السطور 32-42
        // ═══════════════════════════════════════════════════════════════
        private Bitmap? _screenCapture;           // صورة الشاشة الملتقطة
        private Color _currentColor;              // اللون الحالي تحت الماوس
        private int _currentX, _currentY;         // موضع الماوس الحالي
        private DispatcherTimer _updateTimer;     // مؤقت تحديث المعاينة

        // Preview UI elements
        private Canvas _canvas;
        private System.Windows.Controls.Image _previewImage;
        private Border _previewBorder;
        private Border _colorBox;
        private TextBlock _hexText;
        private Border _hexBackground;

        // ═══════════════════════════════════════════════════════════════
        // Events
        // ═══════════════════════════════════════════════════════════════
        public event Action<Color, int, int>? ColorPicked;
        public event Action? Cancelled;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - السطور 28-42
        // ═══════════════════════════════════════════════════════════════
        public EyedropperOverlay()
        {
            // إعدادات النافذة - السطور 36-42
            WindowStyle = WindowStyle.None;
            AllowsTransparency = true;
            Background = System.Windows.Media.Brushes.Transparent;
            Topmost = true;
            ShowInTaskbar = false;
            
            // تغطية كل الشاشة
            Left = SystemParameters.VirtualScreenLeft;
            Top = SystemParameters.VirtualScreenTop;
            Width = SystemParameters.VirtualScreenWidth;
            Height = SystemParameters.VirtualScreenHeight;

            // Canvas للرسم
            _canvas = new Canvas();
            Content = _canvas;

            // إنشاء عناصر المعاينة
            CreatePreviewElements();

            // التقاط صورة الشاشة - السطر 62
            CaptureScreen();

            // مؤقت التحديث - السطر 70 (30ms interval)
            _updateTimer = new DispatcherTimer();
            _updateTimer.Interval = TimeSpan.FromMilliseconds(30);
            _updateTimer.Tick += UpdateTimer_Tick;
            _updateTimer.Start();

            // ربط الأحداث
            MouseLeftButtonDown += OnMouseLeftButtonDown;
            MouseRightButtonDown += OnMouseRightButtonDown;
            KeyDown += OnKeyDown;

            // تطبيق WS_EX_NOACTIVATE
            SourceInitialized += (s, e) => ApplyNoActivate();
            
            // تعيين المؤشر
            Cursor = System.Windows.Input.Cursors.Cross;
        }

        // ═══════════════════════════════════════════════════════════════
        // Create preview elements - السطور 100-140
        // ═══════════════════════════════════════════════════════════════
        private void CreatePreviewElements()
        {
            // خلفية شبه شفافة للشاشة (optional - for screenshot display)
            _previewImage = new System.Windows.Controls.Image();
            _previewImage.Stretch = Stretch.None;
            Canvas.SetLeft(_previewImage, 0);
            Canvas.SetTop(_previewImage, 0);
            _canvas.Children.Add(_previewImage);

            // مربع المعاينة الرئيسي - 80x80
            _previewBorder = new Border
            {
                Width = 100,
                Height = 100,
                CornerRadius = new CornerRadius(8),
                BorderBrush = new SolidColorBrush(Colors.White),
                BorderThickness = new Thickness(2),
                Background = new SolidColorBrush(Color.FromArgb(150, 0, 0, 0))
            };

            // مربع اللون الفعلي 80x50
            _colorBox = new Border
            {
                Width = 80,
                Height = 50,
                CornerRadius = new CornerRadius(4),
                BorderBrush = new SolidColorBrush(Colors.White),
                BorderThickness = new Thickness(1),
                Background = new SolidColorBrush(Colors.Black),
                Margin = new Thickness(10, 10, 10, 0),
                VerticalAlignment = VerticalAlignment.Top
            };

            // خلفية نص HEX
            _hexBackground = new Border
            {
                Width = 80,
                Height = 25,
                CornerRadius = new CornerRadius(4),
                Background = new SolidColorBrush(Color.FromArgb(200, 0, 0, 0)),
                Margin = new Thickness(10, 65, 10, 5),
                VerticalAlignment = VerticalAlignment.Top
            };

            // نص HEX
            _hexText = new TextBlock
            {
                Text = "#000000",
                Foreground = new SolidColorBrush(Colors.White),
                FontFamily = new System.Windows.Media.FontFamily("Consolas"),
                FontSize = 12,
                FontWeight = FontWeights.Bold,
                HorizontalAlignment = System.Windows.HorizontalAlignment.Center,
                VerticalAlignment = System.Windows.VerticalAlignment.Center
            };
            _hexBackground.Child = _hexText;

            // ترتيب العناصر داخل مربع المعاينة
            var previewStack = new StackPanel();
            previewStack.Children.Add(_colorBox);
            previewStack.Children.Add(_hexBackground);
            _previewBorder.Child = previewStack;

            _canvas.Children.Add(_previewBorder);

            // إخفاء المعاينة مبدئياً
            _previewBorder.Visibility = Visibility.Hidden;
        }

        // ═══════════════════════════════════════════════════════════════
        // التقاط صورة الشاشة - السطور 62-68
        // ═══════════════════════════════════════════════════════════════
        private void CaptureScreen()
        {
            try
            {
                int width = (int)SystemParameters.VirtualScreenWidth;
                int height = (int)SystemParameters.VirtualScreenHeight;
                int left = (int)SystemParameters.VirtualScreenLeft;
                int top = (int)SystemParameters.VirtualScreenTop;

                _screenCapture = new Bitmap(width, height);
                using (var g = Graphics.FromImage(_screenCapture))
                {
                    g.CopyFromScreen(left, top, 0, 0, new System.Drawing.Size(width, height));
                }

                // عرض الصورة كخلفية (semi-transparent)
                var hBitmap = _screenCapture.GetHbitmap();
                try
                {
                    var source = Imaging.CreateBitmapSourceFromHBitmap(
                        hBitmap,
                        IntPtr.Zero,
                        Int32Rect.Empty,
                        BitmapSizeOptions.FromEmptyOptions());
                    _previewImage.Source = source;
                    _previewImage.Opacity = 0.3; // شفافية خفيفة لإظهار أن هذا وضع التقاط
                }
                finally
                {
                    DeleteObject(hBitmap);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[EYEDROPPER] Screen capture error: {ex.Message}");
            }
        }

        [DllImport("gdi32.dll")]
        private static extern bool DeleteObject(IntPtr hObject);

        // ═══════════════════════════════════════════════════════════════
        // تحديث المعاينة - السطور 70-98
        // ═══════════════════════════════════════════════════════════════
        private void UpdateTimer_Tick(object? sender, EventArgs e)
        {
            if (_screenCapture == null) return;

            // الحصول على موضع الماوس
            GetCursorPos(out POINT pt);
            _currentX = pt.X;
            _currentY = pt.Y;

            // تحويل إحداثيات الشاشة إلى إحداثيات الصورة
            int imgX = _currentX - (int)SystemParameters.VirtualScreenLeft;
            int imgY = _currentY - (int)SystemParameters.VirtualScreenTop;

            // التأكد من أن الإحداثيات داخل حدود الصورة
            if (imgX >= 0 && imgX < _screenCapture.Width &&
                imgY >= 0 && imgY < _screenCapture.Height)
            {
                // قراءة لون البكسل
                var pixel = _screenCapture.GetPixel(imgX, imgY);
                _currentColor = Color.FromRgb(pixel.R, pixel.G, pixel.B);

                // تحديث مربع اللون
                _colorBox.Background = new SolidColorBrush(_currentColor);

                // تحديث نص HEX
                _hexText.Text = $"#{pixel.R:X2}{pixel.G:X2}{pixel.B:X2}";

                // تحديث موقع مربع المعاينة
                UpdatePreviewPosition();

                // إظهار المعاينة
                _previewBorder.Visibility = Visibility.Visible;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // تحديث موقع مربع المعاينة - السطور 140-160
        // ═══════════════════════════════════════════════════════════════
        private void UpdatePreviewPosition()
        {
            double previewWidth = 100;
            double previewHeight = 100;
            double offset = 20; // المسافة من المؤشر

            double screenWidth = SystemParameters.VirtualScreenWidth;
            double screenHeight = SystemParameters.VirtualScreenHeight;
            double screenLeft = SystemParameters.VirtualScreenLeft;
            double screenTop = SystemParameters.VirtualScreenTop;

            // حساب الموقع الافتراضي (يمين وأسفل المؤشر)
            double previewX = _currentX - screenLeft + offset;
            double previewY = _currentY - screenTop + offset;

            // انعكاس الموقع إذا اقترب من الحافة اليمنى
            if (previewX + previewWidth > screenWidth - screenLeft)
            {
                previewX = _currentX - screenLeft - previewWidth - offset;
            }

            // انعكاس الموقع إذا اقترب من الحافة السفلى
            if (previewY + previewHeight > screenHeight - screenTop)
            {
                previewY = _currentY - screenTop - previewHeight - offset;
            }

            Canvas.SetLeft(_previewBorder, previewX);
            Canvas.SetTop(_previewBorder, previewY);
        }

        // ═══════════════════════════════════════════════════════════════
        // تطبيق WS_EX_NOACTIVATE - السطور 43-54
        // ═══════════════════════════════════════════════════════════════
        private void ApplyNoActivate()
        {
            try
            {
                var hwnd = new WindowInteropHelper(this).Handle;
                uint style = GetWindowLong(hwnd, GWL_EXSTYLE);
                SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOPMOST | WS_EX_TOOLWINDOW);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[EYEDROPPER] Error applying WS_EX_NOACTIVATE: {ex.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // معالجة النقر الأيسر - السطور 170-180
        // ═══════════════════════════════════════════════════════════════
        private void OnMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            _updateTimer.Stop();
            ColorPicked?.Invoke(_currentColor, _currentX, _currentY);
            CleanupAndClose();
        }

        // ═══════════════════════════════════════════════════════════════
        // معالجة النقر الأيمن - السطور 182-188
        // ═══════════════════════════════════════════════════════════════
        private void OnMouseRightButtonDown(object sender, MouseButtonEventArgs e)
        {
            _updateTimer.Stop();
            Cancelled?.Invoke();
            CleanupAndClose();
        }

        // ═══════════════════════════════════════════════════════════════
        // معالجة لوحة المفاتيح - السطور 190-198
        // ═══════════════════════════════════════════════════════════════
        private void OnKeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == Key.Escape)
            {
                _updateTimer.Stop();
                Cancelled?.Invoke();
                CleanupAndClose();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // التنظيف والإغلاق
        // ═══════════════════════════════════════════════════════════════
        private void CleanupAndClose()
        {
            _screenCapture?.Dispose();
            _screenCapture = null;
            Close();
        }

        // ═══════════════════════════════════════════════════════════════
        // Dispose override
        // ═══════════════════════════════════════════════════════════════
        protected override void OnClosed(EventArgs e)
        {
            _updateTimer?.Stop();
            _screenCapture?.Dispose();
            base.OnClosed(e);
        }
    }
}
