// ═══════════════════════════════════════════════════════════════════════════════
// NativeTextEdit.cs - مربع النص المخصص مع قائمة سياق ووميض مؤشر
// المقابل لـ: main.py class NativeTextEdit (السطور 801-1055)
// تحويل سطر بسطر - كل وظيفة ولوحة مفاتيح عربية مطابقة للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using RichTextBox = System.Windows.Controls.RichTextBox;
using KeyEventArgs = System.Windows.Input.KeyEventArgs;
using Brushes = System.Windows.Media.Brushes;
using Clipboard = System.Windows.Clipboard;
using Size = System.Windows.Size;

namespace SmartKeyboard
{
    // ═══════════════════════════════════════════════════════════════
    // NativeTextEdit - مربع النص المخصص مع Arabic Input
    // السطور 801-1055
    // ═══════════════════════════════════════════════════════════════
    public class NativeTextEdit : RichTextBox
    {
        private readonly MainWindow? _parentWindow;
        private CustomContextMenu? _contextMenu;

        // السطور 810-813: Caret Timer
        private readonly DispatcherTimer _caretTimer;
        private bool _caretVisible = true;

        // السطر 816: Arabic mode flag
        public bool IsArabicMode { get; set; } = true;

        // ═══════════════════════════════════════════════════════════════
        // Arabic keyboard mapping - السطور 928-1000
        // ═══════════════════════════════════════════════════════════════

        // السطور 928-949: Standard Arabic keyboard layout (no shift)
        private static readonly Dictionary<char, string> ArabicMap = new()
        {
            // Numbers row
            {'1', "1"}, {'2', "2"}, {'3', "3"}, {'4', "4"}, {'5', "5"},
            {'6', "6"}, {'7', "7"}, {'8', "8"}, {'9', "9"}, {'0', "0"},
            {'-', "-"}, {'=', "="},

            // Top row (QWERTY -> Arabic)
            {'q', "ض"}, {'w', "ص"}, {'e', "ث"}, {'r', "ق"}, {'t', "ف"},
            {'y', "غ"}, {'u', "ع"}, {'i', "ه"}, {'o', "خ"}, {'p', "ح"},
            {'[', "ج"}, {']', "د"},

            // Middle row (ASDF -> Arabic)
            {'a', "ش"}, {'s', "س"}, {'d', "ي"}, {'f', "ب"}, {'g', "ل"},
            {'h', "ا"}, {'j', "ت"}, {'k', "ن"}, {'l', "م"}, {';', "ك"}, {'\'', "ط"},

            // Bottom row (ZXCV -> Arabic)
            {'z', "ئ"}, {'x', "ء"}, {'c', "ؤ"}, {'v', "ر"}, {'b', "لا"},
            {'n', "ى"}, {'m', "ة"}, {',', "و"}, {'.', "ز"}, {'/', "ظ"},

            // Special keys
            {'`', "ذ"}, {'\\', "\\"}
        };

        // السطور 952-1000: Shifted Arabic (Shift + key)
        private static readonly Dictionary<char, string> ArabicShiftMap = new()
        {
            // Numbers row with shift -> symbols
            {'1', "!"}, {'2', "@"}, {'3', "#"}, {'4', "$"}, {'5', "%"},
            {'6', "^"}, {'7', "&"}, {'8', "*"}, {'9', "("}, {'0', ")"},
            {'-', "_"}, {'=', "+"},

            // Top row shifted (Arabic diacritics and symbols)
            {'q', "َ"},   // Fatha
            {'w', "ً"},   // Tanween Fath
            {'e', "ُ"},   // Damma
            {'r', "ٌ"},   // Tanween Damm
            {'t', "لإ"},  // Lam with Hamza below
            {'y', "إ"},   // Hamza on alif below
            {'u', "'"},   // APOSTROPHE (ASCII 39)
            {'i', "÷"},   // Division
            {'o', "×"},   // Multiplication
            {'p', "؛"},   // Arabic semicolon
            {'[', "<"},
            {']', ">"},

            // Middle row shifted
            {'a', "ِ"},   // Kasra
            {'s', "ٍ"},   // Tanween Kasr
            {'d', "]"},   // Right bracket
            {'f', "["},   // Left bracket
            {'g', "لأ"},  // Lam with Hamza above
            {'h', "أ"},   // Hamza on alif
            {'j', "ـ"},   // Tatweel (Arabic Tatweel U+0640)
            {'k', "،"},   // Arabic comma
            {'l', "/"},   // Forward slash
            {';', ":"},   // Colon
            {'\'', "\""}, // Double quote

            // Bottom row shifted
            {'z', "~"},   // Tilde
            {'x', "ْ"},   // Sukun
            {'c', "}"},   // Right brace
            {'v', "{"},   // Left brace
            {'b', "لآ"},  // Lam with Mad
            {'n', "آ"},   // Alif with Mad
            {'m', "'"},   // APOSTROPHE (ASCII 39)
            {',', "<"},   // Less than
            {'.', ">"},   // Greater than
            {'/', "؟"},   // Arabic question mark

            // Special shifted
            {'`', "ّ"},   // Shadda
            {'\\', "|"}   // Pipe
        };

