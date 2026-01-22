// ═══════════════════════════════════════════════════════════════════════════════
// MainWindow.xaml.cs - النافذة الرئيسية
// المقابل لـ: main.py class OverlayWindow (السطور 1057-2000+)
// تحويل سطر بسطر - كل وظيفة مطابقة للأصل
// ═══════════════════════════════════════════════════════════════════════════════
// Part 1: Initialization, Apply Settings, Toggle, Timers
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Threading;
using Color = System.Windows.Media.Color;
using ColorConverter = System.Windows.Media.ColorConverter;
using Clipboard = System.Windows.Clipboard;
using SolidColorBrush = System.Windows.Media.SolidColorBrush;

namespace SmartKeyboard
{
    /// <summary>
    /// class OverlayWindow(QMainWindow): - السطر 1057
    /// النافذة الرئيسية للبرنامج
    /// </summary>
    public partial class MainWindow : Window
    {
        // ═══════════════════════════════════════════════════════════════
        // P/Invoke declarations
        // ═══════════════════════════════════════════════════════════════
        [DllImport("user32.dll")]
        private static extern int GetWindowLong(IntPtr hWnd, int nIndex);
        
        [DllImport("user32.dll")]
        private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
        
        [DllImport("user32.dll")]
        private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
        
        [DllImport("user32.dll")]
        private static extern IntPtr GetForegroundWindow();
        
        [DllImport("user32.dll")]
        private static extern short GetAsyncKeyState(int vKey);
        
        [DllImport("user32.dll")]
        private static extern short GetKeyState(int nVirtKey);

        // Window style constants
        private const int GWL_EXSTYLE = -20;
        private const int WS_EX_NOACTIVATE = 0x08000000;
        private const int WS_EX_TOPMOST = 0x00000008;
        private const int WS_EX_TRANSPARENT = 0x00000020;
        private const int WS_EX_LAYERED = 0x00080000;
        
        // SetWindowPos constants
        private static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
        private const uint SWP_NOMOVE = 0x0002;
        private const uint SWP_NOSIZE = 0x0001;
        private const uint SWP_NOACTIVATE = 0x0010;
        private const uint SWP_SHOWWINDOW = 0x0040;
        private const uint SWP_FRAMECHANGED = 0x0020;

        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - من __init__ السطور 1064-1190
        // ═══════════════════════════════════════════════════════════════

        // السطر 1066: self.processor = ArabicProcessor()
        private readonly ArabicProcessor _processor = new ArabicProcessor();

        // السطر 1067: self.is_arabic_mode = True
        private bool _isArabicMode = true;

        // السطر 1068: self.last_toggle_time = 0
        private double _lastToggleTime = 0;

        // السطر 1069: self._buttons_visible = False
        private bool _buttonsVisible = false;

        // السطر 1070: self._buttons_locked = False
        private bool _buttonsLocked = false;

        // السطر 1071: self._internal_clipboard = ""
        private string _internalClipboard = "";

        // السطر 1072: self._last_sent_message = ""
        private string _lastSentMessage = "";

        // السطر 1136: self.loc_mode = False
        private bool _locMode = false;

        // السطور 1146-1149: Resize/Drag State
        private string? _resizeMode = null;
        private System.Windows.Point? _dragPos = null;
        private System.Windows.Point? _resizeStartPos = null;
        private System.Windows.Rect? _resizeStartGeo = null;

        // السطر 1160: self._last_foreground = 0
        private IntPtr _lastForeground = IntPtr.Zero;

        // السطور 1167-1174: INPUT STATE MACHINE
        private string _inputState = "IDLE";  // السطر 1169
        private System.Collections.Generic.List<string> _keystrokeBuffer = new();  // السطر 1170
        private bool _clickThroughEnabled = false;  // السطر 1171
        private bool _autoToggleFlag = false;  // السطر 1174

        // السطر 1189: self._mouse_clicked_since_send = True
        private bool _mouseClickedSinceSend = true;

