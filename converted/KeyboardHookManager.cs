// ═══════════════════════════════════════════════════════════════════════════════
// KeyboardHookManager.cs - مدير لوحة المفاتيح
// المقابل لـ: main.py السطور 2057-2443
// تحويل سطر بسطر - كل scan code وكل حالة مطابقة للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Windows.Input;
using SharpHook;
using SharpHook.Native;
using WpfApplication = System.Windows.Application;
using WpfClipboard = System.Windows.Clipboard;

namespace SmartKeyboard
{
    /// <summary>
    /// Keyboard Hook Manager - من start_keyboard_hooks السطور 2057-2443
    /// يدير كل مدخلات لوحة المفاتيح مع suppression
    /// </summary>
    public class KeyboardHookManager : IDisposable
    {
        // ═══════════════════════════════════════════════════════════════
        // P/Invoke
        // ═══════════════════════════════════════════════════════════════
        [DllImport("user32.dll")]
        private static extern short GetKeyState(int nVirtKey);

        [DllImport("user32.dll")]
        private static extern short GetAsyncKeyState(int vKey);

        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - من start_keyboard_hooks السطور 2063-2090
        // ═══════════════════════════════════════════════════════════════

        // السطر 2064: self.media_letter_scans = {32, 46, 48, 16, 34, 25}
        private readonly HashSet<ushort> _mediaLetterScans = new() { 32, 46, 48, 16, 34, 25 };

        // السطور 2067-2081: self.typing_scan_codes
        private readonly Dictionary<ushort, string> _typingScanCodes = new()
        {
            // السطر 2069: QWERTY Row (Q and P removed - handled by DLL)
            { 17, "w" }, { 18, "e" }, { 19, "r" }, { 20, "t" }, { 21, "y" }, { 22, "u" }, { 23, "i" }, { 24, "o" },
            // السطر 2071: ASDF Row (D and G removed - handled by DLL)
            { 30, "a" }, { 31, "s" }, { 33, "f" }, { 35, "h" }, { 36, "j" }, { 37, "k" }, { 38, "l" },
            // السطر 2073: ZXCV Row (C and B removed - handled by DLL)
            { 44, "z" }, { 45, "x" }, { 47, "v" }, { 49, "n" }, { 50, "m" },
            // السطور 2075: Number Row
            { 2, "1" }, { 3, "2" }, { 4, "3" }, { 5, "4" }, { 6, "5" }, { 7, "6" }, { 8, "7" }, { 9, "8" }, { 10, "9" }, { 11, "0" },
            // السطور 2077-2078: Symbols
            { 12, "-" }, { 13, "=" }, { 26, "[" }, { 27, "]" }, { 43, "\\" }, { 39, ";" }, { 40, "'" }, { 51, "," }, { 52, "." }, { 53, "/" },
            { 41, "`" },
            // السطر 2080: Space, Backspace, Enter
            { 57, "space" }, { 14, "backspace" }, { 28, "enter" }
        };

        // السطر 2084: self.dll_scan_to_name
        private readonly Dictionary<ushort, string> _dllScanToName = new()
        {
            { 32, "d" }, { 46, "c" }, { 48, "b" }, { 16, "q" }, { 34, "g" }, { 25, "p" }
        };

        // السطور 2087-2090: self.nav_scan_codes
        private readonly Dictionary<ushort, string> _navScanCodes = new()
        {
            { 75, "left" }, { 77, "right" }, { 72, "up" }, { 80, "down" },
            { 83, "delete" }, { 71, "home" }, { 79, "end" }
        };

        // السطور 2229-2234: NUMPAD_ALWAYS_SYMBOLS
        private readonly Dictionary<ushort, char> _numpadAlwaysSymbols = new()
        {
            { 78, '+' },  // Numpad +
            { 74, '-' },  // Numpad -
            { 55, '*' },  // Numpad *
            { 309, '/' }  // Numpad / (extended key)
        };

        // السطور 2238-2250: NUMPAD_NUMBERS
        private readonly Dictionary<ushort, char> _numpadNumbers = new()
        {
            { 82, '0' },  // Numpad 0 / Ins
            { 79, '1' },  // Numpad 1 / End
            { 80, '2' },  // Numpad 2 / Down
            { 81, '3' },  // Numpad 3 / PgDn
            { 75, '4' },  // Numpad 4 / Left
            { 76, '5' },  // Numpad 5
            { 77, '6' },  // Numpad 6 / Right
            { 71, '7' },  // Numpad 7 / Home
            { 72, '8' },  // Numpad 8 / Up
            { 73, '9' },  // Numpad 9 / PgUp
            { 83, '.' }   // Numpad . / Del
        };