        public NativeTextEdit(MainWindow? parent = null)
        {
            _parentWindow = parent;

            // السطور 805-806: Context menu
            ContextMenu = null;  // Disable default context menu
            MouseRightButtonUp += ShowContextMenu;

            // السطور 810-813: Caret timer - blink every 500ms
            _caretTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(500)
            };
            _caretTimer.Tick += BlinkCaret;
            _caretTimer.Start();

            // Set default style
            Background = Brushes.Transparent;
            BorderThickness = new Thickness(0);
            Foreground = Brushes.White;
        }

        // ═══════════════════════════════════════════════════════════════
        // show_context_menu - السطور 818-877
        // ═══════════════════════════════════════════════════════════════
        private void ShowContextMenu(object sender, MouseButtonEventArgs e)
        {
            // السطور 819-821
            _contextMenu?.Close();
            _contextMenu = null;

            // السطر 823-824
            var menu = new CustomContextMenu();
            _contextMenu = menu;

            // السطور 827-843: Add actions with custom widget
            menu.AddCustomAction("تراجع", "Undo", "Ctrl+Z", () => Undo());
            menu.AddCustomAction("إعادة", "Redo", "Ctrl+Y", () => Redo());

            menu.AddSeparator();

            menu.AddCustomAction("قص", "Cut", "Ctrl+X", () => Cut());
            menu.AddCustomAction("نسخ", "Copy", "Ctrl+C", () => Copy());
            menu.AddCustomAction("لصق", "Paste", "Ctrl+V", () => CustomPaste());

            menu.AddSeparator();

            menu.AddCustomAction("تحديد الكل", "Select All", "Ctrl+A", () => SelectAll());

            // السطور 846-876: Smart positioning - avoid screen edges
            var pos = e.GetPosition(this);
            var globalPos = PointToScreen(pos);

            var screen = SystemParameters.WorkArea;
            menu.Measure(new Size(double.PositiveInfinity, double.PositiveInfinity));
            double menuWidth = menu.DesiredSize.Width;
            double menuHeight = menu.DesiredSize.Height;

            double adjustedX = globalPos.X;
            double adjustedY = globalPos.Y;

            // Check screen edges
            if (adjustedX + menuWidth > screen.Right)
                adjustedX = screen.Right - menuWidth - 10;

            if (adjustedY + menuHeight > screen.Bottom)
                adjustedY = globalPos.Y - menuHeight;

            if (adjustedY < screen.Top)
                adjustedY = screen.Top + 10;

            if (adjustedX < screen.Left)
                adjustedX = screen.Left + 10;

            menu.ShowAt(adjustedX, adjustedY);
            e.Handled = true;
        }

        // ═══════════════════════════════════════════════════════════════
        // blink_caret - السطور 879-881
        // ═══════════════════════════════════════════════════════════════
        private void BlinkCaret(object? sender, EventArgs e)
        {
            _caretVisible = !_caretVisible;
            // Note: WPF handles caret blinking internally, but we keep this for custom painting if needed
        }

        // ═══════════════════════════════════════════════════════════════
        // set_arabic_mode - السطور 891-893
        // ═══════════════════════════════════════════════════════════════
        public void SetArabicMode(bool enabled)
        {
            IsArabicMode = enabled;
        }

