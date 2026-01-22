// ═══════════════════════════════════════════════════════════════════════════════
// KeyboardMapper.cs - خريطة لوحة المفاتيح العربية
// المقابل لـ: main.py السطور 924-1018 (get_arabic_char في NativeTextEdit)
// تحويل سطر بسطر - كل حرف مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System.Collections.Generic;

namespace SmartKeyboard
{
    /// <summary>
    /// خريطة لوحة المفاتيح العربية
    /// Map English character to Arabic with correct keyboard layout
    /// </summary>
    public static class KeyboardMapper
    {
        // ═══════════════════════════════════════════════════════════════
        // السطور 928-949: arabic_map - Standard Arabic keyboard layout (no shift)
        // ═══════════════════════════════════════════════════════════════
        private static readonly Dictionary<char, string> ArabicMap = new Dictionary<char, string>
        {
            // السطور 929-932: Numbers row (Arabic-Indic numerals when typing in Arabic)
            {'1', "1"}, {'2', "2"}, {'3', "3"}, {'4', "4"}, {'5', "5"},
            {'6', "6"}, {'7', "7"}, {'8', "8"}, {'9', "9"}, {'0', "0"},
            {'-', "-"}, {'=', "="},

            // السطور 934-937: Top row (QWERTY -> Arabic)
            {'q', "ض"}, {'w', "ص"}, {'e', "ث"}, {'r', "ق"}, {'t', "ف"},
            {'y', "غ"}, {'u', "ع"}, {'i', "ه"}, {'o', "خ"}, {'p', "ح"},
            {'[', "ج"}, {']', "د"},

            // السطور 939-941: Middle row (ASDF -> Arabic)
            {'a', "ش"}, {'s', "س"}, {'d', "ي"}, {'f', "ب"}, {'g', "ل"},
            {'h', "ا"}, {'j', "ت"}, {'k', "ن"}, {'l', "م"}, {';', "ك"}, {'\'', "ط"},

            // السطور 943-945: Bottom row (ZXCV -> Arabic)
            {'z', "ئ"}, {'x', "ء"}, {'c', "ؤ"}, {'v', "ر"}, {'b', "لا"},
            {'n', "ى"}, {'m', "ة"}, {',', "و"}, {'.', "ز"}, {'/', "ظ"},

            // السطر 948: Special keys
            {'`', "ذ"}, {'\\', "\\"}  // Backslash stays as is
        };

        // ═══════════════════════════════════════════════════════════════
        // السطور 952-1000: arabic_shift_map - Shifted Arabic (Shift + key)
        // ═══════════════════════════════════════════════════════════════
        private static readonly Dictionary<char, string> ArabicShiftMap = new Dictionary<char, string>
        {
            // السطور 954-956: Numbers row with shift -> symbols
            {'1', "!"}, {'2', "@"}, {'3', "#"}, {'4', "$"}, {'5', "%"},
            {'6', "^"}, {'7', "&"}, {'8', "*"}, {'9', "("}, {'0', ")"},
            {'-', "_"}, {'=', "+"},

            // السطور 958-970: Top row shifted (Arabic diacritics and symbols)
            {'q', "َ"},   // السطر 959: Fatha
            {'w', "ً"},   // السطر 960: Tanween Fath
            {'e', "ُ"},   // السطر 961: Damma
            {'r', "ٌ"},   // السطر 962: Tanween Damm
            {'t', "لإ"},  // السطر 963: Lam with Hamza below
            {'y', "إ"},   // السطر 964: Hamza on alif below
            {'u', "'"},   // السطر 965: APOSTROPHE (ASCII 39)
            {'i', "÷"},   // السطر 966: Division
            {'o', "×"},   // السطر 967: Multiplication
            {'p', "؛"},   // السطر 968: Arabic semicolon
            {'[', "<"},   // السطر 969
            {']', ">"},   // السطر 970

            // السطور 972-983: Middle row shifted
            {'a', "ِ"},   // السطر 973: Kasra
            {'s', "ٍ"},   // السطر 974: Tanween Kasr
            {'d', "]"},   // السطر 975: Right bracket
            {'f', "["},   // السطر 976: Left bracket
            {'g', "لأ"},  // السطر 977: Lam with Hamza above
            {'h', "أ"},   // السطر 978: Hamza on alif
            {'j', "ـ"},   // السطر 979: Tatweel (Arabic Tatweel U+0640)
            {'k', "،"},   // السطر 980: Arabic comma
            {'l', "/"},   // السطر 981: Forward slash
            {';', ":"},   // السطر 982: Colon
            {'\'', "\""}, // السطر 983: Double quote

            // السطور 985-999: Bottom row shifted
            {'z', "~"},   // السطر 986: Tilde
            {'x', "ْ"},   // السطر 987: Sukun
            {'c', "}"},   // السطر 988: Right brace
            {'v', "{"},   // السطر 989: Left brace
            {'b', "لآ"},  // السطر 990: Lam with Mad
            {'n', "آ"},   // السطر 991: Alif with Mad
            {'m', "'"},   // السطر 992: APOSTROPHE (ASCII 39)
            {',', "<"},   // السطر 993: Less than
            {'.', ">"},   // السطر 994: Greater than
            {'/', "؟"},   // السطر 995: Arabic question mark

            // السطور 997-999: Special shifted
            {'`', "ّ"},   // السطر 998: Shadda
            {'\\', "|"}   // السطر 999: Pipe
        };

        // ═══════════════════════════════════════════════════════════════
        // get_arabic_char - السطور 924-1018
        // Map English character to Arabic with correct keyboard layout
        // ═══════════════════════════════════════════════════════════════
        public static string? GetArabicChar(char c, bool shiftPressed)
        {
            // السطر 1003: Convert to lowercase for lookup
            char charLower = char.ToLower(c);

            // السطور 1005-1011: If shift is pressed, check shift map first
            if (shiftPressed)
            {
                if (ArabicShiftMap.TryGetValue(charLower, out string? shiftResult))
                {
                    return shiftResult;
                }
                // السطور 1010-1011: If not in shift map, fallback to normal map
                else if (ArabicMap.TryGetValue(charLower, out string? normalResult))
                {
                    return normalResult;
                }
            }
            else
            {
                // السطور 1013-1015: No shift, use normal map
                if (ArabicMap.TryGetValue(charLower, out string? result))
                {
                    return result;
                }
            }

            // السطور 1017-1018: Return None for unmapped keys (will be handled as English)
            return null;
        }

        /// <summary>
        /// التحقق إذا كان الحرف قابل للتحويل للعربية
        /// </summary>
        public static bool CanMapToArabic(char c)
        {
            char lower = char.ToLower(c);
            return ArabicMap.ContainsKey(lower) || ArabicShiftMap.ContainsKey(lower);
        }
    }
}