        // السطور 2377-2382: shift_map for English mode
        private readonly Dictionary<char, char> _shiftMap = new()
        {
            { '1', '!' }, { '2', '@' }, { '3', '#' }, { '4', '$' }, { '5', '%' }, { '6', '^' },
            { '7', '&' }, { '8', '*' }, { '9', '(' }, { '0', ')' }, { '-', '_' }, { '=', '+' },
            { '[', '{' }, { ']', '}' }, { '\\', '|' }, { ';', ':' }, { '\'', '"' },
            { ',', '<' }, { '.', '>' }, { '/', '?' }
        };

        // ═══════════════════════════════════════════════════════════════
        // Callbacks and references
        // ═══════════════════════════════════════════════════════════════
        private readonly Action<string> _onInsertText;
        private readonly Action _onBackspace;
        private readonly Action _onSendText;
        private readonly Func<bool> _getIsArabicMode;
        private readonly Func<string> _getInputState;
        private readonly Action<string> _addToBuffer;

        private TaskPoolGlobalHook? _hook;
        private bool _isRunning = false;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ
        // ═══════════════════════════════════════════════════════════════
        public KeyboardHookManager(
            Action<string> onInsertText,
            Action onBackspace,
            Action onSendText,
            Func<bool> getIsArabicMode,
            Func<string> getInputState,
            Action<string> addToBuffer)
        {
            _onInsertText = onInsertText;
            _onBackspace = onBackspace;
            _onSendText = onSendText;
            _getIsArabicMode = getIsArabicMode;
            _getInputState = getInputState;
            _addToBuffer = addToBuffer;
        }