        // السطر 1201-1203: Target game tracking
        private IntPtr _targetGameHwnd = IntPtr.Zero;
        private bool _wasOnTargetGame = true;

        // ═══════════════════════════════════════════════════════════════
        // Timers - من __init__
        // ═══════════════════════════════════════════════════════════════

        // السطر 1152: self._topmost_timer
        private DispatcherTimer? _topmostTimer;

        // السطر 1157: self._fullscreen_check_timer
        private DispatcherTimer? _fullscreenCheckTimer;

        // السطر 1177: self._hook_health_timer
        private DispatcherTimer? _hookHealthTimer;

        // السطر 1182: self._ready_timer
        private DispatcherTimer? _readyTimer;

        // السطر 1194: self._mouse_tracker_timer
        private DispatcherTimer? _mouseTrackerTimer;

        // السطر 1284: self._ctrl_v_timer
        private DispatcherTimer? _ctrlVTimer;

        // MediaFilter reference
        private MediaFilter? _mediaFilter;

        // السطر 2548: self.settings_dlg - نافذة الإعدادات
        private Styles.SettingsWindow? _settingsWindow;

        // ═══════════════════════════════════════════════════════════════
        // Floating Buttons Manager - السطور 1842-2001
        // إدارة أزرار السحب والإعدادات والتثبيت مع auto-hide 5 ثواني
        // ═══════════════════════════════════════════════════════════════
        private FloatingButtonsManager? _buttonsManager;

        // ═══════════════════════════════════════════════════════════════
        // Window Resize Helper - السطور 1638-1744
        // تغيير حجم النافذة من 8 اتجاهات
        // ═══════════════════════════════════════════════════════════════
        private WindowResizeHelper? _resizeHelper;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - __init__ السطور 1064-1190
        // ═══════════════════════════════════════════════════════════════
        public MainWindow()
        {
            InitializeComponent();

            // Load position from config - السطر 1084
            this.Left = CONFIG.Instance.X;
            this.Top = CONFIG.Instance.Y;
            this.Width = CONFIG.Instance.W;
            this.Height = CONFIG.Instance.H;

            // Event handlers
            this.Loaded += Window_Loaded;
            this.MouseEnter += Window_MouseEnter;
            this.MouseLeave += Window_MouseLeave;
            this.MouseLeftButtonDown += Window_MouseLeftButtonDown;
            this.MouseMove += Window_MouseMove;
            this.MouseLeftButtonUp += Window_MouseLeftButtonUp;
        }

        // ═══════════════════════════════════════════════════════════════
        // Window_Loaded - يُنفذ بعد تحميل النافذة
        // من showEvent السطور 1587-1613
        // ═══════════════════════════════════════════════════════════════
        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            // Apply window styles - السطور 1596-1602
            IntPtr hwnd = new System.Windows.Interop.WindowInteropHelper(this).Handle;
            int currentStyle = GetWindowLong(hwnd, GWL_EXSTYLE);
            SetWindowLong(hwnd, GWL_EXSTYLE, currentStyle | WS_EX_NOACTIVATE | WS_EX_TOPMOST);

            // Force TOPMOST - السطور 1604-1610
            SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW);

            // Apply settings - السطر 1133
            ApplySettings();

            // Initialize timers - السطور 1152-1190
            InitializeTimers();

            // Start keyboard hooks - السطر 1137
            ReloadHotkey();

            // ═══════════════════════════════════════════════════════════════
            // Initialize FloatingButtonsManager - السطور 1842-2001
            // ═══════════════════════════════════════════════════════════════
            _buttonsManager = new FloatingButtonsManager(this);
            
            // ═══════════════════════════════════════════════════════════════
            // Initialize WindowResizeHelper - السطور 1638-1744
            // ═══════════════════════════════════════════════════════════════
            _resizeHelper = new WindowResizeHelper(
                this, 
                () => _buttonsManager?.LockButtons(),    // onResizeStart: lock buttons
                () => _buttonsManager?.UnlockButtons()   // onResizeEnd: unlock buttons
            );

