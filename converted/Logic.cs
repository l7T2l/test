// ═══════════════════════════════════════════════════════════════════════════════
// Logic.cs - معالج النص العربي
// المقابل لـ: logic.py (194 سطر)
// تحويل سطر بسطر - كل قيمة مطابقة للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Text;
using System.Text.RegularExpressions;

namespace SmartKeyboard
{
    /// <summary>
    /// class ArabicProcessor: - السطر 1
    /// معالج النص العربي لتحويل الحروف لأشكالها الصحيحة
    /// </summary>
    public class ArabicProcessor
    {
        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - السطور 3-27
        // ═══════════════════════════════════════════════════════════════

        // السطر 3: self.left_connectors
        private readonly string _leftConnectors = "ٹہےگڤچپـئظشسيبلتنمكطضصثقفغعهخحج";

        // السطر 4: self.right_connectors
        private readonly string _rightConnectors = "ٹہےڈڑگڤژچپـئؤرلالآىآةوزظشسيبللأاأتنمكطضصثقفغعهخحجدذلإإۇۆۈ";

        // السطر 5: self.harakat
        private readonly string _harakat = "ًٌٍَُِّْ";

        // السطر 7: self.symbols (Note: space is NOT included here)
        private readonly string _symbols = "ـ.،؟@#$%^&*-+|\\/=~,:";

        // السطر 8: self.brackets
        private readonly string _brackets = "(){}[]";

        // السطور 10-16: self.arabic_chars
        private readonly string _arabicChars =
            "آ" + "أ" + "إ" + "ا" + "ب" + "ت" + "ث" + "ج" + "ح" + "خ" +
            "د" + "ذ" + "ر" + "ز" + "س" + "ش" + "ص" + "ض" + "ط" + "ظ" +
            "ع" + "غ" + "ف" + "ق" + "ك" + "ل" + "م" + "ن" + "ه" + "و" +
            "ي" + "ة" + "ؤ" + "ئ" + "ى" + "پ" + "چ" + "ژ" + "ڤ" + "گ" +
            "ٹ" + "ہ" + "ے" + "ڈ" + "ڑ" + "ۇ" + "ۆ" + "ۈ";

        // السطور 18-24: self.unicode_map
        private readonly string _unicodeMap =
            "ﺁ ﺁ ﺂ ﺂ " + "ﺃ ﺃ ﺄ ﺄ " + "ﺇ ﺇ ﺈ ﺈ " + "ﺍ ﺍ ﺎ ﺎ " + "ﺏ ﺑ ﺒ ﺐ " + "ﺕ ﺗ ﺘ ﺖ " + "ﺙ ﺛ ﺜ ﺚ " + "ﺝ ﺟ ﺠ ﺞ " + "ﺡ ﺣ ﺤ ﺢ " + "ﺥ ﺧ ﺨ ﺦ " +
            "ﺩ ﺩ ﺪ ﺪ " + "ﺫ ﺫ ﺬ ﺬ " + "ﺭ ﺭ ﺮ ﺮ " + "ﺯ ﺯ ﺰ ﺰ " + "ﺱ ﺳ ﺴ ﺲ " + "ﺵ ﺷ ﺸ ﺶ " + "ﺹ ﺻ ﺼ ﺺ " + "ﺽ ﺿ ﻀ ﺾ " + "ﻁ ﻃ ﻄ ﻂ " + "ﻅ ﻇ ﻈ ﻆ " +
            "ﻉ ﻋ ﻌ ﻊ " + "ﻍ ﻏ ﻐ ﻎ " + "ﻑ ﻓ ﻔ ﻒ " + "ﻕ ﻗ ﻘ ﻖ " + "ﻙ ﻛ ﻜ ﻚ " + "ﻝ ﻟ ﻠ ﻞ " + "ﻡ ﻣ ﻤ ﻢ " + "ﻥ ﻧ ﻨ ﻦ " + "ﻩ ﻫ ﻬ ﻪ " + "ﻭ ﻭ ﻮ ﻮ " +
            "ﻱ ﻳ ﻴ ﻲ " + "ﺓ ﺓ ﺔ ﺔ " + "ﺅ ﺅ ﺆ ﺆ " + "ﺉ ﺋ ﺌ ﺊ " + "ﻯ ﻯ ﻰ ﻰ " + "ﭖ ﭘ ﭙ ﭗ " + "ﭺ ﭼ ﭽ ﭻ " + "ﮊ ﮊ ﮋ ﮋ " + "ﭪ ﭬ ﭭ ﭫ " + "ﮒ ﮔ ﮕ ﮓ " +
            "ﭦ ﭨ ﭩ ﭧ " + "ﮦ ﮨ ﮩ ﮧ " + "ﮮ ﮰ ﮱ ﮯ " + "ﮈ ﮈ ﮉ ﮉ " + "ﮌ ﮌ ﮍ ﮍ " + "ﯗ ﯗ ﯘ ﯘ " + "ﯙ ﯙ ﯚ ﯚ " + "ﯛ ﯛ ﯜ ﯜ " +
            "ﻵ ﻵ ﻶ ﻶ " + "ﻷ ﻷ ﻸ ﻸ " + "ﻹ ﻹ ﻺ ﻺ " + "ﻻ ﻻ ﻼ ﻼ ";