        // ═══════════════════════════════════════════════════════════════
        // start_keyboard_hooks - السطور 2057-2110
        // ═══════════════════════════════════════════════════════════════
        public void Start()
        {
            Stop();
            Console.WriteLine("[HOOK] Starting keyboard hooks...");

            try
            {
                _hook = new TaskPoolGlobalHook();
                _hook.KeyPressed += OnKeyPressed;
                _hook.RunAsync();
                _isRunning = true;
                Console.WriteLine($"[HOOK] Keyboard hook installed ({_typingScanCodes.Count} typing + {_navScanCodes.Count} nav keys)");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[HOOK] Failed: {ex.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // stop_keyboard_hooks - السطور 2112-2129
        // ═══════════════════════════════════════════════════════════════
        public void Stop()
        {
            if (_hook != null && _isRunning)
            {
                Console.WriteLine("[HOOK] Stopping keyboard hook...");
                try
                {
                    _hook.Dispose();
                    _hook = null;
                    _isRunning = false;
                    Console.WriteLine("[HOOK] Keyboard hook stopped");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[HOOK] Error stopping hook: {ex.Message}");
                }
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // on_keyboard_event - السطور 2182-2443
        // Smart keyboard handler with proper suppression and State Machine
        // ═══════════════════════════════════════════════════════════════
        private void OnKeyPressed(object? sender, KeyboardHookEventArgs e)
        {
            ushort scanCode = e.RawEvent.Keyboard.RawCode;
            string inputState = _getInputState();

            // ==========================================
            // السطور 2189-2198: SYSTEM KEY EXCEPTIONS
            // ==========================================
            try
            {
                bool winPressed = Keyboard.IsKeyDown(Key.LWin) || Keyboard.IsKeyDown(Key.RWin);
                bool altTab = Keyboard.IsKeyDown(Key.LeftAlt) && Keyboard.IsKeyDown(Key.Tab);
                if (winPressed || altTab)
                {
                    return; // Let system keys through
                }
            }
            catch { }

            // ==========================================
            // السطور 2204-2218: STATE MACHINE HANDLING
            // ==========================================

            // السطور 2205-2214: أثناء ARMING: خزّن الأحرف في buffer
            if (inputState == "ARMING")
            {
                if (_typingScanCodes.TryGetValue(scanCode, out string? keyName))
                {
                    if (keyName != "space" && keyName != "backspace" && keyName != "enter")
                    {
                        string? chr = GetCharForKey(keyName);
                        if (chr != null && chr.Length >= 1)
                        {
                            _addToBuffer(chr);
                            Console.WriteLine($"[BUFFER] Stored: {chr}");
                        }
                    }
                }
                e.SuppressEvent = true; // منع تام أثناء ARMING
                return;
            }

            // السطور 2217-2218: أثناء SENDING: امنع أي إدخال جديد
            if (inputState == "SENDING")
            {
                e.SuppressEvent = true;
                return;
            }

            // ==========================================
            // السطور 2224-2300: NUMPAD HANDLING
            // ==========================================
            bool isNumpad = scanCode >= 71 && scanCode <= 83;

            if (isNumpad || _numpadAlwaysSymbols.ContainsKey(scanCode))
            {
                // السطور 2257-2267: ALWAYS WORKING SYMBOLS
                if (_numpadAlwaysSymbols.TryGetValue(scanCode, out char symbol))
                {
                    Console.WriteLine($"[NUMPAD] Symbol (always): {symbol}");
                    WpfApplication.Current?.Dispatcher.Invoke(() => _onInsertText(symbol.ToString()));
                    e.SuppressEvent = true;
                    return;
                }

                // السطور 2269-2291: NUM LOCK DEPENDENT KEYS
                if (_numpadNumbers.TryGetValue(scanCode, out char numChar))
                {
                    const int VK_NUMLOCK = 0x90;
                    bool numLockOn = (GetKeyState(VK_NUMLOCK) & 1) != 0;

                    if (numLockOn)
                    {
                        Console.WriteLine($"[NUMPAD] Num Lock ON - typing: {numChar}");
                        WpfApplication.Current?.Dispatcher.Invoke(() => _onInsertText(numChar.ToString()));
                        e.SuppressEvent = true;
                        return;
                    }
                    else
                    {
                        // Num Lock OFF - navigation mode
                        if (scanCode == 83)
                        {
                            Console.WriteLine("[NUMPAD] Num Lock OFF - Delete");
                            // Handle delete in nav section below
                        }
                        Console.WriteLine("[NUMPAD] Num Lock OFF - passing as navigation");
                        // Fall through to nav handling
                    }
                }
            }

            // السطور 2293-2300: Numpad Enter
            if (scanCode == 28 && isNumpad)
            {
                Console.WriteLine("[NUMPAD] Numpad Enter - sending message");
                bool shift = Keyboard.IsKeyDown(Key.LeftShift) || Keyboard.IsKeyDown(Key.RightShift);
                if (shift)
                {
                    WpfApplication.Current?.Dispatcher.Invoke(() => _onInsertText("\n"));
                }
                else
                {
                    WpfApplication.Current?.Dispatcher.Invoke(() => _onSendText());
                }
                e.SuppressEvent = true;
                return;
            }

            // السطور 2302-2304: فحص Ctrl الفعلي
            const int VK_CONTROL = 0x11;
            bool ctrlPressed = (GetAsyncKeyState(VK_CONTROL) & 0x8000) != 0;

            // ==========================================
            // السطور 2306-2394: TYPING KEYS HANDLING
            // ==========================================
            if (_typingScanCodes.TryGetValue(scanCode, out string? typingKeyName))
            {
                Console.WriteLine($"[KEY] Type: {typingKeyName}");

                // السطور 2311-2346: Handle Ctrl shortcuts
                if (ctrlPressed)
                {
                    Console.WriteLine($"[KEY] Ctrl+{typingKeyName}");

                    switch (typingKeyName)
                    {
                        case "a": // السطور 2314-2315: Select All
                            WpfApplication.Current?.Dispatcher.Invoke(() =>
                            {
                                // Will be handled by MainWindow
                            });
                            break;
                        case "v": // السطور 2316-2333: Paste
                            WpfApplication.Current?.Dispatcher.Invoke(() =>
                            {
                                try
                                {
                                    string winClip = Clipboard.GetText();
                                    if (!string.IsNullOrEmpty(winClip))
                                    {
                                        _onInsertText(winClip);
                                        Console.WriteLine($"[KEY] Ctrl+V: {winClip.Substring(0, Math.Min(20, winClip.Length))}...");
                                    }
                                }
                                catch { }
                            });
                            break;
                        case "x": // السطور 2334-2340: Cut
                            Console.WriteLine("[KEY] Ctrl+X");
                            break;
                        case "z": // السطر 2341-2342: Undo
                            Console.WriteLine("[KEY] Ctrl+Z");
                            break;
                        case "y": // السطور 2343-2344: Redo
                            Console.WriteLine("[KEY] Ctrl+Y");
                            break;
                    }
                    e.SuppressEvent = true;
                    return;
                }

                // السطور 2348-2351: Windows key
                bool winPressed2 = Keyboard.IsKeyDown(Key.LWin) || Keyboard.IsKeyDown(Key.RWin);
                if (winPressed2)
                {
                    Console.WriteLine("[KEY] Windows key - let through");
                    return;
                }

                // السطور 2354-2359: Enter
                if (typingKeyName == "enter")
                {
                    bool shift = Keyboard.IsKeyDown(Key.LeftShift) || Keyboard.IsKeyDown(Key.RightShift);
                    if (shift)
                    {
                        WpfApplication.Current?.Dispatcher.Invoke(() => _onInsertText("\n"));
                    }
                    else
                    {
                        WpfApplication.Current?.Dispatcher.Invoke(() => _onSendText());
                    }
                    e.SuppressEvent = true;
                    return;
                }

                // السطور 2361-2363: Backspace
                if (typingKeyName == "backspace")
                {
                    WpfApplication.Current?.Dispatcher.Invoke(() => _onBackspace());
                    e.SuppressEvent = true;
                    return;
                }

                // السطور 2365-2367: Space
                if (typingKeyName == "space")
                {
                    WpfApplication.Current?.Dispatcher.Invoke(() => _onInsertText(" "));
                    e.SuppressEvent = true;
                    return;
                }

                // السطور 2370-2394: Regular typing
                if (typingKeyName.Length == 1)
                {
                    string? chr = GetCharForKey(typingKeyName);
                    if (chr != null)
                    {
                        WpfApplication.Current?.Dispatcher.Invoke(() => _onInsertText(chr));
                    }
                    e.SuppressEvent = true;
                    return;
                }
            }

            // ==========================================
            // السطور 2396-2430: NAVIGATION KEYS
            // ==========================================
            if (_navScanCodes.TryGetValue(scanCode, out string? navKeyName))
            {
                Console.WriteLine($"[KEY] Nav: {navKeyName}");
                // Navigation keys pass through to text edit
                // Don't suppress - let them work in game too (السطر 2430)
                return;
            }

            // السطور 2432-2440: Ctrl+C (C is handled by DLL)
            if (scanCode == 46 && ctrlPressed)
            {
                Console.WriteLine("[KEY] Ctrl+C - copy");
                e.SuppressEvent = true;
                return;
            }

            // السطر 2443: All other keys - let through
        }

        // ═══════════════════════════════════════════════════════════════
        // _get_char_for_key - السطور 1430-1454
        // ═══════════════════════════════════════════════════════════════
        private string? GetCharForKey(string keyName)
        {
            if (keyName == "space" || keyName == "backspace" || keyName == "enter")
                return null;

            bool shift = Keyboard.IsKeyDown(Key.LeftShift) || Keyboard.IsKeyDown(Key.RightShift);
            bool capsLock = (GetKeyState(0x14) & 1) != 0;

            if (_getIsArabicMode())
            {
                // Arabic mode - use KeyboardMapper
                if (keyName.Length == 1)
                {
                    return KeyboardMapper.GetArabicChar(keyName[0], shift);
                }
            }
            else
            {
                // English mode - السطور 1441-1454
                if (keyName.Length == 1)
                {
                    char c = keyName[0];

                    if (shift && _shiftMap.TryGetValue(c, out char shiftedChar))
                    {
                        return shiftedChar.ToString();
                    }

                    // Caps Lock XOR Shift = uppercase
                    bool uppercase = capsLock != shift;
                    return uppercase ? keyName.ToUpper() : keyName.ToLower();
                }
            }

            return keyName;
        }

        // ═══════════════════════════════════════════════════════════════
        // Dispose
        // ═══════════════════════════════════════════════════════════════
        public void Dispose()
        {
            Stop();
            GC.SuppressFinalize(this);
        }
    }
}
