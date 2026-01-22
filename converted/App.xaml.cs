// ═══════════════════════════════════════════════════════════════════════════════
// App.xaml.cs - نقطة دخول التطبيق
// المقابل لـ: main.py if __name__ == "__main__" (السطور 3270-3298)
// تحويل سطر بسطر - Single instance + Hotkey
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows;
using System.Windows.Interop;
using MessageBox = System.Windows.MessageBox;

namespace SmartKeyboard
{
    /// <summary>
    /// Application entry point
    /// </summary>
    public partial class App : System.Windows.Application
    {
        // ═══════════════════════════════════════════════════════════════
        // P/Invoke for global hotkey
        // ═══════════════════════════════════════════════════════════════
        [DllImport("user32.dll")]
        private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

        [DllImport("user32.dll")]
        private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

        // Hotkey constants
        private const int HOTKEY_ID = 9000;
        private const uint VK_INSERT = 0x2D;
        private const uint MOD_NONE = 0x0000;

        // ═══════════════════════════════════════════════════════════════
        // المتغيرات
        // ═══════════════════════════════════════════════════════════════
        
        // Single instance mutex
        private static Mutex? _mutex;
        
        // Main window
        private MainWindow? _mainWindow;
        
        // Hotkey window source
        private HwndSource? _hwndSource;

        // ═══════════════════════════════════════════════════════════════
        // OnStartup - نقطة الدخول الرئيسية
        // من if __name__ == "__main__"
        // ═══════════════════════════════════════════════════════════════
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Single instance check - من السطور 3270-3275
            _mutex = new Mutex(true, "SmartKeyboard_SingleInstance", out bool createdNew);
            if (!createdNew)
            {
                MessageBox.Show("Smart Keyboard is already running!", "Smart Keyboard", MessageBoxButton.OK, MessageBoxImage.Information);
                Shutdown();
                return;
            }

            Console.WriteLine("[STARTUP] Smart Keyboard v" + Version.VERSION);

            // Create main window - السطر 3285
            _mainWindow = new MainWindow();

            // Show window initially
            _mainWindow.Show();
            Console.WriteLine("[STARTUP] MainWindow shown");

            // Register global hotkey (Insert key) - من reload_hotkey السطر 1141
            RegisterGlobalHotkey();

            Console.WriteLine("[STARTUP] Application ready");
        }

        // ═══════════════════════════════════════════════════════════════
        // RegisterGlobalHotkey - تسجيل مفتاح Insert
        // من keyboard.add_hotkey('insert', self.toggle)
        // ═══════════════════════════════════════════════════════════════
        private void RegisterGlobalHotkey()
        {
            if (_mainWindow == null) return;

            // Get window handle
            var helper = new WindowInteropHelper(_mainWindow);
            IntPtr hwnd = helper.Handle;

            if (hwnd == IntPtr.Zero)
            {
                // Window not ready yet, defer
                _mainWindow.Loaded += (s, e) => RegisterGlobalHotkey();
                return;
            }

            // Create HwndSource for message handling
            _hwndSource = HwndSource.FromHwnd(hwnd);
            _hwndSource?.AddHook(WndProc);

            // Register Insert key - السطر 1141: keyboard.add_hotkey('insert', self.toggle)
            string hotkeyConfig = CONFIG.Instance.Hotkey.ToLower();
            uint vkCode = hotkeyConfig switch
            {
                "insert" => VK_INSERT,
                _ => VK_INSERT
            };

            if (RegisterHotKey(hwnd, HOTKEY_ID, MOD_NONE, vkCode))
            {
                Console.WriteLine($"[HOTKEY] Registered: {hotkeyConfig} (VK=0x{vkCode:X2})");
            }
            else
            {
                Console.WriteLine($"[HOTKEY] Failed to register: {hotkeyConfig}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // WndProc - معالجة رسائل Windows
        // ═══════════════════════════════════════════════════════════════
        private IntPtr WndProc(IntPtr hwnd, int msg, IntPtr wParam, IntPtr lParam, ref bool handled)
        {
            const int WM_HOTKEY = 0x0312;

            if (msg == WM_HOTKEY && wParam.ToInt32() == HOTKEY_ID)
            {
                handled = true;
                _mainWindow?.Toggle();
                Console.WriteLine("[HOTKEY] Insert pressed - Toggle");
            }

            return IntPtr.Zero;
        }

        // ═══════════════════════════════════════════════════════════════
        // OnExit - تنظيف الموارد
        // ═══════════════════════════════════════════════════════════════
        protected override void OnExit(ExitEventArgs e)
        {
            // Unregister hotkey
            if (_mainWindow != null)
            {
                var helper = new WindowInteropHelper(_mainWindow);
                UnregisterHotKey(helper.Handle, HOTKEY_ID);
            }

            // Release mutex
            _mutex?.ReleaseMutex();
            _mutex?.Dispose();

            Console.WriteLine("[EXIT] Application closed");
            base.OnExit(e);
        }
    }
}