        // ═══════════════════════════════════════════════════════════════
        // custom_paste - السطور 895-922
        // لصق مخصص - يفضل Windows clipboard دائماً
        // ═══════════════════════════════════════════════════════════════
        private void CustomPaste()
        {
            try
            {
                // السطور 900-912
                string? winClip = null;
                if (Clipboard.ContainsText())
                {
                    winClip = Clipboard.GetText();
                }

                if (!string.IsNullOrEmpty(winClip))
                {
                    // السطور 903-913: If content differs from last sent message, use it
                    if (_parentWindow != null)
                    {
                        // Note: Would need access to _lastSentMessage from MainWindow
                        InsertText(winClip);
                        Console.WriteLine($"[PASTE] Windows clipboard: {winClip.Substring(0, Math.Min(30, winClip.Length))}...");
                        return;
                    }
                    else
                    {
                        InsertText(winClip);
                        Console.WriteLine($"[PASTE] Windows (no parent): {winClip.Substring(0, Math.Min(30, winClip.Length))}...");
                        return;
                    }
                }

                // السطور 916-918: Fallback to using standard paste
                Paste();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[PASTE] Error: {ex.Message}");
                Paste();
            }
        }

        private void InsertText(string text)
        {
            CaretPosition.InsertTextInRun(text);
        }

        // ═══════════════════════════════════════════════════════════════
        // get_arabic_char - السطور 924-1018
        // Map English character to Arabic with correct keyboard layout
        // ═══════════════════════════════════════════════════════════════
        public string? GetArabicChar(char ch, bool shiftPressed)
        {
            // السطر 1003: Convert to lowercase for lookup
            char charLower = char.ToLower(ch);

            // السطور 1005-1011: If shift is pressed, check shift map first
            if (shiftPressed)
            {
                if (ArabicShiftMap.TryGetValue(charLower, out string? shiftResult))
                    return shiftResult;

                // Fallback to normal map
                if (ArabicMap.TryGetValue(charLower, out string? normalResult))
                    return normalResult;
            }
            else
            {
                // السطور 1012-1015: No shift, use normal map
                if (ArabicMap.TryGetValue(charLower, out string? result))
                    return result;
            }

            // السطور 1017-1018: Return null for unmapped keys
            return null;
        }

        // ═══════════════════════════════════════════════════════════════
        // keyPressEvent - السطور 1020-1055
        // Note: In WPF, we use PreviewTextInput and PreviewKeyDown
        // ═══════════════════════════════════════════════════════════════
        protected override void OnPreviewKeyDown(KeyEventArgs e)
        {
            // السطور 1022-1029: Handle Enter key for sending
            if (e.Key == Key.Return || e.Key == Key.Enter)
            {
                if ((Keyboard.Modifiers & ModifierKeys.Shift) != 0)
                {
                    // Shift+Enter = new line
                    base.OnPreviewKeyDown(e);
                }
                else
                {
                    // Enter = send message
                    _parentWindow?.SendText();
                    e.Handled = true;
                }
                return;
            }

            base.OnPreviewKeyDown(e);
        }

        protected override void OnPreviewTextInput(TextCompositionEventArgs e)
        {
            // السطور 1031-1055
            string text = e.Text;

            // السطور 1036-1038: Let Qt handle special keys
            if (string.IsNullOrEmpty(text) || text.Length != 1)
            {
                base.OnPreviewTextInput(e);
                return;
            }

            // السطور 1040-1044: Check if this is a printable ASCII character
            char ch = text[0];
            if (ch < 32 || ch > 126)
            {
                base.OnPreviewTextInput(e);
                return;
            }

            // السطور 1046-1052: If in Arabic mode, convert to Arabic
            if (IsArabicMode)
            {
                bool shiftPressed = (Keyboard.Modifiers & ModifierKeys.Shift) != 0;
                string? arabicChar = GetArabicChar(ch, shiftPressed);
                if (arabicChar != null)
                {
                    InsertText(arabicChar);
                    e.Handled = true;
                    return;
                }
            }

            // السطر 1055: Default behavior
            base.OnPreviewTextInput(e);
        }
    }
}