        // السطر 27: self.la_index = 8 * 48
        private readonly int _laIndex = 8 * 48;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - السطر 2: def __init__(self)
        // ═══════════════════════════════════════════════════════════════
        public ArabicProcessor()
        {
            // جميع المتغيرات تم تهيئتها أعلاه
        }

        // ═══════════════════════════════════════════════════════════════
        // fix_bidi_numbers - السطور 29-56
        // Fix BiDi (bidirectional) text issues with numbers in Arabic.
        // REVERSES number sequences so when the game reverses them again, they appear correct.
        // Example: "الساعة 3:25" → "الساعة 25:3" → game shows "الساعة 3:25" ✅
        // ═══════════════════════════════════════════════════════════════
        public string FixBidiNumbers(string text)
        {
            // السطور 35-36
            if (string.IsNullOrEmpty(text))
                return text;

            // السطر 42: Pattern to find number sequences with symbols like :, -, ., /
            // This captures: 3:25, 1-2-3, 192.168.1.1, 123/456, phone numbers, etc.
            string numberPattern = @"(\d+(?:[:\-./,]\d+)+)";

            // السطور 44-51: reverse_number_sequence function
            string ReverseNumberSequence(Match match)
            {
                string seq = match.Value;
                // Split by separators, keeping the separators
                string[] parts = Regex.Split(seq, @"([:\-./,])");
                // Reverse the parts
                Array.Reverse(parts);
                return string.Join("", parts);
            }

            // السطر 54: Apply reversal to number sequences
            string result = Regex.Replace(text, numberPattern, new MatchEvaluator(ReverseNumberSequence));

            return result;
        }