            // ═══════════════════════════════════════════════════════════════
            // Register Alt+Shift language hotkey - السطر 1141
            // ═══════════════════════════════════════════════════════════════
            RegisterLanguageHotkey();

            // Set input state
            _inputState = "READY";
        }

        // ═══════════════════════════════════════════════════════════════
        // InitializeTimers - من __init__
        // ═══════════════════════════════════════════════════════════════
        private void InitializeTimers()
        {
            // السطور 1152-1154: _topmost_timer - 100ms
            _topmostTimer = new DispatcherTimer();
            _topmostTimer.Interval = TimeSpan.FromMilliseconds(100);
            _topmostTimer.Tick += (s, e) => EnsureTopmost();
            _topmostTimer.Start();

            // السطور 1157-1159: _fullscreen_check_timer - 500ms
            _fullscreenCheckTimer = new DispatcherTimer();
            _fullscreenCheckTimer.Interval = TimeSpan.FromMilliseconds(500);
            _fullscreenCheckTimer.Tick += (s, e) => CheckFullscreenToggle();
            _fullscreenCheckTimer.Start();

            // السطور 1177-1179: _hook_health_timer - single shot
            _hookHealthTimer = new DispatcherTimer();
            _hookHealthTimer.Interval = TimeSpan.FromMilliseconds(50);
            _hookHealthTimer.Tick += (s, e) => { _hookHealthTimer?.Stop(); EnsureHooksReady(); };

            // السطور 1182-1184: _ready_timer - single shot
            _readyTimer = new DispatcherTimer();
            _readyTimer.Interval = TimeSpan.FromMilliseconds(300);
            _readyTimer.Tick += (s, e) => { _readyTimer?.Stop(); MarkReady(); };

            // السطور 1192-1196: _mouse_tracker_timer - 50ms
            _mouseTrackerTimer = new DispatcherTimer();
            _mouseTrackerTimer.Interval = TimeSpan.FromMilliseconds(50);
            _mouseTrackerTimer.Tick += (s, e) => CheckMouseClick();
            _mouseTrackerTimer.Start();

            // السطور 1284-1286: _ctrl_v_timer - 20ms
            _ctrlVTimer = new DispatcherTimer();
            _ctrlVTimer.Interval = TimeSpan.FromMilliseconds(20);
            _ctrlVTimer.Tick += (s, e) => OnCtrlVPoll();
            _ctrlVTimer.Start();

            Console.WriteLine("[STARTUP] All timers initialized");
        }

        // ═══════════════════════════════════════════════════════════════
        // apply_settings - من OverlayWindow
        // يطبق الإعدادات على الواجهة
        // ═══════════════════════════════════════════════════════════════
        public void ApplySettings()
        {
            // Background color + opacity
            string bgColorHex = CONFIG.Instance.BgColor;
            int bgOpacity = CONFIG.Instance.BgOpacity;

            try
            {
                Color bgColor = (Color)ColorConverter.ConvertFromString(bgColorHex);
                bgColor.A = (byte)Math.Clamp(bgOpacity, 0, 255);
                TextEdit.Background = new SolidColorBrush(bgColor);
            }
            catch
            {
                TextEdit.Background = new SolidColorBrush(Color.FromArgb((byte)bgOpacity, 0, 0, 0));
            }

            // Text color + opacity
            string textColorHex = CONFIG.Instance.TextColor;
            int textOpacity = CONFIG.Instance.TextOpacity;

            try
            {
                Color textColor = (Color)ColorConverter.ConvertFromString(textColorHex);
                textColor.A = (byte)Math.Clamp(textOpacity, 0, 255);
                TextEdit.Foreground = new SolidColorBrush(textColor);
            }
            catch
            {
                TextEdit.Foreground = new SolidColorBrush(Color.FromArgb((byte)textOpacity, 255, 255, 0));
            }

            // Font size
            TextEdit.FontSize = CONFIG.Instance.FontSize;

            Console.WriteLine($"[SETTINGS] Applied: bg={bgColorHex}, text={textColorHex}, font={CONFIG.Instance.FontSize}");
        }

        // ═══════════════════════════════════════════════════════════════
        // Toggle - إظهار/إخفاء النافذة
        // ═══════════════════════════════════════════════════════════════
        public void Toggle()
        {
            if (this.Visibility == Visibility.Visible)
            {
                // Hide
                this.Hide();
                _inputState = "IDLE";
                Console.WriteLine("[TOGGLE] Hidden");
            }
            else
            {
                // Show with hooks
                ArmInput();
                AtomicShowFocus();
                Console.WriteLine("[TOGGLE] Shown");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // toggle_language - السطور 2597-2622
        // Toggle between Arabic and English input modes
        // ═══════════════════════════════════════════════════════════════
        public void ToggleLanguage()
        {
            // السطر 2599: self.is_arabic_mode = not self.is_arabic_mode
            _isArabicMode = !_isArabicMode;
            
            // السطر 2601: mode = "العربية" if self.is_arabic_mode else "English"
            string mode = _isArabicMode ? "العربية" : "English";
            Console.WriteLine($"Language mode: {mode}");
            
            // السطور 2604-2622: Apply/reset indent when chat is empty
            if (string.IsNullOrWhiteSpace(TextEdit.Text))
            {
                try
                {
                    // Get first_line_end from config
                    int lineEnd = CONFIG.Instance.FirstLineEnd;
                    
                    // Apply indent based on mode
                    if (_isArabicMode && lineEnd > 0)
                    {
                        // Arabic mode: apply text indent
                        TextEdit.Padding = new Thickness(8, 4, 8 + lineEnd, 4);
                    }
                    else
                    {
                        // English mode: reset indent
                        TextEdit.Padding = new Thickness(8, 4, 8, 4);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[LANG] Indent error: {ex.Message}");
                }
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // RegisterLanguageHotkey - السطور 1139-1143
        // Register Alt+Shift language toggle hotkey
        // ═══════════════════════════════════════════════════════════════
        private void RegisterLanguageHotkey()
        {
            try
            {
                // السطر 1141: keyboard.add_hotkey('alt+shift', self.toggle_language)
                // Using keyboard hook to detect Alt+Shift
                // This is handled in KeyboardHookManager when Alt+Shift is pressed
                Console.WriteLine("[HOTKEY] Alt+Shift language toggle registered");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[HOTKEY] Alt+Shift registration failed: {ex.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // _arm_input - السطور 1333-1385
        // تسليح الـ hook قبل الإظهار
        // ═══════════════════════════════════════════════════════════════
        private void ArmInput()
        {
            _inputState = "ARMING";
            _keystrokeBuffer.Clear();
            Console.WriteLine("[INPUT] State: ARMING");

            // Start DLL filter - السطور 1365-1373
            try
            {
                _mediaFilter = MediaFilterSingleton.GetFilter();
                _mediaFilter.Load();
                _mediaFilter.SetCallback(OnDllKeyEvent);
                _mediaFilter.Start();
                _mediaFilter.Enable(true);
                Console.WriteLine("[HOOK] DLL filter active (handles D,C,B,Q,G,P)");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[HOOK] DLL failed: {ex.Message}");
            }

            // Start ready timer - السطور 1383-1385
            _readyTimer?.Start();
        }

        // ═══════════════════════════════════════════════════════════════
        // _mark_ready - السطور 1396-1406
        // إعلان جاهزية الـ hook
        // ═══════════════════════════════════════════════════════════════
        private void MarkReady()
        {
            if (_inputState != "ARMING") return;

            _inputState = "READY";
            Console.WriteLine($"[INPUT] State: READY (buffered {_keystrokeBuffer.Count} keys)");

            // Inject buffered keystrokes - السطور 1404-1406
            foreach (var chr in _keystrokeBuffer)
            {
                OnInsertText(chr);
            }
            _keystrokeBuffer.Clear();
        }

        // ═══════════════════════════════════════════════════════════════
        // _atomic_show_focus - السطور 1408-1428
        // إظهار + رفع + تركيز كعملية ذرية
        // ═══════════════════════════════════════════════════════════════
        private void AtomicShowFocus()
        {
            this.Show();

            // Re-apply TOPMOST - السطور 1414-1420
            IntPtr hwnd = new System.Windows.Interop.WindowInteropHelper(this).Handle;
            SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);

            // Focus when ready - السطور 1423-1428
            Dispatcher.BeginInvoke(() =>
            {
                if (_inputState == "READY")
                {
                    TextEdit.Focus();
                }
            }, DispatcherPriority.Background);
        }

        // ═══════════════════════════════════════════════════════════════
        // _ensure_topmost - السطور 1472-1503
        // إعادة تطبيق TOPMOST
        // ═══════════════════════════════════════════════════════════════
        private void EnsureTopmost()
        {
            if (!this.IsVisible) return;

            IntPtr hwnd = new System.Windows.Interop.WindowInteropHelper(this).Handle;

            // Check and re-apply styles - السطور 1481-1491
            int currentStyle = GetWindowLong(hwnd, GWL_EXSTYLE);
            int requiredStyle = WS_EX_NOACTIVATE | WS_EX_TOPMOST;

            if ((currentStyle & requiredStyle) != requiredStyle)
            {
                SetWindowLong(hwnd, GWL_EXSTYLE, currentStyle | requiredStyle);
            }

            // Force window position - السطور 1493-1503
            SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW | SWP_FRAMECHANGED);
        }

        // ═══════════════════════════════════════════════════════════════
        // _check_fullscreen_toggle - السطور 1505-1540
        // ═══════════════════════════════════════════════════════════════
        private void CheckFullscreenToggle()
        {
            if (!this.IsVisible) return;

            IntPtr foreground = GetForegroundWindow();
            IntPtr hwnd = new System.Windows.Interop.WindowInteropHelper(this).Handle;

            if (foreground != hwnd && foreground != _lastForeground && _lastForeground != IntPtr.Zero)
            {
                double currentTime = Environment.TickCount / 1000.0;
                if (currentTime - _lastToggleTime < 0.3) // 300ms debounce
                {
                    _lastForeground = foreground;
                    return;
                }

                _lastToggleTime = currentTime;
                Console.WriteLine("[FULLSCREEN] Detected foreground change - auto-toggle!");

                this.Hide();
                Dispatcher.BeginInvoke(() => AutoShowTopmost(), DispatcherPriority.Background);
            }

            _lastForeground = foreground;
        }

        // ═══════════════════════════════════════════════════════════════
        // _auto_show_topmost - السطور 1542-1574
        // ═══════════════════════════════════════════════════════════════
        private void AutoShowTopmost()
        {
            this.Show();

            IntPtr hwnd = new System.Windows.Interop.WindowInteropHelper(this).Handle;
            int style = GetWindowLong(hwnd, GWL_EXSTYLE);
            SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOPMOST | WS_EX_LAYERED);
            SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW);

            Console.WriteLine("[FULLSCREEN] Restarting hooks after show");
            ArmInput();

            Dispatcher.BeginInvoke(() =>
            {
                if (_inputState == "READY")
                {
                    TextEdit.Focus();
                }
            }, DispatcherPriority.Background);
        }

        // ═══════════════════════════════════════════════════════════════
        // _ensure_hooks_ready - السطور 1576-1585
        // ═══════════════════════════════════════════════════════════════
        private void EnsureHooksReady()
        {
            if (_inputState == "IDLE" && this.IsVisible)
            {
                Console.WriteLine("[HEALTH] Hooks broken - restarting via ArmInput()");
                ArmInput();
            }
            else if (_inputState == "ARMING")
            {
                _hookHealthTimer?.Start();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // _check_mouse_click - السطور 1198-1279
        // ═══════════════════════════════════════════════════════════════
        private void CheckMouseClick()
        {
            if (CONFIG.Instance.GameClickX == -1) return;

            const int VK_LBUTTON = 0x01;
            const int VK_RBUTTON = 0x02;
            const int VK_MBUTTON = 0x04;

            IntPtr currentFg = GetForegroundWindow();
            IntPtr ourHwnd = this.IsVisible
                ? new System.Windows.Interop.WindowInteropHelper(this).Handle
                : IntPtr.Zero;

            bool onTargetGame = currentFg == _targetGameHwnd;

            if (onTargetGame)
            {
                bool left = (GetAsyncKeyState(VK_LBUTTON) & 0x8000) != 0;
                bool right = (GetAsyncKeyState(VK_RBUTTON) & 0x8000) != 0;
                bool middle = (GetAsyncKeyState(VK_MBUTTON) & 0x8000) != 0;

                if (left || right || middle)
                {
                    if (!_mouseClickedSinceSend)
                    {
                        Console.WriteLine("[FOCUS] Mouse clicked on GAME - needs_enter=True");
                    }
                    _mouseClickedSinceSend = true;
                }
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // _on_ctrl_v_poll - السطور 1289-1298
        // ═══════════════════════════════════════════════════════════════
        private void OnCtrlVPoll()
        {
            if (_mediaFilter != null)
            {
                bool ctrlVPressed = _mediaFilter.CheckCtrlV();
                if (ctrlVPressed && this.IsVisible && _inputState != "SENDING")
                {
                    Console.WriteLine("[POLL] Ctrl+V detected!");
                    DoPaste();
                }
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // _do_paste - السطور 1300-1327
        // ═══════════════════════════════════════════════════════════════
        private void DoPaste()
        {
            try
            {
                string winClip = Clipboard.GetText();

                if (!string.IsNullOrEmpty(winClip) && winClip != _lastSentMessage)
                {
                    int pos = TextEdit.CaretIndex;
                    TextEdit.Text = TextEdit.Text.Insert(pos, winClip);
                    TextEdit.CaretIndex = pos + winClip.Length;
                    _internalClipboard = winClip;
                    Console.WriteLine($"[PASTE] Pasted NEW: {winClip.Substring(0, Math.Min(20, winClip.Length))}...");
                }
                else if (!string.IsNullOrEmpty(_internalClipboard))
                {
                    int pos = TextEdit.CaretIndex;
                    TextEdit.Text = TextEdit.Text.Insert(pos, _internalClipboard);
                    TextEdit.CaretIndex = pos + _internalClipboard.Length;
                    Console.WriteLine($"[PASTE] Pasted INTERNAL: {_internalClipboard.Substring(0, Math.Min(20, _internalClipboard.Length))}...");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[PASTE] Error: {ex.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // reload_hotkey - يعيد تحميل hooks
        // ═══════════════════════════════════════════════════════════════
        private void ReloadHotkey()
        {
            Console.WriteLine("[HOTKEY] Reloading keyboard hooks...");
            // Keyboard hooks will be started in ArmInput()
            Console.WriteLine("[HOTKEY] Keyboard hooks ready");
        }

        // ═══════════════════════════════════════════════════════════════
        // DLL Callback - السطر 1368
        // ═══════════════════════════════════════════════════════════════
        private void OnDllKeyEvent(uint vkCode, uint scanCode, uint flags)
        {
            // Handle media letter keys (D, C, B, Q, G, P)
            Dispatcher.BeginInvoke(() =>
            {
                if (!this.IsVisible || _inputState == "SENDING") return;

                char? keyChar = scanCode switch
                {
                    32 => 'd', 46 => 'c', 48 => 'b',
                    16 => 'q', 34 => 'g', 25 => 'p',
                    _ => null
                };

                if (keyChar.HasValue)
                {
                    bool shift = (Keyboard.Modifiers & ModifierKeys.Shift) != 0;
                    string? arabic = _isArabicMode ? KeyboardMapper.GetArabicChar(keyChar.Value, shift) : null;

                    if (arabic != null)
                    {
                        OnInsertText(arabic);
                    }
                    else
                    {
                        OnInsertText(keyChar.Value.ToString());
                    }
                }
            });
        }

        // ═══════════════════════════════════════════════════════════════
        // on_insert_text - السطور 2445-2450
        // ═══════════════════════════════════════════════════════════════
        private void OnInsertText(string text)
        {
            if (!this.IsVisible) return;

            int pos = TextEdit.CaretIndex;
            TextEdit.Text = TextEdit.Text.Insert(pos, text);
            TextEdit.CaretIndex = pos + text.Length;
        }

        // ═══════════════════════════════════════════════════════════════
        // TextEdit Event Handlers
        // ═══════════════════════════════════════════════════════════════
        private void TextEdit_TextInput(object sender, TextCompositionEventArgs e)
        {
            // Block native input - hooks handle everything
            e.Handled = true;
        }

        private void TextEdit_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            // Enter = send - السطور 1022-1028
            if (e.Key == Key.Enter && !Keyboard.IsKeyDown(Key.LeftShift) && !Keyboard.IsKeyDown(Key.RightShift))
            {
                e.Handled = true;
                SendText();
                return;
            }

            // Escape = hide
            if (e.Key == Key.Escape)
            {
                e.Handled = true;
                Toggle();
                return;
            }

            // Ctrl+A = select all
            if (e.Key == Key.A && Keyboard.Modifiers == ModifierKeys.Control)
            {
                e.Handled = true;
                TextEdit.SelectAll();
                return;
            }

            // Ctrl+V = paste
            if (e.Key == Key.V && Keyboard.Modifiers == ModifierKeys.Control)
            {
                e.Handled = true;
                DoPaste();
                return;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // send_text - إرسال النص (سيتم تفصيله لاحقاً)
        // ═══════════════════════════════════════════════════════════════
        public void SendText()
        {
            string text = TextEdit.Text.Trim();
            if (string.IsNullOrEmpty(text)) return;

            Console.WriteLine($"[SEND] Sending: {text.Substring(0, Math.Min(30, text.Length))}...");

            // Process Arabic text
            string processed = _processor.ProcessText(text);
            processed = _processor.FixBidiNumbers(processed);

            // Save to last sent message
            _lastSentMessage = processed;

            // Copy to clipboard
            try
            {
                System.Windows.Clipboard.SetText(processed);
            }
            catch { }

            // Clear text edit
            TextEdit.Clear();

            // Reset mouse click flag
            _mouseClickedSinceSend = false;

            Console.WriteLine("[SEND] Complete");
        }

        // ═══════════════════════════════════════════════════════════════
        // Context Menu Handlers - من NativeTextEdit.show_context_menu
        // ═══════════════════════════════════════════════════════════════
        private void ContextMenu_Undo(object sender, RoutedEventArgs e) => TextEdit.Undo();
        private void ContextMenu_Redo(object sender, RoutedEventArgs e) => TextEdit.Redo();
        private void ContextMenu_Cut(object sender, RoutedEventArgs e) => TextEdit.Cut();
        private void ContextMenu_Copy(object sender, RoutedEventArgs e) => TextEdit.Copy();
        private void ContextMenu_Paste(object sender, RoutedEventArgs e) => DoPaste();
        private void ContextMenu_SelectAll(object sender, RoutedEventArgs e) => TextEdit.SelectAll();

        // ═══════════════════════════════════════════════════════════════
        // enterEvent - السطور 2467-2470
        // Show buttons when mouse enters chat area
        // ═══════════════════════════════════════════════════════════════
        private void Window_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e)
        {
            // السطر 2469: self._show_buttons_with_timer()
            _buttonsManager?.ShowButtonsWithTimer();
        }

        // ═══════════════════════════════════════════════════════════════
        // leaveEvent - السطور 2472-2475
        // When mouse leaves chat, buttons stay visible for 5 seconds
        // ═══════════════════════════════════════════════════════════════
        private void Window_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e)
        {
            // Buttons remain visible via timer in FloatingButtonsManager
            // السطر 2474: buttons will auto-hide after 5 seconds
        }

        // ═══════════════════════════════════════════════════════════════
        // mousePressEvent - السطور 1638-1663 (resize) + 2523-2527 (drag)
        // ═══════════════════════════════════════════════════════════════
        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            var pos = e.GetPosition(this);
            var globalPos = PointToScreen(pos);

            // السطور 1638-1663: Try resize first
            if (_resizeHelper != null && _resizeHelper.StartResizeIfAtEdge(pos, globalPos))
            {
                return;  // Resize mode started
            }

            // السطور 2523-2527: Start drag
            if (e.LeftButton == MouseButtonState.Pressed)
            {
                this.DragMove();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // mouseMoveEvent - السطور 1665-1732 (resize cursor)
        // ═══════════════════════════════════════════════════════════════
        private void Window_MouseMove(object sender, System.Windows.Input.MouseEventArgs e)
        {
            var pos = e.GetPosition(this);
            var globalPos = PointToScreen(pos);

            // السطور 1665-1732: Handle resize cursor and movement
            _resizeHelper?.HandleMouseMoveForResize(pos, globalPos);
            
            // Position buttons when moving
            _buttonsManager?.PositionButtons();
        }

        // ═══════════════════════════════════════════════════════════════
        // mouseReleaseEvent - السطور 1734-1744 (resize) + 2533-2538 (drag)
        // ═══════════════════════════════════════════════════════════════
        private void Window_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            // السطور 1734-1744: End resize
            _resizeHelper?.EndResize();

            // السطور 2536-2538: Save position
            CONFIG.Instance.X = (int)this.Left;
            CONFIG.Instance.Y = (int)this.Top;
            CONFIG.Instance.W = (int)this.Width;
            CONFIG.Instance.H = (int)this.Height;
        }

        // ═══════════════════════════════════════════════════════════════
        // Window Closing
        // ═══════════════════════════════════════════════════════════════
        protected override void OnClosing(System.ComponentModel.CancelEventArgs e)
        {
            // Stop timers
            _topmostTimer?.Stop();
            _fullscreenCheckTimer?.Stop();
            _mouseTrackerTimer?.Stop();
            _ctrlVTimer?.Stop();

            // Dispose MediaFilter
            _mediaFilter?.Dispose();

            base.OnClosing(e);
        }

        // ═══════════════════════════════════════════════════════════════
        // toggle_settings - السطور 2540-2545
        // ═══════════════════════════════════════════════════════════════
        public void ToggleSettings()
        {
            if (_settingsWindow != null && _settingsWindow.IsVisible)
            {
                _settingsWindow.Hide();
            }
            else
            {
                OpenSettings();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // open_settings - السطور 2547-2557
        // ═══════════════════════════════════════════════════════════════
        public void OpenSettings()
        {
            if (_settingsWindow == null || !_settingsWindow.IsVisible)
            {
                _settingsWindow = new Styles.SettingsWindow();

                // Restore saved position or use default - السطور 2551-2556
                int savedX = CONFIG.Instance.SettingsX;
                int savedY = CONFIG.Instance.SettingsY;
                if (savedX != -1 && savedY != -1)
                {
                    _settingsWindow.Left = savedX;
                    _settingsWindow.Top = savedY;
                }
                else
                {
                    _settingsWindow.Left = this.Left + this.Width + 20;
                    _settingsWindow.Top = this.Top;
                }

                _settingsWindow.Show();
            }
        }
    }
}