        // ═══════════════════════════════════════════════════════════════
        // process_text - السطور 58-193
        // معالجة النص العربي وتحويله للأشكال الصحيحة
        // ═══════════════════════════════════════════════════════════════
        public string ProcessText(string text)
        {
            // السطور 59-60
            if (string.IsNullOrEmpty(text))
                return "";

            try
            {
                // السطور 63-64
                string[] lines = text.Split('\n');
                var processedLines = new System.Collections.Generic.List<string>();

                // السطر 66: for line in lines
                foreach (string rawLine in lines)
                {
                    // السطر 67: line = line.replace("\r", "")
                    string line = rawLine.Replace("\r", "");

                    // السطور 70-75: Check if line has ANY Arabic characters
                    bool hasArabic = false;
                    foreach (char c in line)
                    {
                        if (_arabicChars.Contains(c) || _harakat.Contains(c) || c == 'ء')
                        {
                            hasArabic = true;
                            break;
                        }
                    }

                    // If pure English (no Arabic), return unchanged
                    if (!hasArabic)
                    {
                        processedLines.Add(line);
                        continue;
                    }

                    // السطور 77-79
                    char[] chars = line.ToCharArray();
                    int length = chars.Length;
                    string output = "";

                    // السطور 81-186
                    int g = 0;
                    while (g < length)
                    {
                        // السطور 83-85: Find previous non-harakat character
                        int b = 1;
                        while ((g - b) >= 0 && _harakat.Contains(chars[g - b]))
                            b++;

                        // السطور 87-89: Find next non-harakat character
                        int a = 1;
                        while ((g + a) < length && _harakat.Contains(chars[g + a]))
                            a++;

                        // السطور 91-92
                        char? prevChar = (g - b) >= 0 ? chars[g - b] : (char?)null;
                        char? nextChar = (g + a) < length ? chars[g + a] : (char?)null;

                        // السطور 94-116: Determine position
                        int pos = 0;

                        if (g == 0)
                        {
                            if (nextChar.HasValue && _rightConnectors.Contains(nextChar.Value))
                                pos = 2;
                            else
                                pos = 0;
                        }
                        else if (g == (length - 1))
                        {
                            if (prevChar.HasValue && _leftConnectors.Contains(prevChar.Value))
                                pos = 6;
                            else
                                pos = 0;
                        }
                        else
                        {
                            if (prevChar.HasValue && !_leftConnectors.Contains(prevChar.Value))
                            {
                                if (nextChar.HasValue && !_rightConnectors.Contains(nextChar.Value))
                                    pos = 0;
                                else
                                    pos = 2;
                            }
                            else if (prevChar.HasValue && _leftConnectors.Contains(prevChar.Value))
                            {
                                if (nextChar.HasValue && _rightConnectors.Contains(nextChar.Value))
                                    pos = 4;
                                else
                                    pos = 6;
                            }
                        }

                        // السطر 118
                        char currentChar = chars[g];

                        // السطور 120-121: ء (hamza)
                        if (currentChar == 'ء')
                        {
                            output = "ﺀ" + output;
                        }
                        // السطور 123-128: brackets
                        else if (_brackets.Contains(currentChar))
                        {
                            int idx = _brackets.IndexOf(currentChar);
                            if (idx % 2 == 0)
                                output = _brackets[idx + 1] + output;
                            else
                                output = _brackets[idx - 1] + output;
                        }
                        // السطور 130-149: arabic_chars
                        else if (_arabicChars.Contains(currentChar))
                        {
                            // السطور 131-145: Special handling for "ل" (lam)
                            if (currentChar == 'ل')
                            {
                                int arPos = -1;
                                if ((g + 1) < length)
                                {
                                    if (_arabicChars.Contains(chars[g + 1]))
                                        arPos = _arabicChars.IndexOf(chars[g + 1]);
                                }

                                // السطور 137-145: Lam-Alef combinations
                                if (arPos >= 0 && arPos < 4)
                                {
                                    int idx = (arPos * 8) + pos + _laIndex;
                                    char mappedChar = _unicodeMap[idx];
                                    output = mappedChar + output;
                                    g++; // Skip next char
                                }
                                else
                                {
                                    int idx = (_arabicChars.IndexOf(currentChar) * 8) + pos;
                                    char mappedChar = _unicodeMap[idx];
                                    output = mappedChar + output;
                                }
                            }
                            else
                            {
                                // السطور 147-149: Normal arabic char
                                int idx = (_arabicChars.IndexOf(currentChar) * 8) + pos;
                                char mappedChar = _unicodeMap[idx];
                                output = mappedChar + output;
                            }
                        }
                        // السطور 151-152: symbols
                        else if (_symbols.Contains(currentChar))
                        {
                            output = currentChar + output;
                        }
                        // السطور 154-155: harakat
                        else if (_harakat.Contains(currentChar))
                        {
                            output = currentChar + output;
                        }
                        // السطور 157-184: English buffer
                        else
                        {
                            string engBuffer = currentChar.ToString();
                            int h = g + 1;
                            while (h < length)
                            {
                                char c = chars[h];
                                // السطر 163: Stop at Arabic-related OR symbols
                                bool isStopChar = _arabicChars.Contains(c) ||
                                                  _harakat.Contains(c) ||
                                                  "ء،؟".Contains(c) ||
                                                  _brackets.Contains(c) ||
                                                  _symbols.Contains(c);
                                if (!isStopChar)
                                {
                                    engBuffer += c;
                                    h++;
                                }
                                else
                                {
                                    break;
                                }
                            }

                            // السطور 171-182: Handle spaces properly for RTL
                            string engStripped = engBuffer.Trim(' ');

                            if (!string.IsNullOrEmpty(engStripped))
                            {
                                // Has actual English content - handle leading/trailing spaces
                                string leadingSpaces = engBuffer.Substring(0, engBuffer.Length - engBuffer.TrimStart(' ').Length);
                                string trailingSpaces = engBuffer.Substring(engBuffer.TrimEnd(' ').Length);
                                output = trailingSpaces + engStripped + leadingSpaces + output;
                            }
                            else
                            {
                                // Only spaces, no English - just add spaces once
                                output = engBuffer + output;
                            }

                            g = h - 1;
                        }

                        g++;
                    }

                    // السطر 188
                    processedLines.Add(output);
                }

                // السطر 190
                return string.Join("\n", processedLines);
            }
            catch (Exception e)
            {
                // السطور 192-193
                return $"Error: {e.Message}";
            }
        }
    }
}
